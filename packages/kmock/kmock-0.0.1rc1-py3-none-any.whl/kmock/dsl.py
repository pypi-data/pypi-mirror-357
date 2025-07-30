import abc
import asyncio
import functools
import math
import operator
from types import TracebackType
from typing import AsyncIterator, Iterable, Iterator, List, Optional, Sequence, Set, Tuple, Type, TypeVar, Union, \
    overload

import aiohttp.web
import attrs
from typing_extensions import Self, override

from kmock import aiobus, filtering, rendering

_V = TypeVar('_V', bound="View")


@attrs.define
class View(Sequence[rendering.Request], abc.ABC):
    """
    A base view into collections of requests with all the filtering DSL in it.
    """

    def _walk(self, cls: Type[_V], unique: bool = False) -> Iterator[_V]:
        if isinstance(self, cls):
            yield self

    @overload
    def __getitem__(self, item: None) -> Self:
        ...

    @overload
    def __getitem__(self, item: int) -> rendering.Request:
        ...

    @overload
    def __getitem__(self, item: slice) -> "Slicer":
        ...

    @overload
    def __getitem__(self, item: rendering.EllipsisType) -> "Stream":
        ...

    @overload
    def __getitem__(self, item: filtering.Criterion) -> "Filter":
        ...

    @overload
    def __getitem__(self, item: Set[filtering.Criterion]) -> "OrGroup":
        ...

    @overload
    def __getitem__(self, item: Tuple[filtering.Criterion, ...]) -> "AndGroup":
        ...

    def __getitem__(self, item: Union[None, int, slice, rendering.EllipsisType, filtering.Criterion, Set[filtering.Criterion], Tuple[filtering.Criterion, ...]]) -> Union[rendering.Request, "View"]:
        # NB: only the DSL-specific type checks here! Not the criteria--specific!
        if item is None:
            return self
        elif item is Ellipsis:
            return Stream(self)
        elif isinstance(item, int) and not isinstance(item, bool):
            return list(iter(self))[item]  # a request, not a new view
        elif isinstance(item, slice):
            return Slicer(self, s=item)
        elif isinstance(item, (tuple, list)):
            # No worries: the chained same-kind criteria are merged for optimization.
            result = self
            for subitem in item:
                result = result[subitem]
            return result
        elif isinstance(item, (set, frozenset)) and not item:
            return self
        elif isinstance(item, (set, frozenset)) and len(item) == 1:
            return self[list(item)[0]]
        elif isinstance(item, (set, frozenset)):
            return OrGroup([self[subitem] for subitem in item])
        else:
            try:
                criteria = filtering.Criteria.guess(item)
            except ValueError:
                return NotImplemented
            else:
                return Filter(self, criteria) if criteria is not None else NotImplemented

    def __lshift__(self, other: rendering.Payload) -> "Reaction":
        new = Reaction(self) << other
        for root in self._walk(Root, unique=True):
            root._payloads.append(new)
        return new

    def __rshift__(self, other: rendering.Sink) -> "Reaction":
        new = Reaction(self) >> other
        for root in self._walk(Root, unique=True):
            root._payloads.append(new)
        return new

    def __rlshift__(self, other: rendering.Payload) -> "Reaction":
        return self.__rshift__(other)

    def __rrshift__(self, other: rendering.Sink) -> "Reaction":
        return self.__lshift__(other)

    def __or__(self, other: "View") -> "OrGroup":
        if isinstance(other, View):
            return OrGroup([self, other])
        return NotImplemented

    def __and__(self, other: "View") -> "AndGroup":
        if isinstance(other, View):
            return AndGroup([self, other])
        return NotImplemented

    def __sub__(self, other: "View") -> "Exclusion":
        if isinstance(other, View):
            return Exclusion(self, [other])
        return NotImplemented

    def __invert__(self) -> "Exclusion":
        roots = list(self._walk(Root, unique=True))
        return Exclusion(OrGroup(roots), [self])

    def __ror__(self, other: "View") -> "OrGroup":
        return self.__or__(other)

    def __rand__(self, other: "View") -> "AndGroup":
        return self.__and__(other)

    def __len__(self) -> int:
        # Pure list(self) causes RecursionError in PyPy: pre-allocation of lists from sized sources?
        return len(list(iter(self)))

    def __contains__(self, item: filtering.Criterion) -> bool:
        if isinstance(item, rendering.Request):
            # Check by identity! — to not produce false-positives for similar repeated requests.
            return any(request is item for request in self)
        else:
            return bool(self[item])

    def __bool__(self) -> bool:
        try:
            next(iter(self))
        except StopIteration:
            return False
        else:
            return True

    async def __aiter__(self) -> AsyncIterator[rendering.Request]:
        for item in self:
            yield item

    def __pow__(self, power: float, modulo: float = None) -> "Priority":
        return Priority(self, power)

    @property
    def override(self) -> "Priority":
        return self ** math.inf

    @property
    def fallback(self) -> "Priority":
        return self ** -math.inf


@attrs.define  # not frozen: it can be inherited as mutable
class Root(View):
    """
    A view for the root handlers/servers where the requests first arrive.

    It is needed as the terminal point of walking the tree of views
    for registering the payloads on ``<<`` & ``>>`` operators. Also
    as a shared sync-to-async live feeder (at least one root must be "entered").
    """

    # The source of truth for all requests arrived to this server/handler.
    # But it should be accessed only via the DSL: indexes, slices, iterators.
    _requests: List[rendering.Request] = attrs.field(factory=list, init=False)

    # The reactions/responses/side-effects to consider for a matching request.
    # Filled by the <<>> operators with the newer ones replacing the older ones.
    _payloads: List["Reaction"] = attrs.field(factory=list, init=False)

    # Helpers for sync-to-async queue-to-bus stream feeding as used in dsl.Stream.<</>>
    _stream_queue: rendering.StreamQueue = attrs.field(factory=asyncio.Queue)
    _stream_task: Optional[asyncio.Task] = None

    def __iter__(self) -> Iterator[rendering.Request]:
        return iter(self._requests)

    async def __aenter__(self: Self) -> Self:
        if self._stream_task is None:
            self._stream_task = asyncio.create_task(self._sync_bus_feeder())
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self._stream_task is not None:
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass
            self._stream_task = None

    async def _sync_bus_feeder(self) -> None:
        while True:
            buses, item = await self._stream_queue.get()
            for bus in buses:
                await bus.put(item)


@attrs.frozen
class Group(View):
    """Base class for ``&`` & ``|`` logic groups of views."""
    _sources: Sequence[View]

    @override
    def _walk(self, cls: Type[_V], unique: bool = False) -> Iterator[_V]:
        yield from super()._walk(cls, unique)
        seen: Set[int] = set()
        for source in self._sources:
            for view in source._walk(cls, unique):
                if not unique or not id(view) in seen:
                    seen.add(id(view))
                    yield view


@attrs.frozen
class OrGroup(Group):
    """
    The OR-group to check that a request belongs to ANY of the grouped filters.

    Examples: ``(kmock['get'] | kmock['/'] | kmock['?q=query']) << b'hello'``,
    except that not all filters can be put in a set (e.g. dicts).

    When it comes to iterating or indexing the requests, they are concatenated
    in the order of grouping, i.e. ``a|b|c`` are yielded in this order: a, b, c.
    As such, ``(a|b|c)[0]`` or ``(a|b|c)[-1]`` can belong to either group
    depending on what is seen (recorded & filtered) in the other groups.
    """

    def __iter__(self) -> Iterator[rendering.Request]:
        # Iterate over requests strictly in their chronological order. Since the sourcing filters
        # can deliver different sets of requests, we cannot merge them properly. As such, we must
        # iterate over the root and only check if each request is seen through the sourcing filters.
        # Grouped filters from different roots, if any, iterate in the order of their chaining.
        # For performance, materialize all seen requests locally once — this costs us memory, but
        # avoids the __contains__ checks and materializing of each source for each single request.
        inputs: List[Set[int]] = [{id(request) for request in filter} for filter in self._sources]
        ids: Set[int] = functools.reduce(operator.or_, inputs or [{}])
        for root in self._walk(Root, unique=True):  # deduplicated, in the order of chaining
            for request in root:
                if id(request) in ids:
                    yield request

    def __or__(self, other: View) -> "OrGroup":
        # Optimize chained ORs into one.
        if isinstance(other, OrGroup):  # ((a|b)|(c|d))
            return OrGroup(self._sources + other.filters)
        if isinstance(other, View):  # (((a|b)|c)|d)
            return OrGroup(self._sources + [other])
        return super().__or__(other)


@attrs.frozen
class AndGroup(Group):
    """
    The AND-group to check that a request belongs to ALL of the grouper filters.

    Examples: ``kmock['get'] & kmock['/']``. The same as ``kmock['get', '/']``.

    Grouping views to different roots (handlers/servers) makes no sense, as it
    will always be empty by definition (a request can come only from one root).
    """

    def __iter__(self):
        inputs: List[Set[int]] = [{id(request) for request in filter} for filter in self._sources]
        ids: Set[int] = functools.reduce(operator.and_, inputs)
        for root in self._walk(Root, unique=True):  # deduplicated, in the order of chaining
            for request in root:
                if id(request) in ids:
                    yield request

    def __and__(self, other: View) -> "AndGroup":
        # Optimize chained ANDs into one.
        if isinstance(other, AndGroup):  # ((a&b)&(c&d))
            return AndGroup(self._sources + other.filters)
        if isinstance(other, View):  # (((a&b)&c)&d)
            return AndGroup(self._sources + [other])
        return super().__and__(other)


@attrs.frozen
class Chained(View):
    """
    A base view for all other views with a single source, forming a _chain_.
    """
    _source: View = attrs.field(repr=False)

    def __iter__(self) -> Iterator[rendering.Request]:
        return iter(self._source)

    @override
    def _walk(self, cls: Type[_V], unique: bool = False) -> Iterator[_V]:
        yield from super()._walk(cls, unique)
        yield from self._source._walk(cls, unique)


@attrs.frozen
class Exclusion(Chained):
    """
    A NOT-filter for requests in the source EXCEPT requests in excluded sources.

    Examples: ``kmock['get'] - kmock['/'] - kmock['?q=query']``.
    """
    _exclusions: List[View]

    def __iter__(self):
        inputs: List[Set[int]] = [{id(request) for request in filter} for filter in self._exclusions]
        excluded: Set[int] = functools.reduce(operator.or_, inputs)
        for request in super().__iter__():
            if id(request) not in excluded:
                yield request

    def __sub__(self, other: View) -> "Exclusion":
        if isinstance(other, View):  # (((a-b)-c)-d), but not (a-b)-(c-d)!
            return Exclusion(self._source, self._exclusions + [other])
        return super().__sub__(other)


@attrs.frozen
class Slicer(Chained):
    """
    A slice of requests, as in list: with the ``[start:stop:step]`` notation.

    Examples: ``kmock['get'][1:]``, ``kmock['post'][:3]``, ``kmock['/'][::2]``.
    """
    s: slice

    def __iter__(self) -> Iterator[rendering.Request]:
        # We have to materialize the source to properly slice it (slice simulation is difficult).
        return iter(list(super().__iter__())[self.s])


@attrs.frozen
class Filter(Chained):
    """
    A criteria-based filter or filter by arbitrary bool-evaluable callback.

    Examples:

    - ``kmock['get']['/'][{'watch': 'true'}]``
    - ``kmock[{'Content-Type': 'application/json'}]``
    - ``kmock[lambda req: req.params.get('idx') == '5']``
    - ``kmock['post', kmock.body(re.compile(r'.*hello.*'))]``

    A sequence of filters is collapsed into one filter preserving the logic.
    If there are apparently conflicting criteria, which lead to no result,
    an errors is raised: e.g. ``kmock['get']['post']``.
    """
    criteria: filtering.Criteria

    @overload
    def __getitem__(self, item: None) -> Self:
        ...

    @overload
    def __getitem__(self, item: int) -> rendering.Request:
        ...

    @overload
    def __getitem__(self, item: slice) -> "Slicer":
        ...

    @overload
    def __getitem__(self, item: filtering.Criterion) -> "Filter":
        ...

    @overload
    def __getitem__(self, item: Tuple[filtering.Criterion, ...]) -> "Filter":
        ...

    def __getitem__(self, item: Union[None, int, slice, filtering.Criterion]) -> Union[rendering.Request, "View"]:
        new = super().__getitem__(item)
        # Try to optimize/collapse chained criteria into one to ease the debugging & save RAM.
        # This also helps to catch the conflicting requirements, which otherwise lead to no matches.
        # NB: Arbitrary callables cannot be merged with anything, so they remain chained.
        #     Besides, do not optimize cases like `kmock['get'][fn]['/']` due to ambiguity:
        #     the fn() must see all GETs but no POSTs, and all /paths/, not only /.
        if isinstance(new, Filter) and type(new) is Filter and new._source is self:
            if isinstance(self.criteria, filtering.OptiCriteria):
                if isinstance(new.criteria, filtering.OptiCriteria):
                    if type(new.criteria) is type(self.criteria):
                        new = Filter(self._source, criteria=self.criteria + new.criteria)
        return new

    def __iter__(self) -> Iterator[rendering.Request]:
        for request in super().__iter__():
            if self.criteria(request):
                yield request


@attrs.frozen
class Priority(Chained):
    """
    An internal hint to pass the info through the chain.

    It is consumed when ordering the payloads to be served on each request.

    The chain can stretch from the first root node till the final payload node,
    e.g.: ``kmock.fallback['get']['/'][:1] << b''``;
    or directly precede the payload: ``kmock['get']['/'][:1].fallback << b''``.

    An alternative would be to store the priority attribute on every node,
    even on those that have no use or need for prioritizing (bad abstractions).

    A little optimization is possible by popping up the priority node
    on every other node creation, and then merging it with the payload node.
    This adds code complexity and slightly misaligned type annotations
    with little performance benefit.
    """
    priority: float


# NB: the .source is checked in the RawHandler, when checking if a request is suitable for serving.
@attrs.frozen
class Reaction(Chained):
    """
    An actionable response reaction for a filter with payloads and side effects.

    Examples:

    - ``kmock['get /'] << b'hello'``
    - ``kmock['get /'] >> callback_fn >> (reqs:=[])``
    - ``kmock['get /'] << 301 << 'Location: https://kopf.dev' << b'Use Kopf!'``
    - ``kmock.fallback << 404``

    Worth noting: creating a new reaction from the old reaction (by using
    chained ``<<`` & ``>>`` operators) does not simply add the new reaction
    in addition to the old one, but **replaces** it to avoid duplicates.

    As such, in this code, ``r1`` will never serve or record any requests,
    only ``r2`` will (both payload items will be served by ``r2`` as a stream).
    Essentially, ``r1`` becomes abandoned & deactivated at creation of ``r2``::

        r1 = kmock['get /'] << b'hello, '
        r2 = r1 << b'world!\n'

    This is an intentional design decision. Otherwise, i.e. by keeping ``r1``
    active, it might lead to iconsistencies: either ``r1`` will record requests
    that it did not actually serve, or ``r1`` will serve regular (non-streamed)
    payloads followed by streaming ``r2``, which is a conflicting behaviour.

    For extra code safety, assertions on deactivated reactions are prohibited.
    If there is a scenaro where this is needed, please report it as an issue.

    .. seealso: :doc:`/responses`
    """
    response: rendering.Response = attrs.field(factory=rendering.Response)

    # Every impactful view (i.e. a payload) only "sees" the requests that managed to get to it
    # and does not see the requests intercepted by earlier payloads for the same criteria.
    _requests: List[rendering.Request] = attrs.field(factory=list, init=False)

    _disabled: asyncio.Event() = attrs.field(factory=asyncio.Event, init=False)

    async def __call__(self, request: rendering.Request) -> aiohttp.web.StreamResponse:
        self._requests.append(request)
        return await self.response(request)

    def __iter__(self) -> Iterator[rendering.Request]:
        # For extra safety in code-writing, prohibit accessing/asserting the deactivated reactions.
        if all(payload is not self for root in self._walk(Root) for payload in root._payloads):
            raise RuntimeError("Accessing requests of a deactivated reaction is prohibited.")
        yield from iter(self._requests)

    def __lshift__(self, arg: rendering.Payload) -> Self:
        try:
            new = attrs.evolve(self, response=self.response + rendering.Response.guess(arg))
        except TypeError:
            return NotImplemented

        # Substitute self in its original position (important!) with the new response.
        # Note: if it is not there, it will NOT be appended — append explicitly!
        for root in self._walk(Root, unique=True):
            root._payloads[:] = [new if payload is self else payload for payload in root._payloads]
        return new

    def __rshift__(self, other: rendering.Sink) -> Self:
        return self << rendering.SinkBox(other)

    @property
    def priority(self) -> float:
        try:
            return next(self._walk(Priority)).priority
        except StopIteration:
            return 0


@attrs.frozen
class Stream(Chained):
    """
    A pseudo-view into "live" (aka "lazy") responses or streams.

    Examples:

    - ``kmock['/'] << ...; loop.call_later(9, lambda: kmock['get /'][...] << b'hello')``
    - ``kmock['/'] << (...,); loop.call_later(9, lambda: kmock[...] << b'all streams see' << ...)``

    .. seealso: :doc:`/live`
    """

    # An accumulator of payloads and a state exchange (fed/consumed) between producers & consumers.
    _batch: rendering.StreamBatch = attrs.field(factory=rendering.StreamBatch)

    def __iter__(self) -> Iterator[rendering.Request]:
        for request in super().__iter__():
            if request._stream_bus.consumer_count:
                yield request

    def __lshift__(self, other: rendering.Payload) -> Self:

        # Prevent accidental feeding after the batch is streamed. Start a new batch instead!
        # This can only happen if users remember the result of kmock[...], not access it anew.
        if self._batch.consumed:
            raise RuntimeError("Cannot feed new items to an already consumed batch. Create a new batch with [...].")

        # Feed into all buses in the current view (with all filters & slices & grouping applied).
        # Only currently streaming (stream-consuming) requests will actually see the fed items.
        reqs: List[rendering.Request] = list(iter(self))
        roots: Iterable[Root] = self._walk(Root, unique=True)
        buses: List[aiobus.Bus[rendering.StreamBatch]] = [req._stream_bus for req in reqs]
        queues = [root._stream_queue for root in roots if root._stream_task is not None]
        if not queues:
            raise RuntimeError("Live feeding is only possible if the mock handler is entered.")

        # Register the batch at most once (though keep it mutable for later additions).
        if not self._batch.fed:
            self._batch.fed = True
            queues[0].put_nowait((buses, self._batch))

        # Collapse sequential feeds into one batch, as long as we stay in the sync part of the code.
        # Only giving control away with ``await`` consumes those, so no locks are needed.
        # E.g.: kmock[...]<<a<<b<<c<<... is the same as kmock[...]<<(a,b,c,...)
        if self._batch.payload is None:
            self._batch.payload = other
        elif isinstance(self._batch.payload, tuple) and isinstance(other, tuple):
            self._batch.payload = self._batch.payload + other
        elif isinstance(self._batch.payload, tuple):
            self._batch.payload = self._batch.payload + (other,)
        elif isinstance(other, tuple):
            self._batch.payload = (self._batch.payload,) + other
        else:
            self._batch.payload = (self._batch.payload, other)

        return self

    def __rshift__(self, other: rendering.Sink) -> Self:
        return self << rendering.SinkBox(other)
