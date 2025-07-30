import abc
import asyncio
import collections.abc
import concurrent.futures
import enum
import fnmatch
import inspect
import re
import threading
import warnings
from typing import Any, Callable, Dict, FrozenSet, Mapping, Optional, \
                   Protocol, Sequence, Set, TypeVar, Union, runtime_checkable

import aiohttp.web
import attrs
from typing_extensions import Self

from kmock import boxes, enums, parsing, rendering, resources

T = TypeVar('T')
V = TypeVar('V')


@runtime_checkable
class SupportsBool(Protocol):
    def __bool__(self) -> bool:
        ...


CriterionFn = Union[
    Callable[[], "Criterion"],
    Callable[[rendering.Request], "Criterion"],
]

# Anything that can be used as a single anonymous criterion in view filtering:
#   kmock[criterion1][criterion2, criterion3][{criterion4, criterion5}]
# It is then analyzed, parsed, and converted to specialized named criteria.
Criterion = Union[
    None,
    str,  # mixed methods, actions, paths, namespaces
    int,
    bool,
    bytes,
    SupportsBool,
    re.Pattern,
    enums.action,
    enums.method,
    resources.resource,
    resources.Selectable,
    Set["Criterion"],
    FrozenSet["Criterion"],
    Mapping[str, "Criterion"],

    # Events are true if they are set.
    asyncio.Event,
    threading.Event,

    # Futures are true if they are set AND the result is true.
    asyncio.Future,
    concurrent.futures.Future,

    # Arbitrary callables can be used too. NB: strict bool-supporting classes! To avoid support for
    # e.g. generators and other unexpected objects as filters (which are "true" by mere existence).
    Callable[[], bool],
    Callable[[], SupportsBool],
    Callable[[rendering.Request], bool],
    Callable[[rendering.Request], SupportsBool],
]
CriterionBox = Union[
    boxes.data,
    boxes.text[Union[re.Pattern[str], re.Pattern[bytes]]],
    boxes.body[Union[re.Pattern[str], re.Pattern[bytes]]],
    boxes.params[re.Pattern[str]],
    boxes.headers[re.Pattern[str]],
    boxes.cookies[re.Pattern[str]],
]

TRUE_STRINGS = re.compile(r'^true|yes|on|t|y|1$', re.I)
FALSE_STRINGS = re.compile(r'^false|no|off|f|n|0$', re.I)


# TODO: RENAME? -> Filter — for brevity. But first, rename dsl.Filter -> dsl.???
@attrs.frozen
class Criteria(Callable[[rendering.Request], bool]):
    """A standalone container for specialized named criteria."""

    @abc.abstractmethod
    def __call__(self, request: rendering.Request) -> bool:
        raise NotImplementedError

    def _check(self, pat: Criterion, val: Any, *, glob: bool = False) -> bool:
        # No criteria means matching everything.
        if pat is None:
            # TODO: this is a DX BUG! checking a data dict {'a': 'b'} vs pattern {'a': None}
            #       should NOT lead to True. 'a' ust be either null or absent. 'b' != None!
            return True

        # Special types & wrappers check for themselves.
        elif isinstance(pat, resources.resource):
            return val is not None and (isinstance(val, resources.Selectable) and pat.check(val))

        # Enums from either side match both names & values case-insensitively.
        elif isinstance(pat, enum.Enum):
            if pat == val:  # quick-check if we are lucky
                return True
            if self._check(re.compile(re.escape(pat.name), re.I), val):
                return True
            if isinstance(pat.value, int):
                return self._check(pat.value, val, glob=glob)
            if isinstance(pat.value, (str, bytes)):
                return self._check(re.compile(re.escape(pat.value), re.I), val, glob=glob)
            return False
        elif isinstance(pat, int) and isinstance(val, enum.Enum):
            return self._check(pat, val.value)
        elif isinstance(pat, (str, bytes)) and isinstance(val, enum.Enum):
            if pat == val:  # quick-check if we are lucky
                return True
            if self._check(re.compile(re.escape(pat), re.I), val.name):
                return True
            if isinstance(val.value, (int, str, bytes)):
                return self._check(re.compile(re.escape(pat), re.I), val.value, glob=glob)
            return False
        elif isinstance(pat, re.Pattern) and isinstance(val, enum.Enum):
            if self._check(pat, val.name):
                return True
            if isinstance(val.value, (int, str, bytes)):
                return self._check(pat, val.value, glob=glob)
            return False

        # Regexps accept any form of scalars.
        elif isinstance(pat, re.Pattern) and isinstance(val, int):
            return self._check(pat, str(val), glob=glob)
        elif isinstance(pat, re.Pattern) and isinstance(val, (str, bytes)):
            try:
                return bool(pat.fullmatch(val))
            except TypeError:
                # TypeError: can't use a string pattern on a bytes-like object
                if isinstance(val, bytes):
                    return self._check(pat, val.decode(), glob=glob)
                # TypeError: can't use a bytes pattern on a string-like object
                if isinstance(val, str):
                    return self._check(pat, val.encode(), glob=glob)
                raise
        elif isinstance(pat, re.Pattern):
            return False

        # JSON-like syntax (dicts, lists) mean matching the value, but elements can be any patterns.
        # This also covers our shortcuts: headers(), cookies(), params(), etc.
        # E.g.: {'query': re.compile('true', re.I)}
        elif isinstance(pat, collections.abc.Mapping) and isinstance(val, collections.abc.Mapping):
            return all(key in val and self._check(pat[key], val[key], glob=glob) for key in pat)
        elif isinstance(pat, collections.abc.Mapping):
            return False  # we wanted a dict, got something else

        # Strings & bytes are interchangeable with implicit encoding, including regexp patterns.
        elif isinstance(pat, (str, bytes)) and glob:
            return val is not None and fnmatch.fnmatchcase(val, pat)
        elif isinstance(pat, str) and isinstance(val, bytes):
            return pat == val.decode()
        elif isinstance(pat, str) and isinstance(val, (str, int)):
            return pat == str(val)
        elif isinstance(pat, bytes) and isinstance(val, str):
            return pat == val.encode()
        elif isinstance(pat, bytes) and isinstance(val, int):
            return pat == str(val).encode()
        elif isinstance(pat, bytes) and isinstance(val, bytes):
            return pat == val

        # Booleans match some predefined strings/bytes (JSON-style).
        # NB: pattern=False does NOT match value=None! If False is expected, it MUST be False/0.
        elif isinstance(pat, bool) and val is None:
            return False
        elif isinstance(pat, bool) and isinstance(val, (str, bytes)):
            return self._check(TRUE_STRINGS if pat else FALSE_STRINGS, val, glob=glob)
        elif isinstance(pat, bool) and isinstance(val, (bool, int, SupportsBool)):
            return bool(pat) == bool(val)
        elif isinstance(pat, bool):
            return False

        # Integers are shortcuts for same-value strings; e.g.: {'page': 5} == {'page': '5'}.
        elif isinstance(pat, int) and isinstance(val, (str, bytes)):
            return self._check(str(pat), val, glob=glob)

        # Avoid materializing ephemeral collections. E.g. {'page': range(5, 9999)}.
        elif isinstance(pat, range) and isinstance(val, int):
            return val in pat
        elif isinstance(pat, range) and isinstance(val, str):
            try:
                return int(val) in pat
            except ValueError:
                return False
        elif isinstance(pat, range) and isinstance(val, bytes):
            try:
                return int(val.decode()) in pat
            except ValueError:
                return False

        # Unordered collections mean any value in it. E.g. {'watch': {'true', 'yes', '1'}}.
        elif isinstance(pat, (set, frozenset)):
            if isinstance(val, collections.abc.Hashable) and val in pat:  # quick-check
                return True
            return any(self._check(sub_pat, val, glob=glob) for sub_pat in pat)

        # Compare everything else by equality — the "best effort" approach without any smart logic.
        else:
            return pat == val

    @staticmethod
    def guess(arg: Union["Criteria", Criterion, CriterionBox], /) -> Optional["Criteria"]:
        if arg is None:
            return None
        elif isinstance(arg, aiohttp.web.StreamResponse):  # a mapping for some reason
            raise ValueError(f"Unrecognized criterion type: {type(arg)}")

        # Preparsed or explicitly defined criteria go as is. Mostly for non-boxed shortcuts below.
        elif isinstance(arg, Criteria):
            return arg

        # Unpack purpose-hinting enums & boxes into purpose-specific classes & fields.
        elif isinstance(arg, enums.method):
            return HTTPCriteria(method=arg)
        elif isinstance(arg, enums.action):
            return K8sCriteria(action=arg)
        elif isinstance(arg, boxes.body):
            return HTTPCriteria(body=arg.body)
        elif isinstance(arg, boxes.text):
            return HTTPCriteria(text=arg.text)
        elif isinstance(arg, boxes.data):
            return HTTPCriteria(data=arg.data)
        elif isinstance(arg, boxes.path):
            return HTTPCriteria(path=arg.path)
        elif isinstance(arg, boxes.params):
            return HTTPCriteria(params=dict(arg))
        elif isinstance(arg, boxes.headers):
            return HTTPCriteria(headers=dict(arg))
        elif isinstance(arg, boxes.cookies):
            return HTTPCriteria(cookies=dict(arg))
        elif isinstance(arg, resources.resource):
            return K8sCriteria(resource=arg)
        elif isinstance(arg, resources.Selectable):
            return K8sCriteria(resource=resources.resource(arg))

        # Generic Python types are either parsed & recognized, or go to multi-field criteria.
        elif isinstance(arg, re.Pattern):  # todo: also to StrCriteria?
            return HTTPCriteria(path=arg)
        elif isinstance(arg, bytes):
            return HTTPCriteria(body=arg)
        elif isinstance(arg, str):
            # NB: http methods over k8s actions: mostly for the ambiguous "delete" verb.
            if not arg:
                return None
            elif (maybe_http := parsing.ParsedHTTP.parse(arg)) is not None:
                return HTTPCriteria(method=maybe_http.method, path=maybe_http.path, params=maybe_http.params)
            elif (maybe_k8s := parsing.ParsedK8s.parse(arg)) is not None and maybe_k8s.action:
                return K8sCriteria(action=maybe_k8s.action, resource=maybe_k8s.resource)
            else:
                return StrCriteria(arg)
        elif isinstance(arg, collections.abc.Mapping):
            return DictCriteria(arg) if arg else None
        elif isinstance(arg, collections.abc.Callable):
            return FnCriteria(arg)
        elif isinstance(arg, (asyncio.Event, threading.Event)):
            return EventCriteria(arg)
        elif isinstance(arg, (asyncio.Future, concurrent.futures.Future)):
            return FutureCriteria(arg)
        elif isinstance(arg, (bool, SupportsBool)):
            return BoolCriteria(arg)
        else:
            raise ValueError(f"Unrecognized criterion type: {type(arg)}")


@attrs.frozen(kw_only=True, repr=False)
class OptiCriteria(Criteria):
    """
    A base for multi-field criteria with squashing/optimizing and simpler repr.
    """

    def __repr__(self) -> str:
        # For brevity, only non-default field values in repr (why is it not a feature of attrs yet?)
        cls = type(self)
        vals = {
            field.alias or field.name: getattr(self, field.name)
            for field in attrs.fields(type(self))
            if field.repr and field.init
            if not field.name.startswith('_')
            # if callable(field.default) or getattr(self, field.name) != field.default
            if getattr(self, field.name) != field.default and getattr(self, field.name) is not None and getattr(self, field.name) != {}
        }
        text = ', '.join(f"{key!s}={val!r}" for key, val in vals.items())
        return f"{cls.__name__}({text})"

    def __add__(self, other: Self) -> Self:
        # Only criteria with STRICTLY the same fields can be optimized, no descendant classes.
        if type(other) is not type(self):
            return NotImplemented
        kwargs: Dict[str, Any] = {}
        for field in attrs.fields(type(self)):
            a = getattr(self, field.name)
            b = getattr(other, field.name)
            try:
                kwargs[field.name] = self._combine((field.name,), a, b)
            except NotImplementedError:
                return NotImplemented
        return type(self)(**kwargs)

    def _combine(self, path: Sequence[str], a: Any, b: Any) -> Any:
        if isinstance(a, collections.abc.Mapping) and isinstance(b, collections.abc.Mapping):
            return self._combine_dicts(path, a, b)
        elif a is not None and b is not None and a != b:
            keys_str = ''.join(f"[{key!r}]" for key in path[1:])
            path_str = f"{path[0]}{keys_str}"
            warnings.warn(f"Conflicting values of {path_str}: {a!r} vs. {b!r}", UserWarning)
            raise ValueError(f"Ambiguous values of {path_str}: {a!r} vs. {b!r}")
        else:
            return b if b is not None else a if a is not None else None

    def _combine_dicts(self, path: Sequence[str], a: Mapping[str, T], b: Mapping[str, T]) -> Mapping[str, T]:
        m: Dict[str, Any] = {}
        for key in set(a) | set(b):
            if key not in a:
                m[key] = b[key]
            elif key not in b:
                m[key] = a[key]
            elif a[key] == b[key]:
                m[key] = a[key]  # b would also work
            else:
                m[key] = self._combine(tuple(path) + (key,), a[key], b[key])
        return type(a)(m)


@attrs.frozen(kw_only=True, repr=False)
class HTTPCriteria(OptiCriteria):
    """
    The generic HTTP-level criteria of the request (not involving K8s aspects).
    """

    method: Optional[enums.method] = None
    path: Optional[Union[re.Pattern, str]] = None
    text: Optional[Union[re.Pattern, str]] = None
    body: Optional[Union[re.Pattern, bytes]] = None
    data: Optional[Any] = None
    params: Optional[Mapping[str, Union[None, str, re.Pattern]]] = None
    cookies: Optional[Mapping[str, Union[None, str, re.Pattern]]] = None
    headers: Optional[Mapping[str, Union[None, str, re.Pattern]]] = None

    def __call__(self, request: rendering.Request) -> bool:
        return (
            True
            # TODO: consider globs for headers/params. But if so, treat None as "must be absent".
            #       same for .data — None MUST mean it must be either JSON-null, or absent (which is equivalent in k8s)
            #       current interpretation as "any" is highly MISLEADING. Use "*" for "any"?
            and self._check(self.method, request.method)
            and self._check(self.params, request.params)  # TODO: glob=True?
            and self._check(self.headers, request.headers)  # TODO: glob=True?
            and self._check(self.cookies, request.cookies)  # TODO: glob=True?
            and self._check(self.path, request.url.path, glob=True)
            and self._check(self.text, request.text)
            and self._check(self.body, request.body)
            and self._check(self.data, request.data)
        )


@attrs.frozen(kw_only=True, repr=False)
class K8sCriteria(OptiCriteria):
    """
    The K8s-level criteria of the request, if they could be guessed/parsed.

    This is also an example of extending KMock for app-specific handling.
    """

    action: Optional[enums.action] = None
    resource: Optional[resources.resource] = None
    namespace: Optional[Union[re.Pattern, str]] = None
    clusterwide: Optional[bool] = None
    name: Optional[Union[re.Pattern, str]] = None
    subresource: Optional[Union[re.Pattern, str]] = None

    def __call__(self, request: rendering.Request) -> bool:
        return (
            True
            and self._check(self.action, request.action)
            and self._check(self.resource, request.resource)
            and self._check(self.subresource, request.subresource)
            and self._check(self.clusterwide, request.clusterwide)
            and self._check(self.namespace, request.namespace, glob=True)
            and self._check(self.name, request.name, glob=True)
        )


@attrs.frozen
class FnCriteria(Criteria):
    fn: CriterionFn

    def __call__(self, request: rendering.Request) -> bool:
        # A callable can return anything: other callables, awaitables, bools, or None.
        # Treat the result as a positional non-specialised criterion (no way to specialise it).
        # Everything else can be explicitly specialised with kwargs, hence the separate fields.
        result = self.fn(request) if inspect.signature(self.fn).parameters else self.fn()
        criteria = Criteria.guess(result)
        return criteria(request)


@attrs.frozen
class BoolCriteria(Criteria):
    value: Union[bool, SupportsBool]

    def __call__(self, request: rendering.Request) -> bool:
        return bool(self.value)


@attrs.frozen
class DictCriteria(Criteria):
    value: Mapping[str, Any]

    def __call__(self, request: rendering.Request) -> bool:
        return bool(
            self._check(self.value, request.headers) or
            self._check(self.value, request.cookies) or
            self._check(self.value, request.params) or
            self._check(self.value, request.data)
        )


@attrs.frozen
class StrCriteria(Criteria):
    value: str

    def __call__(self, request: rendering.Request) -> bool:
        return bool(
            self._check(self.value, request.method) or
            self._check(self.value, request.data) or
            self._check(self.value, request.text)
        )


@attrs.frozen
class EventCriteria(Criteria):
    event: Union[asyncio.Event, threading.Event]

    def __call__(self, request: rendering.Request) -> bool:
        return self.event.is_set()


@attrs.frozen
class FutureCriteria(Criteria):
    future: Union[asyncio.Future, concurrent.futures.Future]

    def __call__(self, request: rendering.Request) -> bool:
        return bool(self.future.done() and self.future.result())


# Some non-boxed shortcuts with values of specific purpose. They are not worth making them
# into separate class(es) in boxes.py, but are still needed for DSL completeness.
# TODO: Remake into classes — e.g. for kmock.objects[kmock.namespace('ns1')]
#       in addition to kmock.objects[kmock.resource('v1/pods')]
#  OR: keep those indexes positional?
def clusterwide(arg: bool = True) -> Criteria:
    return K8sCriteria(clusterwide=bool(arg))


def namespace(arg: Union[re.Pattern, str]) -> Criteria:
    return K8sCriteria(namespace=arg)


def name(arg: Union[re.Pattern, str]) -> Criteria:
    return K8sCriteria(name=arg)


def subresource(arg: Union[re.Pattern, str]) -> Criteria:
    return K8sCriteria(subresource=arg)
