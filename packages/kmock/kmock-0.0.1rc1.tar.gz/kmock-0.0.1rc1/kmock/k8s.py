import asyncio
import collections.abc
import copy
import datetime
import itertools
import json
import random
import string
import traceback
from typing import Any, Collection, Dict, Hashable, Iterable, Iterator, List, Mapping, MutableMapping, MutableSequence, \
    Optional, \
    Sequence, Set, \
    Tuple, TypeVar, Union, \
    overload

import aiohttp.web
import attrs
from typing_extensions import override, Self

from kmock import aiobus, apps, dsl, enums, filtering, rendering, resources


@attrs.define
class KubernetesScaffold(apps.RawHandler):
    """
    A bare structure of the Kubernetes API: errors, API & resource discovery.

    It is stateless! It keeps nothing in memory except for what was fed into it.
    For a stateful server, see :class:`KubernetesEmulator`.
    """

    # server_version: str = '0.0.0'  # TODO: but there are many more fields

    # def __attrs_post_init__(self) -> None:
    #     # TODO: can we say 'if the resource was parsed/defined, then go'? without duplicating the URL pattern here.
    #     self.fallback['get', re.compile(r'/apis/[^/]+/[^/]+')] << self._serve_version
    #     self.fallback['get', re.compile(r'/apis/[^/]+')] << self._serve_group
    #     self.fallback['get', re.compile(r'/api/[^/]+')] << self._serve_version
    #     self.fallback['get /version'] << self._serve_server_version
    #     self.fallback['get /apis'] << self._serve_apis
    #     self.fallback['get /api'] << self._serve_api
    #     self.fallback['get /'] << self._serve_root
    #     self.fallback << 404

    @override
    async def _render_error(self, exc: Exception) -> aiohttp.web.StreamResponse:
        # For Kubernetes server, we simulate Kubernetes error in the hope that
        # clients will understand it properly and re-raise internally.
        # https://kubernetes.io/docs/reference/kubernetes-api/common-definitions/status/
        return aiohttp.web.json_response({
            'apiVersion': 'v1',
            'kind': 'Status',
            'metadata': {},
            'code': 500,
            'status': 'Failure',
            'reason': type(exc).__name__,
            'message': repr(exc),
            'details': {'traceback': traceback.format_exc()},
        }, status=500)

    @override
    async def _stream_error(self, exc: Exception, raw_response: aiohttp.web.StreamResponse) -> None:
        error = json.dumps({
            'type': 'ERROR',
            'object': {
                'apiVersion': 'v1',
                'kind': 'Status',
                'metadata': {},
                'code': 500,
                'status': 'Failure',
                'reason': type(exc).__name__,
                'message': repr(exc),
                'details': {'traceback': traceback.format_exc()},
            }
        })
        await raw_response.write(error.encode() + b'\n')

    def _get_paths(self) -> Set[str]:
        paths: Set[str] = set()
        for payload in self._payloads:
            for filter in payload._walk(dsl.Filter):
                if isinstance(filter.criteria, filtering.Criteria):
                    if isinstance(filter.criteria.path, str):
                        paths.add(filter.criteria.path)
        return paths

    def _get_resources(self) -> Collection[Tuple[Optional[bool], resources.resource]]:
        """
        Reconstruct the supposed K8s resources served by this handler.

        The resources are retrieved from the predefined payloads,
        taking their namespaces and cluster-wide filters into account.

        Only the registered payloads are considered. And only the very specific
        resources — with group, version, and a plural name or 'any name'.
        Anything else is considered non-specific and thus non-discoverable.
        Extra fields (such as kind, categories, etc) are passed through.

        The reconstruction might be imprecise, it is the best effort approach.
        In case of need, use a stricter handler, such as `KubernetesApp`.
        """
        result: List[Tuple[Optional[bool], resources.resource]] = []
        for payload in self._payloads:
            res: List[resources.resource] = []
            clusterwide: Optional[bool] = None

            for filter in payload._walk(dsl.Filter):
                if isinstance(filter.criteria, filtering.Criteria):
                    if (resource := filter.criteria.resource) is not None:
                        if resource.group is not None and resource.version is not None:
                            name = resource.plural
                            if name is not None and name.lower() == name:
                                res.append(resource)
                    if filter.criteria.clusterwide is not None:
                        clusterwide = filter.criteria.clusterwide

            for resource in res:
                result.append((clusterwide, resource))
        return result

    def _walk_criteria(self) -> Iterator[filtering.Criteria]:
        # TODO: exclude duplicates, in case there are groups
        for payload in self._payloads:
            for filter in payload._walk(dsl.Filter):
                if isinstance(filter.criteria, filtering.Criteria):
                    yield filter.criteria

    async def _serve_root(self, request: rendering.Request) -> rendering.Payload:
        paths: Set[str] = {'/api', '/apis', '/version'}
        for _, resource in self._get_resources():
            if resource.group == '' and resource.version == 'v1':
                paths.add(f"/api/v1")
            elif resource.group is not None and resource.version is not None:
                paths.add(f"/apis/{resource.group}")
                paths.add(f"/apis/{resource.group}/{resource.version}")
        return {
            'paths': sorted(paths | self._get_paths()),
        }

    async def _serve_api(self, request: rendering.Request) -> rendering.Payload:
        return {'versions': ['v1']}

    async def _serve_apis(self, request: rendering.Request) -> rendering.Payload:
        resources = [resource for _, resource in self._get_resources()]
        groups = {
            group: {
                resource.version
                for resource in resources
                if resource.version is not None and resource.group == group
            }
            for group in {
                resource.group for resource in resources
                if resource.group is not None and resource.group != ''  # excluding the core v1
            }
        }
        return {
            'groups': [
                {
                    'name': group,
                    'preferredVersion': {  # TODO
                        'groupVersion': f'{group}/{list(versions)[0]}',
                        'version': list(versions)[0],
                    },
                    'versions': [
                        {
                            'groupVersion': f'{group}/{version}',
                            'version': version,
                        }
                        for version in versions
                    ],
                }
                for group, versions in groups.items()
            ],
        }

    async def _serve_server_version(self, request: rendering.Request) -> rendering.Payload:
        return {
            # TODO: make it configurable
            'major': '1',
            'minor': '26',
            'gitVersion': 'v1.26.4+k3s1',
            'gitCommit': '8d0255af07e95b841952563253d27b0d10bd72f0',
            'gitTreeState': 'clean',
            'buildDate': '2023-04-20T00:33:18Z',
            'goVersion': 'go1.19.8',
            'compiler': 'gc',
            'platform': 'linux/amd64'
        }

    async def _serve_group(self, request: rendering.Request) -> rendering.Payload:
        # e.g.: /apis/kopf.dev
        resources = [resource for _, resource in self._get_resources()]
        groups = {
            group: {
                resource.version for resource in resources
                if resource.group is not None and resource.version is not None
                if resource.group == group
            }
            for group in {resource.group for resource in resources}
            if group != ''  # excluding the core v1
        }
        group = request.resource.group
        versions = groups[group]
        return {
            'apiVersion': 'v1',  # of APIGroup, not of the served group
            'kind': 'APIGroup',
            'name': group,
            'preferredVersion':{  # TODO:
                'groupVersion': f'{group}/{list(versions)[0]}',
                'version': list(versions)[0],
            },
            'versions': [
                {
                    'groupVersion': f'{group}/{version}',
                    'version': version,
                }
                for version in versions
            ],
        }

    async def _serve_version(self, request: rendering.Request) -> rendering.Payload:
        # e.g.: /apis/kopf.dev/v1beta1
        info: Dict[str, Dict[str, Any]] = collections.defaultdict(dict)
        for clusterwide, resource in self._get_resources():
            # Only sufficiently specific resources and only for the requested group/version.
            plural = resource.plural
            if plural is None:
                continue
            if not request.resource.check(resource):
                continue

            # TODO: find the first specific kind/singular, do not overwrite always (it can be None)
            # TODO: find the most specific clusterwide (or both! ir can be both ==> error?)
            # info[plural]['kind'] = resource.kind
            # info[plural]['singularName'] = resource.singular
            # info[plural].setdefault('shortNames', set())
            # info[plural].setdefault('categories', set())
            info[plural].setdefault('subresources', set())
            # if resource.shortcut is not None:
            #     info[plural]['shortNames'].add(resource.shortcut)
            # if resource.category is not None:
            #     info[plural]['categories'].add(resource.category)
            # if resource.subresource is not None:  # TODO
            #     info[plural]['subresources'].add(resource.subresource)
            # if resource.verb is not None:# TODO: expose verbs somehow
            #     info[plural]['verbs'].add(resource.verb)
        return {
            'apiVersion': 'v1',  # of APIResourceList, not of the served group
            'kind': 'APIResourceList',
            'groupVersion': f'{request.resource.group}/{request.resource.version}',
            'resources': [
                {
                    'name': f'{plural}/{subresource}' if subresource else plural,
                    'namespaced': None if clusterwide is None else not clusterwide,
                    'kind': struct['kind'],
                    'singularName': struct['singularName'],
                    'shortNames': list(struct['shortNames']),
                    'categories': list(struct['categories']),
                    'verbs': list(struct['verbs']),
                }
                for plural, struct in info.items()
                for subresource in {''} | struct['subresources']
            ],
        }

    def _get_url(
            self,
            resource: resources.Selectable,
    ) -> str:
        parts: List[Optional[str]] = [
            '/api' if self.group == '' and self.version == 'v1' else '/apis',
            self.group,
            self.version,
            self.plural,
        ]
        return '/'.join([part for part in parts if part])


# TODO:
#   kmock.objects[res] -> ResourceView
#   kmock.objects[res, 'ns'] -> NamespaceView
#   kmock.objects[res, 'ns', 'n'] -> Dict/Object?
#   kmock.objects[:] = [...]                        replace all objects
#   kmock.objects[res] = [...]                   replace objects of one resource
#   kmock.objects[res, 'ns'] = [...]             replace objects of one resource-namespace
#   kmock.objects[..., 'ns'] = [...]                replace objects of one namespace?
#   del kmock.objects[res, 'ns', 'n']
#   del kmock.objects[res, 'ns']
#   del kmock.objects[res]
#   kmock.objects[..., 'ns']                        all objects of a namespace
#   kmock.objects[..., None]                        all clusterwide objects of any resource
#   kmock.objects[..., ..., 'n']                    all objects with a specific name, regardless of ns
#   kmock.objects[res, 'ns', 'n'] = Dict/Object     define a namespaced object
#   kmock.objects[res, 'n'] = Dict/Object           define a cluster object: mind not the namespace!
#  As sets, for assertions:
#   kmock.objects[res1] | kmock.objects[res2]       barely useful.
#   kmock.objects[res1] & kmock.objects[res2]       makes no sense! leads to an empty set in most cases
#   kmock.objects[res1] - kmock.objects['ns']       makes no sense! leads to an empty set in most cases
#   assert kmock.objects <= [obj1, obj2]            at least these two, maybe more
#   assert kmock.objects == [obj1, obj2]            precisely these two, nothing else (unordered!)
#  And VERSIONED
#   kmock.objects[res, 'ns', 'n'].versions[123]
#   kmock.objects[res, 'ns', 'n'].versions[-1]
#  => So, we now must make an ObjectsView, in addition to RequestsView

K = TypeVar('K', bound=Hashable)
V = TypeVar('V')


def patch_dict_recursively(value: Mapping[K, V], patch: Mapping[K, V], /) -> Mapping[K, V]:
    result = {}
    for key in patch:
        a: Optional[V] = value.get(key)
        b: Optional[V] = patch.get(key)
        if a is None and b is None:
            pass
        elif a is None:
            result[key] = b
        elif b is None:
            pass  # "a" does not go to the result
        elif isinstance(a, collections.abc.Mapping) and isinstance(b, collections.abc.Mapping):
            result[key] = patch_dict_recursively(a, b)
        elif isinstance(a, collections.abc.Mapping):
            raise ValueError(f"Cannot patch a dict by a scalar: {a!r} << {b!r}")
        elif isinstance(b, collections.abc.Mapping):
            raise ValueError(f"Cannot patch a scalar by a dict: {a!r} << {b!r}")
        else:
            result[key] = b  # overwrite the previous value
    return result


def match_dict_recursively(value: Mapping[K, V], pattern: Mapping[K, V], /) -> bool:
    required_keys = set(pattern)
    available_keys = set(value)
    if required_keys - available_keys:
        return False  # some required keys are missing
    for key in required_keys:
        a = value[key]
        b = pattern[key]
        if isinstance(a, collections.abc.Mapping) and isinstance(b, collections.abc.Mapping):
            if not match_dict_recursively(a, b):
                return False  # recursively missing keys
        elif b is Ellipsis:
            pass  # we already checked that the key exists
        elif a != b:
            return False  # mismatching types or unequal values
    return True


# TODO: ensure wrapping into this class in one of the following ways:
#       - either on demand, when accessed in .objects or .versions,
#         while keeping the actually stored data as dicts
#       - or immediately on storing the objects in __setitem__(),
#         and store them as such (enabled "a is b" comparison).
#   Currently, rae dicts are accepted and stored as dicts.
#   Change the type annotations to accept Dict[str, Any] where applicable without wrapping
#       (it was a type alias Object=Dict[str, Any] before converting to a class).
class Object(Dict[str, Any]):
    """
    A K8s object wrapper with extra syntax features for simpler/shorter tests.

    In the core, it is a dict, typically with the keys ``metadata``, ``spec``,
    and ``status``, but this is neither required nor guaranteed. For simplicity,
    it inherits from ``dict`` to pass all the ``isinstance()`` and type checks.

    Unlike the regular dict, the object has recursive partial pattern matching.
    I.e., the actual object may contain more fields that the pattern declares
    (typically, the metadata fields, names/namespaces, or resource versions),
    but those in the pattern are required and must store the declared values::

        assert kmock.objects[r, 'ns', 'n'] == {'spec': {'key': 'must be this'}}
        assert kmock.objects[r, 'ns', 'n'] != {'spec': {'key': 'anything else'}}

    The `...`` aka ``Ellipsis`` means "any value but the key must be present"
    (or "must be absent" with the negation)::

        assert kmock.objects[r, 'ns', 'n'] == {'spec': {'key': ...}}  # present
        assert kmock.objects[r, 'ns', 'n'] != {'spec': {'key': ...}}  # absent

    For strict dict-to-dict comparison, convert it to raw dicts explicitly::

        assert dict(kmock.objects[res, 'ns', 'n']) != {
            'metadata': {'name': 'n1', 'namespace': 'ns'},
            'spec': 'must be this',
        }

    Note that only the top-level objects/versions have this extended comparison.
    Accessing the keys of the data returns raw values and raw dicts, which are
    in turn compared by pure Python, i.e. with no recursive partial matching::

        assert kmock.objects[r, 'ns', 'n']['spec'] == {'key': 'must be this'}
        assert kmock.objects[r, 'ns', 'n']['spec']['key] == 'must be this'
    """
    __slots__ = ()

    # kmock.objects[res, 'ns', 'n', -1] == {'spec': …}
    # kmock.objects[res, 'ns', 'n'].versions[-1] == {'spec': …}
    def __eq__(self, pattern: Mapping[str, Any]) -> bool:
        return match_dict_recursively(self, pattern)

    # kmock.objects[res, 'ns', 'n', -1] != {'spec': …}
    # kmock.objects[res, 'ns', 'n'].versions[-1] != {'spec': …}
    def __ne__(self, pattern: Mapping[str, Any]) -> bool:
        return not match_dict_recursively(self, pattern)

    # kmock.objects[res, 'ns', 'n', -1].update({'spec': …})
    def update(
            self,
            changes: Union[Mapping[str, Any], Iterable[Tuple[str, Any]]] = (),
            /,
            **kwargs: Any,
    ) -> None:
        """
        Recursively update the object.

        For scalars, it is the same as native Python update (replacing).

        For dicts, it is a recursive merge (patching). This is so to prevent
        a dict value in the patch to replace the whole pre-existing dict
        in the base object instead of several keys in it::

            obj = Object({'spec': {'timeout': 60, 'interval': 10}})
            obj.update({'spec': {'interval': 15}})
            assert obj == {'spec': {'timeout': 60, 'interval': 15}}

        Note the preservance of ``timeout=60`` in this example,
        which would be lost with the native Python update.
        """
        patch = dict(changes, **kwargs)
        dict.update(self, patch_dict_recursively(self, patch))


@attrs.frozen(repr=False, eq=False, order=False)
class ObjectView(MutableMapping[str, Any]):
    """
    A view of a single object: ``kmock.objects[resource, namespace, name]``.

    * ``==`` & ``!=`` recursively compare against a partial dict pattern.
    * ``.history`` exposes the previous states of the object.
    * ``.patch(…)`` creates a new version with partial recursive changes.

    Accessing/modifying the view delegates to the latest version of the object.
    No history of modification is created on individual or mass changes of keys,
    e.g. with ``kmock.objects[…].update(…)`` — to make it easier to modify
    objects in place in tests without side effects.

    To emulate the history progression as in the API, call ``.patch(…)``.
    It provides the same signature and behaviour as ``.update(…)``,
    but also creates a new object version with an auto-generated version string.
    (The API's PATCH method internally uses this same method.)
    """

    # TODO: should it self-identify? Or should the identification come from outside where it is stored?
    # resource: resources.resource = attrs.field(kw_only=True)
    # namespace: Optional[str] = attrs.field(kw_only=True)
    # name: str = attrs.field(kw_only=True)

    # Reminder: the signatures are designed to refer by version names in addition to indexes.
    _history: List[Union[Object, None]] = attrs.field(factory=list, init=False)
    _counter: int = attrs.field(default=0, kw_only=True)

    def __repr__(self) -> str:
        return repr(self._history[-1])

    def __len__(self) -> int:
        return len(self._history[-1])

    def __iter__(self) -> Iterable[str]:
        return iter(self._history[-1])

    def __getitem__(self, key: str) -> Any:
        return self._history[-1][key]

    def __delitem__(self, key: str) -> Any:
        del self._history[-1][key]

    def __setitem__(self, key: str, val: Any) -> Any:
        self._history[-1][key] = val

    # kmock.objects[res, 'ns', 'n'] == {'spec': …}
    def __eq__(self, pattern: Mapping[str, Any]) -> bool:
        return match_dict_recursively(self._history[-1], pattern)

    # kmock.objects[res, 'ns', 'n'] != {'spec': …}
    def __ne__(self, pattern: Mapping[str, Any]) -> bool:
        return not match_dict_recursively(self._history[-1], pattern)

    def update(
            self,
            changes: Union[Mapping[str, Any], Iterable[Tuple[str, Any]]] = (),
            /,
            **kwargs: Any,
    ) -> None:
        """
        Recursively update the object without creating a new version.

        For scalars, it is the same as native Python update (replacing).
        For dicts, it is a recursive merge (patching). This is so to prevent
        a dict value in the patch to replace the whole pre-existing dict
        in the base object instead of several keys in it::

            obj = Object({'spec': {'timeout': 60, 'interval': 10}})
            obj.update({'spec': {'interval': 15}})
            assert obj == {'spec': {'timeout': 60, 'interval': 15}}

        Note the preservance of ``timeout=60`` in this example,
        which would be lost with the native Python update.
        """
        payload = self._history[-1]
        if payload is None:
            raise ValueError("Cannot update a deleted object (a deletion placeholder).")
        payload.update(changes, **kwargs)

    def patch(
            self,
            changes: Union[Mapping[str, Any], Iterable[Tuple[str, Any]]] = (),
            /,
            **kwargs: Any,
    ) -> None:
        """
        The same as ``.update(…)``, but creates a new version of the object.
        """
        self._history.append(Object(copy.deepcopy(self._history[-1])))
        self.update(changes, **kwargs)

    def delete(self) -> None:
        """
        Soft-delete the object by marking it as such but retaining the history.

        In contrast, ``del kmock.objects[…]`` physically deletes it from memory,
        while ``kmock.objects[…].deletes()`` keeps the object's history.
        The API emulator uses the soft-deletion internally.
        """
        self._history.append(None)


ObjectKey = Tuple[resources.resource, Optional[str], str]


# TODO: rename: ObjectSpace? as in "Space", the container pattern.
@attrs.frozen
class ObjectsView:
    """
    A container of objects.

    The following notations are supported with a 3-item key::

        kmock.objects[res, None, 'name']  # cluster-wide objects
        kmock.objects[res, 'namespace', 'name']  # namespaced objects

    The 4-item key is a shortcut for the ``.versions`` field of the object::

        kmock.objects[res, 'namespace', 'name', 0]  # the initial version
        kmock.objects[res, 'namespace', 'name', -2]  # the pre-last version
        kmock.objects[res, 'namespace', 'name', -1]  # the current version
        kmock.objects[res, 'namespace', 'name', 1:3]  # a slice of versions
        kmock.objects[res, 'namespace', 'name', :]  # a list of all versions

    There are 2 ways to delete the object:

    * ``del kmock.objects[res, 'ns', 'n']`` physically deletes it from memory.
    * ``kmock.objects[res, 'ns', 'n']`` soft-deletes the object.

    When the object is hard-deleted, a new object with the same name begins
    a new history starting with the version zero. The previous history is lost.

    When the object is soft-deleted, a special placeholder is put as the latest
    version. It does NOT compare to any dict anymore (always raises an error).
    However, it still has ``.versions`` to access the past states of the object.

    A new object with the same name continues the versioning with the new state.
    The following state of the object's history is possible
    (mind the ``<=`` & ``>=`` mean set-like "includes but may contain more")::

        POST /…/namespaces/ns/… ← {'spec': '1st', 'metadata': {'name': 'n1'}}
        PATCH /…/namespaces/ns/…/n1 ← {'spec': '1st modified'}
        DELETE /…/namespaces/ns/…/n1
        POST /…/namespaces/ns/… ← {'spec': '2nd', 'metadata': {'name': 'n1'}}

        assert len(kmock.objects[r, 'ns', 'n1', 0].versions) == 4
        assert kmock.objects[r, 'ns', 'n1', 0] >= {'spec': '1st'}
        assert kmock.objects[r, 'ns', 'n1', 1] >= {'spec': '1st modified'}
        assert kmock.objects[r, 'ns', 'n1', 2] is kmock.objects.DELETED
        assert kmock.objects[r, 'ns', 'n1', 3] >= {'spec': '2nd'}

    Objects tend to be sorted in chronological order with the same code flow,
    the same as it happens for usual Python dicts. But patching/modifying
    the existing objects can change their positioning relative to each other
    (mostly due to an implementation-specific decision to modify those objects
    in place or removing and re-appending them to the end).
    """
    _objects: Dict[ObjectKey, ObjectView] = attrs.field(factory=dict, init=False)

    @overload
    def __getitem__(self, _: Tuple[resources.resource, Optional[str], str], /) -> ObjectView:
        ...

    @overload
    def __getitem__(self, _: Tuple[resources.resource, Optional[str], str, int], /) -> Object:
        ...

    @overload
    def __getitem__(self, _: Tuple[resources.resource, Optional[str], str, slice], /) -> List[Object]:
        ...

    def __getitem__(self, key: Any, /) -> Union[ObjectView, Object, List[Object]]:
        if isinstance(key, tuple) and len(key) == 4 and isinstance(key[-1], (int, slice)):
            return list(self._objects[key[:-1]]._history)[key[-1]]
        elif isinstance(key, tuple) and len(key) == 3:
            return self._objects[key]
        raise LookupError(f"Unsupported filter for objects: {key!r}")

    def __delitem__(self, key: ObjectKey) -> None:
        if isinstance(key, tuple) and len(key) == 3:
            del self._objects[key]
        raise LookupError(f"Unsupported filter for objects: {key!r}")

    # TODO: value can be dict{}, or a list[Data] for a full history:
    #       kmock.objects[res, 'ns', 'n'] = {}
    #       kmock.objects[res, 'ns', 'n'] = [{}, {'spec': 123}]
    #       kmock.objects[res, 'ns', 'n'].patch({'spec': 123})
    def __setitem__(self, key: ObjectKey, value: ..., /) -> None:
        if isinstance(key, tuple) and len(key) == 4 and isinstance(key[-1], (int, slice)):
            self._objects[key[:-1]]._history[key[-1]] = value
        elif isinstance(key, tuple) and len(key) == 3:
            self._objects[key] = ObjectView()
            # TODO: do we patch or do we set? patching must be explicit, isn't it?
            #       python operations must all be in-memory.
            if isinstance(value, collections.abc.Mapping):
                self._objects[key].update(value)
            elif isinstance(value, collections.abc.Iterable):
                self[tuple(key) + (slice(None, None),)] = value
            else:
                raise ValueError(f"Unsupported value for object: {value!r}")

        else:
            raise LookupError(f"Unsupported filter for objects: {key!r}")

    # # TODO: but is it possible without metadata? i.e. we do not know which resource it is!
    # #       -> replace with: kmock.objects[res,ns,n] = obj1; so on…
    # # DSL: kmock.objects = [obj1, obj2, …] — without slicing/indexing.
    # def reset(self, objs: Iterable[...], /) -> None:
    #     self.clear()
    #     for obj in objs:
    #         resource = resources.resource(...)  # TODO?!
    #         name: Optional[str] = obj.get('metadata', {}).get('name')
    #         namespace: Optional[str] = obj.get('metadata', {}).get('namespace')
    #         key: ObjectKey = (resource, namespace, name)
    #         self[key] = obj


# @attrs.frozen
# class ResourceView(Collection[Data]):
#     _objects: Dict[ObjectKey, Data]
#     resource: Optional[resources.resource]
#
#     @overload
#     def __getitem__(self, _: Optional[str], /) -> "NamespaceView":
#         ...
#
#     @overload
#     def __getitem__(self, _: Tuple[Optional[str]], /) -> "NamespaceView":
#         ...
#
#     @overload
#     def __getitem__(self, _: Tuple[Optional[str], str], /) -> Data:
#         ...
#
#     def __getitem__(self, item):
#         if item is None:
#             return NamespaceView(self._objects, self.resource, None)
#         # if isinstance(item, slice):
#         #     return ResourceView(self._objects, None)
#         if isinstance(item, str):
#             return NamespaceView(self._objects, self.resource, None)
#         if isinstance(item, tuple) and item:
#             return self[item[0]][item[1:]]
#         raise LookupError(f"Unsupported filter for objects: {item!r}")


# @attrs.frozen(eq=False, order=False)
# class NamespaceView(AbstractSet[Data]):
#     _objects: Dict[ObjectKey, ObjectView]
#     resource: Optional[resources.resource]
#     namespace: Optional[str]
#
#     def __iter__(self) -> Iterator[Data]:
#         return (
#             obj
#             for resource, resource_objs in self._objects.items()
#             for namespace, namespace_objs in resource_objs.items()
#             for name, obj in namespace_objs.items()
#             if self.resource is None or self.resource == resource
#             if self.namespace == namespace
#             # if self.name == name
#         )
#
#     @overload
#     def __getitem__(self, _: str, /) -> Data:
#         ...
#
#     @overload
#     def __getitem__(self, _: int, /) -> Data:
#         ...
#
#     # @overload
#     # def __getitem__(self, _: slice, /) -> Collection[Object]:
#     #     ...
#
#     def __getitem__(self, item):
#         if isinstance(item, int):
#             objects = list(self)
#             return objects[item]
#         if isinstance(item, str):
#             # return self._objects[self.resource][self.namespace][self.name]
#             # return NameView(self._objects, self.resource, self.namespace, item)
#             return self._objects[self.resource][self.namespace][self.name]
#         if isinstance(item, tuple) and item:
#             return self[item[0]][item[1:]]
#         raise LookupError(f"Unsupported filter for objects: {item!r}")
#
#     # TODO: also implement set-like <,>,<=,>=,&,|,-?
#     def __eq__(self, other) -> bool:
#         # Unordered comparison: as for sets, but without hashing unhashable dicts.
#         # Technically:
#         # - every object of self is present in other;
#         # - every object of other is present in self;
#         # - no extras on either side
#         a_objs = list(self)
#         b_objs = list(other)
#         a_in_b = all(any(b_obj == a_obj for b_obj in b_objs) for a_obj in a_objs)
#         b_in_a = all(any(b_obj == a_obj for a_obj in a_objs) for b_obj in b_objs)
#         a_extras = any(all(b_obj != a_obj for b_obj in b_objs) for a_obj in a_objs)
#         b_extras = any(all(b_obj != a_obj for a_obj in a_objs) for b_obj in b_objs)
#         return a_in_b and b_in_a and not a_extras and not b_extras
#
#     def __ne__(self, other) -> bool:
#         return not(self.__eq__(other))
#
#     def __le__(self, other) -> bool:  # self is a subset of other, or equal
#         a_objs = list(self)
#         b_objs = list(other)
#         a_in_b = all(any(b_obj == a_obj for b_obj in b_objs) for a_obj in a_objs)
#         b_in_a = all(any(b_obj == a_obj for a_obj in a_objs) for b_obj in b_objs)
#         a_extras = any(all(b_obj != a_obj for b_obj in b_objs) for a_obj in a_objs)
#         b_extras = any(all(b_obj != a_obj for a_obj in a_objs) for b_obj in b_objs)
#         return a_in_b and not a_extras
#
#     def __ge__(self, other) -> bool:  # other is a subset of self, or equal
#         a_objs = list(self)
#         b_objs = list(other)
#         a_in_b = all(any(b_obj == a_obj for b_obj in b_objs) for a_obj in a_objs)
#         b_in_a = all(any(b_obj == a_obj for a_obj in a_objs) for b_obj in b_objs)
#         a_extras = any(all(b_obj != a_obj for b_obj in b_objs) for a_obj in a_objs)
#         b_extras = any(all(b_obj != a_obj for a_obj in a_objs) for b_obj in b_objs)
#         return b_in_a and not b_extras
#
#     def __lt__(self, other) -> bool:  # self is a subset of other, but not equal
#         a_objs = list(self)
#         b_objs = list(other)
#         a_in_b = all(any(b_obj == a_obj for b_obj in b_objs) for a_obj in a_objs)
#         b_in_a = all(any(b_obj == a_obj for a_obj in a_objs) for b_obj in b_objs)
#         a_extras = any(all(b_obj != a_obj for b_obj in b_objs) for a_obj in a_objs)
#         b_extras = any(all(b_obj != a_obj for a_obj in a_objs) for b_obj in b_objs)
#         return a_in_b and not a_extras and b_extras
#
#     def __gt__(self, other) -> bool:  # other is a subset of self, but not equal
#         a_objs = list(self)
#         b_objs = list(other)
#         a_in_b = all(any(b_obj == a_obj for b_obj in b_objs) for a_obj in a_objs)
#         b_in_a = all(any(b_obj == a_obj for a_obj in a_objs) for b_obj in b_objs)
#         a_extras = any(all(b_obj != a_obj for b_obj in b_objs) for a_obj in a_objs)
#         b_extras = any(all(b_obj != a_obj for a_obj in a_objs) for b_obj in b_objs)
#         return b_in_a and not b_extras and a_extras
#
#     def __or__(self, other) -> Collection[Data]:
#         a_objs = list(self)
#         b_objs = list(other)
#         return a_objs + [b_obj for b_obj in b_objs if all(a_obj != b_obj for a_obj in a_objs)]
#
#     def __and__(self, other) -> Collection[Data]:
#         a_objs = list(self)
#         b_objs = list(other)
#         return [a_obj for a_obj in a_objs if any(b_obj == a_obj for b_obj in b_objs)]
#
#     def __sub__(self, other) -> Collection[Data]:
#         a_objs = list(self)
#         b_objs = list(other)
#         return [a_obj for a_obj in a_objs if all(b_obj != a_obj for b_obj in b_objs)]


# TODO: remove! replaced by ObjectView
# @attrs.frozen
# class NameView(Collection[Data]):
#     _objects: Dict[ObjectKey, Data]
#     resource: resources.resource
#     namespace: Optional[str]
#     name: str


@attrs.define(kw_only=True)
class KubernetesEmulator(KubernetesScaffold):
    """
    A server that mimics Kubernetes and tracks the state of objects in memory.

    Object creation, patching, and deletion are tracked. The operations emulate
    the behaviour of a realistic Kubernetes server, but very simplistically.
    The server then serves these objects on listings, watch-streams, fetching.
    It is essentially an in-memory-database-over-http.

    However, unlike the real Kubernetes server, this emulator only modifies
    the objects as simple JSON structures: merge the dicts, overwrite the keys.
    There is no special treatment of "special" fields, e.g. lists where
    the new values are added/merged instead of overwriting the whole dict key.
    If you need 'special' field treament, inherit and implement for your cases.

    All objects are available for assertions in the ``kmock.objects`` field
    (in addition to the inherited ``kmock.requests`` and others).

    Note: the object tracking happens even if there are reactions that catch
    the creation/update/deletion operations. However, the objects are shown
    only in the default handlers, i.e. when the fetching/listing/watching
    requests are not intercepted (because those will return their content).

    .. seealso::
        Simulator vs. emulator: https://stackoverflow.com/a/1584701/857383
    """

    # The accessible/modifiable container of all objects stored in memory (unordered).
    objects: ObjectsView = attrs.field(factory=ObjectsView, init=False)

    _lock = attrs.field(factory=asyncio.Lock, init=False)
    _buses: Dict[resources.resource, aiobus.Bus] = attrs.field(factory=lambda: collections.defaultdict(aiobus.Bus))

    def __attrs_post_init__(self) -> None:
        # If there is no specific user instruction found, serve the implicit logic as a K8s server.
        # Generally, these are empty/dummy responses with conventional structure, but overrideable.
        # TODO: can EVERYTHING be a filter per se? Not as a marker/enum, but simply a specially defined instance.
        #  We do not have @kopf.on() here, which does not accept positional selectors (yet).
        self.fallback[enums.action.LIST] << self._serve_list
        self.fallback[enums.action.WATCH] << self._serve_watch
        self.fallback[enums.action.FETCH] << self._serve_fetch
        self.fallback[enums.action.CREATE] << self._serve_create
        self.fallback[enums.action.UPDATE] << self._serve_update
        self.fallback[enums.action.DELETE] << self._serve_delete

    @override
    async def _handle(self, request: rendering.Request) -> aiohttp.web.StreamResponse:
        # Silently serve object-modifying requests even if intercepted by user-defined reactions.
        # These objects must be available for assertions and implicit (fallback) reading requests.
        if request.resource is not None:
            async with self._lock:
                object_key = None
                if request.action == enums.action.CREATE:
                    obj = request.data
                    object_name = obj.get('metadata', {}).get('name')
                    object_namespace = obj.get('metadata', {}).get('namespace')
                    object_key = (request.resource, request.namespace or object_namespace, object_name)
                    if object_key not in self.objects:
                        self.objects[object_key] = obj
                        await self._buses[request.resource].put({'type': 'ADDED', 'object': obj})
                    # TODO: else: 409 already exists?
                elif request.action == enums.action.DELETE:
                    object_key = (request.resource, request.namespace, request.name)
                    # TODO: both the stream & the response must contain the implicit metadata-fields:
                    #           name, namespace, resourceVersion, apiVersion, kind.
                    if object_key in self.objects:
                        obj = self.objects[object_key]
                        now = datetime.datetime.utcnow().isoformat()
                        obj.get('metadata', {}).setdefault('deletionTimestamp', now)
                        await self._buses[request.resource].put({'type': 'MODIFIED', 'object': obj})
                elif request.action == enums.action.UPDATE:
                    object_key = (request.resource, request.namespace, request.name)
                    # TODO: both the stream & the response must contain the implicit metadata-fields:
                    #           name, namespace, resourceVersion, apiVersion, kind.
                    if object_key in self.objects:
                        obj = self._apply_patch(self.objects[object_key], request.data)
                        self.objects[object_key] = obj
                        await self._buses[request.resource].put({'type': 'MODIFIED', 'object': obj})

                # TODO: both the stream & the response must contain the implicit metadata-fields:
                #           name, namespace, resourceVersion, apiVersion, kind.
                if object_key is not None and object_key in self.objects:
                    obj = self.objects[object_key]
                    meta = obj.get('metadata', {})
                    if meta.get('deletionTimestamp') and not meta.get('finalizers', []):
                        del self.objects[object_key]
                        await self._buses[request.resource].put({'type': 'DELETED', 'object': obj})

        return await super()._handle(request)

    async def _serve_list(self, request: rendering.Request) -> rendering.Payload:
        # TODO: see test_empty_stream_yields_nothing():
        #   when a watch reaction is added, the list request is still made.
        #   but without the explicit list reaction, we get 404.
        #   we should somehow handle this for k8s-specific watches, but not for generic streams.
        items: list[...] = []
        async with self._lock:
            for (resource, namespace, name), obj in self.objects.items():
                if resource == request.resource and (request.clusterwide or namespace == request.namespace)\
                        and (request.name is None or name == request.name):
                    # TODO: the response must contain the implicit metadata-fields:
                    #           name, namespace, resourceVersion, apiVersion, kind.
                    items.append(obj)
        return {
            # TODO: kind=? version=?
            'metadata': {'resourceVersion': '...'},
            'items': items,
        }

    async def _serve_watch(self, request: rendering.Request) -> rendering.Payload:
        # TODO:  We can send 410s by default for absent watch-feeds, or we can wait for a bus events.
        #       The TrackingServer definitely could have the latter, sometimes, not always.
        #       But the base Kubernetes server will NEVER get anything on the bus.
        #       So, it gets stuck in waiting for nothing forever.
        #       If we yield 410 here, the contnuous_watcher terminates, this is good.
        #       But in that case, we kill the tracking/blocking capabilities.
        #       ❓ How to keep them both with minimal changes and boilerplate code to the tests?
        # # If there are no non-depleted (i.e. ready) streams left, simulate a stream with 410 'Gone'.
        # yield 410
        # return
        events: List[Any] = []
        async with self._lock:
            for (resource, namespace, name), obj in self.objects.items():
                if resource == request.resource and (request.clusterwide or namespace == request.namespace)\
                        and (request.name is None or name == request.name):
                    events.append({'type': 'ADDED', 'object': obj})

        async with self._buses[request.resource] as bus_stream:
            # Instantly stream all existing objects while holding the stream mark.
            yield events

            # Then stream the bookmarked bus as soon as the events arrive or until cancelled.
            async for event in bus_stream:
                resource = request.resource
                namespace = event.get('object', {}).get('metadata', {}).get('namespace')
                name = event.get('object', {}).get('metadata', {}).get('name')
                if resource == request.resource and (request.clusterwide or namespace == request.namespace)\
                        and (request.name is None or name == request.name):
                    yield event

    async def _serve_fetch(self, request: rendering.Request) -> rendering.Payload:
        # TODO: a separate type for objects, though allowing any payload (maybe restrict to dicts)
        items: List[Object] = []
        async with self._lock:
            for (resource, namespace, name), obj in self.objects.items():
                if resource == request.resource and (request.clusterwide or namespace == request.namespace)\
                        and (request.name is None or name == request.name):
                    items.append(dict(obj))
        if len(items) > 1:
            raise RuntimeError('More than one object matches the request. This should not happen.')

        return items[0] if items else rendering.Response(status=404)
        # return items[0] if items else 404  #TODO: make it explicit!

    async def _serve_create(self, request: rendering.Request) -> rendering.Payload:
        return await self._serve_fetch(request)

    async def _serve_update(self, request: rendering.Request) -> rendering.Payload:
        return await self._serve_fetch(request)

    async def _serve_delete(self, request: rendering.Request) -> rendering.Payload:
        # TODO: it must return the last seen state of the resource, but it is absent to now,
        #       since it is actually remove in the tracking _handle() routine.
        return {}

    def _apply_patch(self, base: Mapping[str, Any], patch: Mapping[str, Any]) -> Mapping[str, Any]:
        result = dict(base)
        for key, val in patch.items():
            if val is None:
                if key in result:
                    del result[key]
            elif key not in result:
                result[key] = val
            elif isinstance(val, collections.abc.Mapping) and isinstance(result[key], collections.abc.Mapping):
                result[key] = self._apply_patch(result[key], val)
            else:
                # E.g. dict-over-list or list-over-dict — but we overwrite for simplicity.
                result[key] = val
        return result
