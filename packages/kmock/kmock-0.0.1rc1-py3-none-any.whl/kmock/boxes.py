"""
Temporary containers for nicer DSL.

Once used in one of the roles, the containers are dismissed and their
contained values are used in the relevant structures:

* As criteria: ``kmock[kmock.headers('Authorization: Bearer tkn')]``
* As payload: ``kmock << kmock.headers('Content-Type: application/json')``

Not all boxes can be used in all roles: e.g., params can only be in criteria.
But for uniformity, we still generate the shortcut containers first.
"""
import collections.abc
import re
import urllib.parse
from typing import Any, Dict, Generic, Iterable, List, Mapping, Optional, TypeVar, Union, overload

import attrs
from typing_extensions import Self, override

# An extra type for criteria. Use as [None] for strict containers (despite already defined),
# or as [re.Pattern[str | bytes]] for criteria in addition to strict str/bytes.
P = TypeVar('P')


@attrs.define
class path:
    path: Union[str, re.Pattern[str]] = ''


@attrs.define(init=False)
class body(Generic[P]):
    body: Union[bytes, P] = b''

    @overload
    def __init__(self, arg: Union[None, P], /) -> None:
        ...

    @overload
    def __init__(self, *args: Union[str, bytes]) -> None:
        ...

    def __init__(self, *args: Union[str, bytes, None, P]) -> None:
        super().__init__()
        if not args or all(arg is None for arg in args):
            self.body = b''
        elif len(args) == 1 and isinstance(args[0], re.Pattern):
            self.body = args[0]
        else:
            encoded: List[bytes] = []
            for arg in args:
                if arg is None:
                    pass
                elif isinstance(arg, bytes):
                    encoded.append(arg)
                elif isinstance(arg, str):
                    encoded.append(arg.encode())
                else:
                    raise ValueError("Body can be either strings, bytes, or a single re.Pattern.")
            self.body = b''.join(encoded)


@attrs.define(init=False)
class text(Generic[P]):
    text: Union[str, P] = ''

    @overload
    def __init__(self, arg: Union[None, P], /) -> None:
        ...

    @overload
    def __init__(self, *args: Union[str, bytes]) -> None:
        ...

    def __init__(self, *args: Union[str, bytes, None, P]) -> None:
        super().__init__()
        if not args or all(arg is None for arg in args):
            self.text = ''
        elif len(args) == 1 and isinstance(args[0], re.Pattern):
            self.text = args[0]
        else:
            decoded: List[str] = []
            for arg in args:
                if arg is None:
                    pass
                elif isinstance(arg, str):
                    decoded.append(arg)
                elif isinstance(arg, bytes):
                    decoded.append(arg.decode())
                else:
                    raise ValueError("Text can be either strings, bytes, or a single re.Pattern.")
            self.text = ''.join(decoded)


@attrs.define(init=False)
class data:
    data: Any

    @overload
    def __init__(self, arg: Any, /) -> None:
        ...

    @overload
    def __init__(self, *args: Mapping[Any, Any], **kwargs: Any) -> None:
        ...

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.data = None
        for arg in args:
            if arg is None:
                pass
            elif self.data is None:
                self.data = arg
            elif isinstance(self.data, collections.abc.Mapping):
                # Hopefully, arg is a mapping or a dict-ready sequence. If not, fail.
                self.data = dict(self.data, **dict(arg))
            else:
                raise ValueError(f"Unmergeable combination of multiple arguments: {args!r}")
        if kwargs:
            if self.data is None or isinstance(self.data, collections.abc.Mapping):
                self.data = dict(self.data or {}, **kwargs)
            else:
                raise ValueError("Kwargs can be passed to data only alone or for a mapping.")


class patterndict(Generic[P], collections.abc.Mapping[str, Union[str, None, P]]):
    __slots__ = '_data'
    _data: Dict[str, Union[str, None, P]]

    def __init__(
            self,
            *args: Union[None, str, bytes, Mapping[str, Union[str, None, P]]],
            **kwargs: Union[str, None, P],
    ) -> None:
        super().__init__()
        self._data = {}
        for arg in args:
            if arg is None:
                pass
            elif isinstance(arg, (str, bytes)):
                value = arg.decode() if isinstance(arg, bytes) else arg
                items = self._parse_str(value)
                self._data.update(items)
            elif isinstance(arg, (collections.abc.Mapping, collections.abc.Iterable)):
                try:
                    self._data.update(arg)
                except ValueError:
                    raise ValueError(f"Unsupported argument for {self.__class__.__name__}: {arg!r}")
            else:
                raise ValueError(f"Unsupported argument for {self.__class__.__name__}: {arg!r}")
        self._data.update(kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data!r})"

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterable[str]:
        return iter(self._data)

    def __getitem__(self, key: str) -> Union[str, None, P]:
        return self._data[key]

    def _parse_str(self, s: str, /) -> Mapping[str, Union[str, None, P]]:
        raise ValueError(f"Unsupported argument for {self.__class__.__name__}: {s!r}")

    @classmethod
    def guess(cls, arg: Union[None, str, bytes, Mapping[str, Union[str, None, P]]]) -> Optional[Self]:
        return None if arg is None else cls(arg)


class params(Generic[P], patterndict[P]):
    __slots__ = ()

    @override
    def _parse_str(self, s: str, /) -> Mapping[str, Union[str, None, P]]:
        # Distinguish truly empty keys and no-value keys: None means any value for a present key.
        # E.g.: "?key=&…" becomes {'key': ''), but "?key&…" becomes {'key': None}
        s = s.lstrip('?')
        orphans = {v for v in s.split('&') if '=' not in v}
        values = urllib.parse.parse_qsl(s, keep_blank_values=True)
        return {key: None if not val and key in orphans else val for key, val in values}


class cookies(Generic[P], patterndict[P]):
    __slots__ = ()


class headers(Generic[P], patterndict[P]):
    __slots__ = ()

    @override
    def _parse_str(self, s: str, /) -> Mapping[str, Union[str, None, P]]:
        result: Dict[str, str] = {}
        lines = [line.strip() for line in s.splitlines() if line.strip()]
        for line in lines:
            if ':' not in line:
                raise ValueError(f"Unsupported argument for {self.__class__.__name__}: {line!r}")
            name, s = line.split(':', 1)
            result[name.strip()] = s.strip()
        return result
