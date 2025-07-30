import urllib.parse
from typing import List, Mapping, Optional, Tuple

import attrs
from typing_extensions import Self

from kmock import enums, resources


@attrs.frozen
class ParsedHTTP:
    """
    Try to parse a string that looks ike a typical HTTP request.

    E.g.: `get /path?q=query`.
    """
    method: Optional[enums.method]
    path: Optional[str]
    params: Optional[Mapping[str, str]]

    @classmethod
    def parse(cls, s: str) -> Optional[Self]:
        maybe_method, *parts = s.split(maxsplit=1)
        method = enums.method(maybe_method)
        method = method if method in enums.method else None  # ignore unknown methods!
        s = s if method is None else parts[0] if parts else ''

        # Skip the k8s-like case: "delete pods", but catch as http in "delete /pods".
        parsed = urllib.parse.urlparse(s.strip())
        if parsed.path and not parsed.path.startswith('/'):
            return None

        path = parsed.path or None
        query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True) or None
        params = dict(query) if query else None
        if method is None and path is None and params is None:
            return None

        return cls(method, path, params)


@attrs.frozen
class ParsedK8s:
    action: Optional[enums.action]
    resource: Optional[resources.resource]

    @classmethod
    def parse(cls, s: str) -> Optional[Self]:
        maybe_action, *parts = s.split(maxsplit=1)
        try:
            action = enums.action(maybe_action)
        except ValueError:
            action = None
        action = action if isinstance(action, enums.action) else None  # ignore unknown actions!
        s = s if action is None else parts[0] if parts else ''

        try:
            resource = resources.resource(s)
            resource = None if resource.group is None and resource.version is None and resource.plural is None else resource
        except TypeError:
            resource = None
        if action is None and resource is None:
            return None

        return cls(action, resource)


@attrs.frozen
class ParsedPath:
    group: Optional[str] = None
    version: Optional[str] = None
    plural: Optional[str] = None
    namespace: Optional[str] = None
    name: Optional[str] = None
    subresource: Optional[str] = None


def parse_path(path: str) -> ParsedPath:
    parts: List[Optional[str]] = path.strip('/').split('/')

    # TODO: cover this with good tests with all combinations.
    if len(parts) >= 2 and parts[0] == 'apis':
        _, group, version, *parts = parts + [None]
    elif len(parts) >= 2 and parts[0] == 'api':
        group = ''
        _, version, *parts = parts + [None]
    else:
        group = version = None
        parts = parts + [None]
    parts = parts[:-1]  # if the filler was added but not used for versions

    if group is not None:  # is it k8s-related at all?
        _, namespace, *parts = parts if parts and parts[0] == 'namespaces' else [None, None] + parts
        plural, *parts = parts if parts else [None]
        name, *parts = parts if parts else [None]
        subresource = '/'.join(parts) or None
    else:
        plural = namespace = name = subresource = None
    return ParsedPath(group, version, plural, namespace, name, subresource)


def guess_http(s: str) -> Tuple[Optional[enums.method], Optional[str], Optional[Mapping[str, str]]]:
    """
    Try to parse a string that looks ike a typical HTTP request.

    E.g.: `get /path?q=query`.
    """
    maybe_method, *parts = s.split(maxsplit=1)
    method = enums.method(maybe_method)
    method = method if method in enums.method else None

    s = s if method is None else parts[0] if parts else ''
    parsed = urllib.parse.urlparse(s.strip())
    path = parsed.path if parsed.path.startswith('/') else None
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True) or None
    params = dict(query) if query else None
    return method, path, params


def guess_k8s(k8s: ParsedPath, method: enums.method, query: Mapping[str, str]) -> Optional[enums.action]:
    if k8s.group is None:  # non-k8s requests have no k8s action by definition
        return None

    if method == enums.method.GET and query.get('watch') == 'true':
        action = enums.action.WATCH  # both for lists & named resources
    elif k8s.name is None:
        action = (
            enums.action.LIST if method == enums.method.GET else
            enums.action.CREATE if method == enums.method.POST else
            None  # not guessed, but continuing (not an error)
        )
    else:
        action = (
            enums.action.FETCH if method == enums.method.GET else
            enums.action.UPDATE if method == enums.method.PATCH else
            enums.action.DELETE if method == enums.method.DELETE else
            None  # not guessed, but continuing (not an error)
        )
    return action


def are_all_known_headers(arg: Mapping[str, str]) -> bool:
    known_headers = {key.lower() for key in KNOWN_HEADERS}
    return arg and all(key.lower().startswith('x-') or key.lower() in known_headers for key in arg)


# Only those that are distinguished headers and rarely (if ever) can be regular JSON dict keys.
# As a rule of thumb, multi-word headers are fine; if single-word, then only verbs, not nouns.
# Many more can be found at https://en.wikipedia.org/wiki/List_of_HTTP_header_fields
KNOWN_HEADERS = {
    'Accept',
    'Accept-CH',
    'Accept-Charset',
    'Accept-Datetime',
    'Accept-Encoding',
    'Accept-Language',
    'Accept-Patch',
    'Accept-Ranges',
    'Authorization',  # as an exception, the very common one
    'Cache-Control',
    'Content-Disposition',
    'Content-Encoding',
    'Content-Language',
    'Content-Length',
    'Content-Location',
    'Content-MD5',
    'Content-Range',
    'Content-Security-Policy',
    'Content-Transfer-Encoding',
    'Content-Type',
    'ETag',
    'Expires',
    'If-Match',
    'If-Modified-Since',
    'If-None-Match',
    'If-Range',
    'If-Unmodified-Since',
    'Last-Modified',
    'Location',  # as an exception, the very common one
    'Proxy-Authenticate',
    'Proxy-Authorization',
    'Proxy-Connection',
    'Refresh',
    'Retry-After',
    'Set-Cookie',
    'Transfer-Encoding',
    'User-Agent',
    'WWW-Authenticate',
}
