import asyncio
import collections.abc
import concurrent.futures
import inspect
import io
import json
import pathlib
import queue
import sys
import threading
import warnings
from typing import Any, AsyncGenerator, AsyncIterable, AsyncIterator, Awaitable, Callable, Dict, Generator, Iterable, \
                   List, Mapping, MutableSequence, MutableSet, Optional, Sequence, Tuple, Type, Union, final

import aiohttp.web
import attrs
import yarl
from typing_extensions import Self

from kmock import aiobus, boxes, enums, parsing, resources

if sys.version_info >= (3, 10):
    from types import EllipsisType, NotImplementedType
else:
    EllipsisType = type(Ellipsis)
    NotImplementedType = type(NotImplemented)


# Multi-type content for responses, with a heuristic to serve each type differently.
# Each item can be the whole response or a step of a streaming response.
Payload = Union[
    None,

    # Raw binary payload get into the response bodies or streams unmodified:
    bytes,
    pathlib.Path,
    io.RawIOBase,
    io.TextIOBase,
    io.BufferedIOBase,

    # Plain types with JSON-like syntax in Python go to requests JSON- or JSON-lines-encoded:
    str,
    int,
    float,
    List[Any],
    Dict[Any, Any],
    Mapping[Any, Any],

    # Ellipsis ("...") marks a live response (if top-level) or a live stream segment (if nested):
    EllipsisType,

    # Round-brackets (collections, generators) become streams; they can be individually depleted:
    Tuple["Payload", ...],
    Iterable["Payload"],
    AsyncIterable["Payload"],

    # Lazily evaluated content is unfolded at request handling time:
    Awaitable["Payload"],  # coros, tasks, futures (awaited before rendering)
    Callable[[], "Payload"],  # lambdas, partials, sync & async callbacks
    Callable[["Request"], "Payload"],  # lambdas, partials, sync & async callbacks

    # Exceptions are re-raised in place (some have special meaning):
    Type[BaseException],
    BaseException,

    # Pre-interpreted or explicitly classified metadata to override the declared one:
    "Response",

    # An internal trick to keep side effects inbetween content sequence, but ignore their results:
    "SinkBox",
]

# Boxes can be fed into ``<<``, but never get into the payload directly (thus a separate type).
PayloadBox = Union[
    boxes.data,
    boxes.text[None],
    boxes.body[None],
    boxes.headers[None],
    boxes.cookies[None],
]

# Sinks are where the requests go to, but any results of it are ignored. Typically used via >>.
Sink = Union[
    None,

    # For files & i/o, the requests are append-saved into those files (not overwritten!):
    #   kmock['get /'] >> pathlib.Path('/tmp/reqs.log') >> (sio:=io.StringIO())
    pathlib.Path,
    io.RawIOBase,
    io.TextIOBase,
    io.BufferedIOBase,

    # Mutable collections get the requests added to them (no dicts yet: unclear value):
    #   kmock['get /'] >> (requests:=[]) >> (deduplicated:=set())
    MutableSequence,
    MutableSet,

    # Synchronization primitives get the request object put/set into them:
    #   kmock['get /'] >> (fut:=asyncio.Future()) >> (queue:=asyncio.Queue())
    concurrent.futures.Future,
    asyncio.Future,
    asyncio.Queue,
    queue.Queue,
    threading.Event,
    threading.Condition,
    asyncio.Event,
    asyncio.Condition,
    aiobus.Bus,

    # Generators (but not simple iterators/iterables) get the requests from their `yield`.
    # The yield is interpreted as if it were an effect, or ignored if not recognized.
    Generator[Union["Effect", Any], Union["Request", None], Union["Effect", None]],
    AsyncGenerator[Union["Effect", Any], Union["Request", None]],

    # Lazily evaluated content is unfolded at request handled time.
    # The result is interpreted as it it were an effect, or ignored if not recognized.
    Awaitable[Union["Effect", Any]],  # coros, tasks, futures (awaited before rendering)
    Callable[[], Union["Effect", Any]],  # lambdas, partials, sync & async callbacks
    Callable[["Request"], Union["Effect", Any]],  # lambdas, partials, sync & async callbacks

    # An internal trick to keep side effects inbetween content sequence, but ignore their results:
    "SinkBox",
]

# The same as unions above, but for runtime quick-checking:
SUPPORTED_SINKS = (
    collections.abc.Awaitable, collections.abc.Callable,
    pathlib.Path, io.RawIOBase, io.BufferedIOBase, io.TextIOBase,
    aiobus.Bus, asyncio.Event, asyncio.Queue, asyncio.Condition, asyncio.Future,
    threading.Event, queue.Queue, threading.Condition, concurrent.futures.Future,
    collections.abc.MutableSet, collections.abc.MutableSequence, collections.abc.MutableMapping,
)
SUPPORTED_PAYLOADS = (
    # aiohttp.web.Response,  # TODO remove?
    BaseException,
    bytes, int, float, bool, str, list, dict,
    pathlib.Path, io.RawIOBase, io.BufferedIOBase, io.TextIOBase,
    collections.abc.Awaitable, collections.abc.Callable,
    collections.abc.Iterable, collections.abc.AsyncIterable, collections.abc.Mapping,
    EllipsisType, NotImplementedType,
)


# You might want to wrap it into a closure. Forget it! That requires interpreting value types and
# signatures internally the same way as it is already done in the response rendering:
# pure awaitables, callable coroutines, sync/async callables with and without arguments, etc.
# The internal lightweight container is the simplest and also the most performant solution.
class SinkBox:
    __slots__ = '_item'
    _item: Sink

    def __init__(self, arg: Sink, /) -> None:
        super().__init__()

        # Quick early check of supported types: at definition in tests, not at execution in servers.
        # This simplifies the development in case of errors or misuse.
        if arg is None:
            self._item = arg
        elif isinstance(arg, SUPPORTED_SINKS):
            self._item = arg
        else:
            raise ValueError(f"Unsupported type of a side effect: {type(arg)}")


@final
@attrs.mutable(kw_only=True)  # mutable to accumulate the payload into one tuple until consumed
class StreamBatch:
    fed: bool = False
    consumed: bool = False
    payload: Payload = None


StreamQueue = asyncio.Queue[Tuple[Iterable[aiobus.Bus[StreamBatch]], StreamBatch]]


class UnsupportedEffectError(ValueError):
    """Unsupported type for a side effect."""


class ReactionMismatchError(Exception):
    """
    Signals that this reaction or group does not recognize the request.

    Depending on the caller type, it either skips to the next reaction or
    returns a default response.

    In either case, this error must be suppressed: it remains the internal
    signalling mechanism of the framework only and is not visible to users.
    """
    pass


class StreamingError(Exception):
    """
    An internal(!) wrapper for errors in streaming if the response is prepared.
    """


@attrs.frozen(kw_only=True, eq=False)
class Request:
    """
    An incoming request with pre-parsed Kubernetes-specific intentions.

    The request can be compared/asserted against a wide range of simpler types
    if they are understod by `Criteria`, so as against `Criteria` itself::

        assert kmock.gets[0] == b'{}'  # bytes are request bodies
        assert kmock.gets[0] == {'status': {}}  # dicts do partial nested json matching
        assert kmock.gets[0] == '/api/v1'  # strings starting with slash are full paths
        assert kmock.gets[0] == re.compile(r'/api/v1.*')  # regexps are paths
        assert kmock.gets[0] == 'get'  # known HTTP methods are directly supported
        assert kmock.gets[0] == 'list'  # known Kubernetes actions are directly supported
        assert kmock.gets[0] == kmock.method.POST  # so as enums
        assert kmock.gets[0] == kmock.action.WATCH  # so as enums
        assert kmock.gets[0] == kmock.resource('', 'v1', 'pods')  # Kubernetes specific resources
        assert kmock.gets[0] == kmock.resource(group='kopf.dev')  # Kubernetes partial resources
        assert kmock.gets[0] == 'ns'  # BEWARE: strings are namespaces, not the requested content

    If implicit comparision is not sufficient, specific fields can be used.
    It is more verbose and wordy but very precise.

    .. note::
        ``int`` is not supported for HTTP statuses: requests have no statuses,
        those are in responses. We do not assert on responses since the user
        typically defines the responses manually.
    """

    id: int = 0  # starts with 0, increments in the handler context

    # Raw HTTP-specifics. We hide the low-level API client, so we have to keep these explicitly.
    # NB: no dict-boxes here! These are factual http data, not the smartly parsed handmade patterns.
    method: enums.method = attrs.field(default=None, converter=enums.method)
    url: yarl.URL = attrs.field(default='', converter=yarl.URL)
    params: Mapping[str, str] = attrs.field(factory=dict)
    headers: Mapping[str, str] = attrs.field(factory=dict)
    cookies: Mapping[str, str] = attrs.field(factory=dict)
    body: bytes = b''
    text: str = ''
    data: Any = None

    # Parsed K8s-specifics (even if it was defined as a raw pattern or was not registered at all).
    action: Optional[enums.action] = None
    resource: Optional[resources.resource] = None
    namespace: Optional[str] = None
    # TODO: for specific requests, namespace is not a pattern, so None means cluster wide.
    #       -> make .clusterwide a property for assertions only (=self.namespace is None)
    clusterwide: Optional[bool] = None
    name: Optional[str] = None
    subresource: Optional[str] = None

    # TODO: maybe add response-specific info, for assertions. Specifically, status is usually request-dependant.
    #   status: Optional[int] = None
    #   runtime: Optional[float] = None

    # None only in tests or other artificial setups.
    # Neither the type nor the protocol are guaranteed, use at your own risk.
    _raw_request: Optional[aiohttp.web.BaseRequest] = attrs.field(default=None, repr=False)

    # Impl note 1: Despite having only one consumer, asyncio.Queue is a bad fit: it wastes memory
    #   on items even when not streamed; and it yields items from before the start of the stream.
    #   The complexity of proper queue flushing on Ellipsis occurrences with nested sub-streams or
    #   nested callbacks grows to the same of the Bus, which flushes at item injection instead.
    # Impl note 2: Despite not being a semantic property of requests per se, the bus here simplifies
    #   the rendering. Otherwise, we have to have a dict{request->bus} in e.g. Root/Handler and pass
    #   it to every response. But we already pass the Request — so why not pass its own bus with it?
    _stream_bus: aiobus.Bus[StreamBatch] = attrs.field(factory=aiobus.Bus, repr=False, init=False)

    @classmethod
    async def _parse(cls: Self, raw_request: aiohttp.web.BaseRequest, *, id: int = 0) -> Self:

        # Normalize the HTTP specifics as much as possible.
        # Ensure the full request payload is fetched & buffered before the connection is closed.
        # We will need the requests later in the tests for assertions/filtering.
        body = await raw_request.read()
        text = await raw_request.text()

        # TODO: try to decode formdata, if possible?
        try:
            data = await raw_request.json()
        except ValueError:  # usually json.JSONDecodeError, but might depend on the module
            try:
                # It is an empty dict for wrong content-types instead of an error, hence "or None".
                data = await raw_request.post() or None
            except ValueError:
                data = None

        # Translate the HTTP request into the K8s request as much as possible.
        k8s = parsing.parse_path(raw_request.path)
        resource = None if k8s is None or k8s.group is None else resources.resource(
            group=k8s.group, version=k8s.version, plural=k8s.plural)
        method = enums.method(raw_request.method)  # even if unknown
        action = parsing.guess_k8s(k8s, method, raw_request.query)
        request = cls(
            id=id, raw_request=raw_request,
            url=raw_request.url,
            method=raw_request.method,
            params=dict(raw_request.query),
            headers=dict(raw_request.headers),
            cookies=dict(raw_request.cookies),
            data=data, body=body, text=text,
            action=action, resource=resource, namespace=k8s.namespace,
            name=k8s.name, subresource=k8s.subresource,
            clusterwide=None if k8s is None or k8s.group is None else bool(k8s.namespace is None),
        )
        return request

    def __hash__(self) -> int:
        return id(self)

    # TODO: Any->Criterion! but it creates circular imports
    #       ? put Criteria + Request into one module?
    #       but keep the per-element parsing away in "parsing.…"
    #       and move away shortcuts elsewhere (or get rid of them)
    def __eq__(self, other: Any) -> bool:
        from kmock import filtering

        try:
            criteria = filtering.Criteria.guess(other)
        except ValueError:
            return NotImplemented
        else:
            return criteria(self)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


@attrs.frozen(kw_only=True)
class Response:
    """
    A pre-assembled response to be sent as a rection to matching requests.

    Typicaly constructed from consecutive ``view << response_item`` calls.
    The containing DSL view that contains a response is :class:`Reaction`.

    Chained feeding (``view << item1 << item2``) either combines the metadata
    (if distinguishable: status, headers, etc.), or creates a stream (if not).
    """

    status: Optional[int] = None
    reason: Optional[str] = None
    payload: Optional[Payload] = None
    cookies: Optional[Mapping[str, str]] = None
    headers: Optional[Mapping[str, str]] = None

    async def __call__(self, request: Request) -> aiohttp.web.StreamResponse:
        # TODO: ??? do we need this? but Response() is readonly/frozen, we cannot alter them.
        # TODO: It MUST be per-request, not per-Response, since Response can be reused (can it?)
        # Metadata can be adjusted during rendering if there are callables/awaitables
        # that return metadata instead of the payload (including other Response objects).
        # After the final response is rendered, restore the metadata to the original state.
        # async with self._transient_metadata():


        try:
            response: aiohttp.web.StreamResponse = await self._render(request, self.payload)
        except (StopIteration, StopAsyncIteration):  # can come from next()/anext() callables
            # TODO: do we need to disable self? can we be reused next time? can next() be conditional?
            # TODO: this has no effect at the moment, as it is not used in matching.
            #       either remove the active state, or reintroduce .active to matching.
            #       or redesign the active state with the new DSL somehow.
            # self.disable()
            # self._disabled.set()
            raise ReactionMismatchError

        # The response-related fields (status) are applied anyway, headers are merged.
        # # TODO: this is dumb. Why not create it properly in the first place?
        if not response.prepared:
            self.__apply_metadata(response)
        # TODO: else check the actual stored values and warn/fail if mismatched.

        return response

    async def _render(self, request: Request, payload: Payload) -> aiohttp.web.StreamResponse:
        # TODO: add lightweight checks of supported types to Renderer.guess() too, as for Effects.

        # No content means that the reaction is a catcher: record the request but continue matching.
        # This includes callables/awaitables that return no content (i.e. no lazy content too).
        if payload is None and self.status is None:
            raise ReactionMismatchError
        elif payload is None:
            return aiohttp.web.Response()
        elif isinstance(payload, Response):
            # TODO: react to pre-interpreted kmock.Response(), unless it is squashed in lshifts
            #       For this, invoke self._render(…, response.payload) deeper,
            #       but merge status/headers/etc into our current one (but restore them afterwards).
            #       The status/headers/etc restoration should happen after __apply_metadata() above.
            object.__setattr__(self, 'status', payload.status)
            object.__setattr__(self, 'reason', payload.reason)
            object.__setattr__(self, 'headers', dict(self.headers or {}, **(payload.headers or {})))
            object.__setattr__(self, 'cookies', dict(self.cookies or {}, **(payload.cookies or {})))
            return await self._render(request, payload.payload)
            # raise NotImplementedError("Response objects are not supported as payloads (yet).")
        # elif isinstance(payload, aiohttp.web.Response):  # TODO: remove?
        #     return payload

        # We hold the side effects in the content field to keep the response items ordered,
        # but effects live their own life with their own type interpretation.
        elif isinstance(payload, SinkBox):
            await self._effect(request, payload._item)
            return await self._render(request, None)  # NB: .status affects the response or skipping

        # Some syntax sugar is reserved for future interpretation, prevent their usage now.
        elif isinstance(payload, (set, frozenset, collections.abc.Set)):
            raise ValueError("Sets are reserved and are not served.")

        # Exceptions are raised in-place. It must go before the callable check.
        elif payload is NotImplemented:
            raise ReactionMismatchError
        elif isinstance(payload, type) and issubclass(payload, StopIteration):
            # Python prohibits synchronous StopIteration from coroutines, so we convert it here.
            raise StopAsyncIteration
        elif isinstance(payload, StopIteration):
            # Python prohibits synchronous StopIteration from coroutines, so we convert it here.
            raise StopAsyncIteration(*payload.args) from payload
        elif isinstance(payload, BaseException):
            raise payload
        elif isinstance(payload, type) and issubclass(payload, BaseException):
            raise payload

        # Binaries go to the response as is, uninterpreted.
        elif isinstance(payload, bytes):
            return aiohttp.web.Response(body=payload)
        elif isinstance(payload, pathlib.Path):
            return aiohttp.web.Response(body=payload.read_bytes())
        elif isinstance(payload, (io.RawIOBase, io.BufferedIOBase, io.TextIOBase)):
            return aiohttp.web.Response(body=payload.read())

        # Lazy content is unfolded into real content at request time, not at definition time.
        # Beware: callables and awaitables can raise here, i.e. without further recursion.
        # Beware: futures are iterable (for some weird reason), they must go first.
        elif isinstance(payload, collections.abc.Awaitable):  # coroutines, futures, tasks
            result = await payload
            return await self._render(request, result)
        elif callable(payload):  # sync & async callbacks, lambdas, partials
            result = payload(request) if inspect.signature(payload).parameters else payload()
            return await self._render(request, result)

        # Tuples, generators, and other iterables (except lists & sets) go as streams.
        elif isinstance(payload, (collections.abc.Iterable, collections.abc.AsyncIterable)) and not isinstance(payload, (str, list, collections.abc.Mapping, collections.abc.Set)):
            if request._raw_request is None:  # for type checkers: it is None only in some tests.
                raise RuntimeError("Streaming is only possible when raw request is present.")
            raw_response = aiohttp.web.StreamResponse()
            self.__apply_metadata(raw_response)
            try:
                # Postpone the HTTP/TCP initial traffic until the very first real(!) chunk arrives.
                # With this, the renderer can do invisible side effects or e.g. raise StopIteration
                # to skip serving the request and pass it to the next renderers in line/priority.
                # possibly with other status/headers or even to non-streams (e.g. 404/410/JSON).
                # If the stream is prepared before chunk-yielding, there is no way back except as
                # to reuse the pre-initialized response with maybe wrong status/headers.
                stream = self._stream(request, payload)
                chunk = await anext(stream)
                try:
                    await raw_response.prepare(request._raw_request)
                    await raw_response.write(chunk)
                    async for chunk in stream:
                        await raw_response.write(chunk)
                    await raw_response.write_eof()
                except ConnectionError:
                    pass  # the client sometimes disconnects earlier, ignore it

            # This stream is depleted, try the next pattern (maybe not a stream). Comes from anext()
            except StopAsyncIteration:
                raise ReactionMismatchError
            except Exception as e:
                raise StreamingError(raw_response) from e

        # Standalone ellipsis (not wrapped into a tuple) can become a stream or a simple payload.
        # It depends on the actual value fed into the corresponding live view, i.e. kmock[...].
        elif payload is Ellipsis:
            batch: StreamBatch = await request._stream_bus.get()
            batch.consumed = True
            return await self._render(request, batch.payload)

        # Everything that syntactically looks like JSON, goes as JSON: [], {}, strs, ints, floats…
        # Mind that strings go quoted, not as the raw payload (use bytes for that).
        # Note it is confirmed payload; positional ints are classified as status at earlier stages.
        # TODO: datetime (ISO 8601), timedelta (ISO 8601), and more?
        #       can we have a custom json-serializer, and simply let it render the value,
        #       and if it fails, fail it on our side?
        #       BUT: aiohttp does this now, with proper ContentTypes & other fields.
        elif isinstance(payload, (int, float, bool, str, list, dict, collections.abc.Mapping)):
            return aiohttp.web.json_response(payload)

        else:
            raise ValueError(f"Unsupported payload type: {type(payload)}")

    async def _stream(self, request: Request, item: Payload) -> AsyncIterable[bytes]:
        """
        Render a streamed item into chunks of bytes to send in the response.

        One content item can produce 0…♾️ chunks, e.g. if it is a callback.
        All such chunks are sent on their own without concatenation.
        """

        # Nones usually come as a result of callables/awaitables with other useful side effects.
        if item is None:
            pass

        # We hold the side effects in the content field to keep the response items ordered,
        # but effects live their own life with their own type interpretation.
        elif isinstance(item, SinkBox):
            await self._effect(request, item._item)

        # Exceptions are raised in-place. It must go before the callable check.
        elif isinstance(item, BaseException):
            raise item
        elif isinstance(item, type) and issubclass(item, BaseException):
            raise item

        # Binaries go to the stream as is, uninterpreted.
        elif isinstance(item, bytes):
            yield item
        elif isinstance(item, pathlib.Path):
            yield item.read_bytes()
        elif isinstance(item, io.TextIOBase):
            yield item.read().encode('utf-8')
        elif isinstance(item, (io.RawIOBase, io.BufferedIOBase)):
            yield item.read()

        # Lazy content is unfolded into real content at request time, not at definition time.
        # Beware: callables and awaitables can raise here, i.e. without further recursion.
        # Beware: futures are iterable (for some weird reason), they must go first.
        elif isinstance(item, collections.abc.Awaitable):  # coros, futures, tasks
            result = await item
            async for chunk in self._stream(request, result):
                yield chunk
        elif callable(item):  # sync & async callbacks, lambdas, partials
            result = item(request) if inspect.signature(item).parameters else item()
            async for chunk in self._stream(request, result):
                yield chunk

        # Everything that visually looks like JSON, goes as JSON: [], {}, strs, ints, floats…
        # Mind that strings go quoted, not as the raw payload (used bytes for that).
        # TODO: datetimes, timedeltas, see above for _render()
        elif isinstance(item, (int, float, bool, str, list, dict, collections.abc.Mapping)):
            yield json.dumps(item).encode('utf-8') + b'\n'

        # Tuples, generators, and other iterables are sub-streams.
        elif isinstance(item, (set, frozenset, collections.abc.Set)):
            raise ValueError("Sets are reserved and are not served.")
        elif isinstance(item, collections.abc.Iterable):
            for subitem in item:
                async for chunk in self._stream(request, subitem):
                    yield chunk
        elif isinstance(item, collections.abc.AsyncIterable):
            # Escalate StopAsyncIteration if the source is depleted, to match the next reaction.
            yield await anext(item)
            async for subitem in item:
                async for chunk in self._stream(request, subitem):
                    yield chunk

        # Live streams stream live, with tail optimization & some extra item interpretation.
        elif item is Ellipsis:
            async for subitem in self.__optimize_tail(request._stream_bus):
                async for chunk in self._stream(request, subitem):
                    yield chunk
        else:
            raise ValueError(f"Unsupported streaming type: {type(item)}")

    async def __optimize_tail(self, bus: aiobus.Bus[StreamBatch]) -> AsyncIterator[Payload]:
        """
        Unfold from a bus into a flat stream & optimize the tail recursion.

        For live streams, only one batch of items is processed at a time.
        The live stream either ends or continues if a new ellipsis was added.
        Stream tails (items after the ellipsis) remain on hold for later,
        i.e. when a new batch is injected with no ellipsis in it.

        Tail optimization means that recursion is avoided when not needed,
        and it runs in a simple same-level for/while cycle.
        Stateful cases with tail items —(a,...,b)— are recursed as the only way.
        Deterministic cases —(a,b,...) or (a,(b,(...,)))— are tail-optimized.
        Lazy-eval cases —(a,b,lambda:...)— cannot be optimized due to ambiguity,
        but this can be revised in the future if a good algorithm is found.
        """
        tail_ellipsis = True
        while tail_ellipsis:
            batch: StreamBatch = await bus.get()
            batch.consumed = True
            flat_batch = self.__unfold(batch.payload)
            tail_ellipsis = flat_batch and flat_batch[-1] is Ellipsis
            for batch in flat_batch[:-1] if tail_ellipsis else flat_batch:
                yield batch

    def __unfold(self, item: Payload) -> Sequence[Payload]:
        """
        Flatten the batch of nested tuples (but not of lists or iterables!).

        Callables & awaitables & other lazy-evaluated items are not resolved
        to avoid premature or out-of-order side-effects. Tuples and only tuples!

        It is NOT exposed to users and is used only for better tail optimization
        to cover all deterministic cases instead of only top-level Ellipsis.
        """
        flat_batch: List[Payload] = []
        if isinstance(item, tuple):  # and tuples only! not lists, not iterables!
            for subitem in item:
                flat_batch.extend(self.__unfold(subitem))
        else:
            flat_batch.append(item)
        return tuple(flat_batch)

    async def _effect(self, request: Request, sink: Sink) -> None:
        if sink is None:
            pass

        # TODO: write the whole request with verb + headers!!!!
        elif isinstance(sink, pathlib.Path):
            sink.write_bytes(request.body)
        elif isinstance(sink, io.TextIOBase):
            sink.write(request.text)
        elif isinstance(sink, (io.RawIOBase, io.BufferedIOBase)):
            sink.write(request.body)

        # Synchronization primitives are also supported.
        elif isinstance(sink, aiobus.Bus):
            await sink.put(request)
        elif isinstance(sink, asyncio.Event):
            sink.set()
        elif isinstance(sink, asyncio.Queue):
            await sink.put(request)
        elif isinstance(sink, queue.Queue):
            sink.put(request)  # beware: it can block the whole event loop
        elif isinstance(sink, asyncio.Condition):
            async with sink:
                sink.notify_all()
        elif isinstance(sink, asyncio.Future) and not isinstance(sink, asyncio.Task):
            sink.set_result(request)
        elif isinstance(sink, concurrent.futures.Future):
            sink.set_result(request)
        elif isinstance(sink, threading.Event):
            sink.set()  # beware: it can block the whole event loop
        elif isinstance(sink, threading.Condition):
            with sink:  # beware: it can block the whole event loop
                sink.notify_all()

        # Raw mutable containers accumulate requests. E.g.: kmock>>(reqs:=[])
        elif isinstance(sink, collections.abc.MutableSet):
            sink.add(request)
        elif isinstance(sink, collections.abc.MutableSequence):
            sink.append(request)
        elif isinstance(sink, collections.abc.MutableMapping):
            sink[request] = request.data or request.body or None

        # Generators (but not simple iterators/iterables) get the requests from their `yield`.
        # The yield is interpreted as if it were an effect, or ignored if not recognized.
        elif isinstance(sink, collections.abc.Generator):
            result = sink.send(request)
            await self._effect(request, result)
        elif isinstance(sink, collections.abc.AsyncGenerator):
            result = await sink.asend(request)
            await self._effect(request, result)

        # Lazy content is unfolded into real content at request time, not at definition time.
        # Beware: callables and awaitables can raise here, i.e. without further recursion.
        # Beware: futures are iterable (for some weird reason), they must go first.
        elif isinstance(sink, collections.abc.Awaitable):  # coroutines, futures, tasks
            result = await sink
            try:
                await self._effect(request, result)
            except UnsupportedEffectError:
                pass
        elif callable(sink):  # sync & async callbacks, lambdas, partials
            result = sink(request) if inspect.signature(sink).parameters else sink()
            try:
                await self._effect(request, result)
            except UnsupportedEffectError:
                pass

        else:
            # ValueError is sufficient for users, but we need to intercept this case in excepts.
            raise UnsupportedEffectError(f"Unsupported side-effect type: {type(sink)}")

    @classmethod
    def guess(cls, arg: Union[Payload, PayloadBox]) -> Self:
        # TODO: parse "200 OK" strings into status+reason?
        if arg is None:
            return cls()
        elif not isinstance(arg, bool) and isinstance(arg, int) and 100 <= arg < 1000:
            return cls(status=arg)
        # TODO: and check that all values are precise, no regexps inside there.

        # Unpack purpose-hinting boxes into purpose-specific classes & fields.
        elif isinstance(arg, boxes.body):
            return cls(payload=arg.body)
        elif isinstance(arg, boxes.text):
            return cls(payload=arg.text)
        elif isinstance(arg, boxes.data):
            return cls(payload=arg.data)
        elif isinstance(arg, boxes.headers):
            return cls(headers=dict(arg))
        elif isinstance(arg, boxes.cookies):
            return cls(cookies=dict(arg))

        elif isinstance(arg, collections.abc.Mapping) and parsing.are_all_known_headers(arg):
            return cls(headers=arg)
        elif isinstance(arg, (set, frozenset, collections.abc.Set, boxes.params, boxes.path)):
            raise ValueError(f"Unsupported payload type: {type(arg)}")
        elif isinstance(arg, type) and issubclass(arg, BaseException):
            return cls(payload=arg)
        elif isinstance(arg, (Response, SinkBox)):
            return cls(payload=arg)
        else:
            cls.__verify_payload(arg)
            return cls(payload=arg)

    @classmethod
    def __verify_payload(cls, payload: Payload) -> None:
        if payload is None:
            pass
        # TODO: pre-interpreted kmock.Response()?
        elif isinstance(payload, aiohttp.web.StreamResponse):
            raise ValueError(f"Unsupported payload type: {type(payload)}")
        elif isinstance(payload, (set, frozenset, collections.abc.Set)):  # reserved for future
            raise ValueError(f"Unsupported payload type: {type(payload)}")
        elif isinstance(payload, type) and issubclass(payload, BaseException):
            pass
        elif isinstance(payload, tuple):  # safe introspection of simple streams without depletion
            for item in payload:
                cls.__verify_payload(item)
        elif isinstance(payload, SUPPORTED_PAYLOADS):
            pass
        else:
            raise ValueError(f"Unsupported payload type: {type(payload)}")

    def __add__(self, other: "Response") -> "Response":
        """
        Combine 2 responses into one.

        Metadata (status, headers, cookies, etc) from both sides is combined.
        If they have conflicting metadata values, an error is raised.
        Payloads (the response bodies) from both sides are packed to a stream.
        """
        if not isinstance(other, Response):
            return NotImplemented

        if self.status is not None and other.status is not None:
            warnings.warn(f"Ambiguous statuses: {self.status!r} vs. {other.status!r}", UserWarning)
        status = other.status if other.status is not None else self.status

        # TODO: None must mean "delete the header if it was there before, ignore/drop otherwise"
        a_headers = {key: val for key, val in (self.headers or {}).items() if val is not None}
        b_headers = {key: val for key, val in (other.headers or {}).items() if val is not None}
        conflicting_keys = sorted(set(a_headers) & set(b_headers))
        if conflicting_keys:
            warnings.warn(f"Ambiguous headers: {conflicting_keys!r}", UserWarning)
        headers = dict(a_headers, **b_headers)

        cookies = self.cookies  # TODO: self.merge_dicts
        reason = self.reason  # TODO

        if self.payload is None:
            payload = other.payload
        elif other.payload is None:
            payload = self.payload

        # Fail on conceptually conflicting contents: e.g., 2 full responses cannot be joined.
        elif isinstance(self.payload, aiohttp.web.StreamResponse):
            if other.payload is not None:
                warnings.warn(f"Ambiguous content: {self.payload!r} vs. {other.payload!r}", UserWarning)
            payload = other.payload
        elif isinstance(other.payload, aiohttp.web.StreamResponse):
            if self.payload is not None:
                warnings.warn(f"Ambiguous content: {self.payload!r} vs. {other.payload!r}", UserWarning)
            payload = other.payload

        # Optimize: combine immutable repeatable streams into a flat stream, for simplicity.
        elif isinstance(self.payload, tuple) and isinstance(other.payload, tuple):
            payload = self.payload + other.payload
        elif isinstance(self.payload, tuple):
            payload = self.payload + (other.payload,)
        elif isinstance(other.payload, tuple):
            payload = (self.payload,) + other.payload
        else:
            payload = (self.payload, other.payload)

        return attrs.evolve(
            self,
            status=status, reason=reason,
            cookies=cookies, headers=headers,
            payload=payload,
        )

    def __apply_metadata(self, raw_response: aiohttp.web.StreamResponse) -> None:
        """
        Transfer the metadata (status, headers, etc) into a raw response.
        """
        if self.status is not None:
            raw_response.set_status(self.status, self.reason)
        for header_name, header_val in (self.headers or {}).items():
            if header_val is not None:
                raw_response.headers[header_name] = header_val
        for cookie_name, cookie_val in (self.cookies or {}).items():
            if cookie_val is not None:
                raw_response.set_cookie(cookie_name, cookie_val)
            else:
                raw_response.del_cookie(cookie_name)
