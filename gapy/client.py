from apiclient.discovery import build
import httplib2
from oauth2client.client import SignedJwtAssertionCredentials, flow_from_clientsecrets, \
    OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from gapy.response import ManagementResponse, QueryResponse
from gapy.error import GapyError

GOOGLE_API_SCOPE = "https://www.googleapis.com/auth/analytics"
GOOGLE_API_SCOPE_READONLY = "https://www.googleapis.com/auth/analytics.readonly"
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"


def _get_storage(storage, storage_path):
    if not storage:
        if not storage_path:
            raise GapyError(
                "Must provide either a storage object or a storage_path")
        storage = Storage(filename=storage_path)
    return storage


def from_private_key(account_name, private_key=None, private_key_path=None,
                     storage=None, storage_path=None, api_version="v3",
                     readonly=False, http_client=None, ga_hook=None):
    """Create a client for a service account.

    Create a client with an account name and a private key.

     Args:
      account_name: str, the account identifier (probably the account email).
      private_key: str, the private key as a string.
      private_key_path: str, path to a file with the private key in.
      storage: oauth2client.client.Storage, a Storage implementation to store
               credentials.
      storage_path: str, path to a file storage.
      readonly: bool, default False, if True only readonly access is requested
                from GA.
      http_client: httplib2.Http, Override the default http client used.
      ga_hook: function, a hook that is called every time a query is made
               against GA.
    """
    if not private_key:
        if not private_key_path:
            raise GapyError(
                "Must provide either a private_key or a private_key_file")
        if isinstance(private_key_path, basestring):
            private_key_path = open(private_key_path)
        private_key = private_key_path.read()

    storage = _get_storage(storage, storage_path)

    scope = GOOGLE_API_SCOPE_READONLY if readonly else GOOGLE_API_SCOPE
    credentials = SignedJwtAssertionCredentials(account_name, private_key,
                                                scope)
    credentials.set_store(storage)

    return Client(_build(credentials, api_version, http_client), ga_hook)


def from_secrets_file(client_secrets, storage=None, storage_path=None,
                      api_version="v3", readonly=False, http_client=None,
                      ga_hook=None):
    """Create a client for a web or installed application.

    Create a client with a client secrets file.

    Args:
        client_secrets: str, path to the client secrets file (downloadable from
                             Google API Console)
      storage: oauth2client.client.Storage, a Storage implementation to store
               credentials.
      storage_path: str, path to a file storage.
      readonly: bool, default False, if True only readonly access is requested
                from GA.
      http_client: httplib2.Http, Override the default http client used.
      ga_hook: function, a hook that is called every time a query is made
               against GA.
    """
    scope = GOOGLE_API_SCOPE_READONLY if readonly else GOOGLE_API_SCOPE
    flow = flow_from_clientsecrets(client_secrets,
                                   scope=scope)
    storage = _get_storage(storage, storage_path)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return Client(_build(credentials, api_version, http_client), ga_hook)


def from_credentials_db(client_secrets, storage, api_version="v3",
                        readonly=False, http_client=None, ga_hook=None):
    """Create a client for a web or installed application.

    Create a client with a credentials stored in stagecraft db.

    Args:
        client_secrets: dict, client secrets (downloadable from
                             Google API Console)
      storage: stagecraft.apps.collectors.libs.ga.CredentialStorage,
               a Storage implementation to store credentials.
      readonly: bool, default False, if True only readonly access is requested
                from GA.
      http_client: httplib2.Http, Override the default http client used.
      ga_hook: function, a hook that is called every time a query is made
               against GA.
    """
    scope = GOOGLE_API_SCOPE_READONLY if readonly else GOOGLE_API_SCOPE
    flow = OAuth2WebServerFlow(
        client_secrets.get('client_id'),
        client_secrets.get('client_secret'),
        scope,
        redirect_uri=client_secrets.get('redirect_uri'),
        user_agent=client_secrets.get('user_agent', None),
        auth_uri=client_secrets.get('auth_uri'),
        token_uri=client_secrets.get('token_uri'))

    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return Client(_build(credentials, api_version, http_client), ga_hook)


def _build(credentials, api_version, http_client=None):
    """Build the client object."""
    if not http_client:
        http_client = httplib2.Http()

    authorised_client = credentials.authorize(http_client)

    return build("analytics", api_version, http=authorised_client)


class Client(object):

    def __init__(self, service, ga_hook=None):
        self._service = service
        self._ga_hook = ga_hook

    @property
    def management(self):
        return ManagementClient(self._service)

    @property
    def query(self):
        return QueryClient(self._service, self._ga_hook)


class ManagementClient(object):

    def __init__(self, service):
        self._service = service

    def accounts(self):
        return self._list("accounts")

    def account(self, id):
        return self._item(self.accounts(), id)

    def webproperties(self, account):
        return self._list("webproperties", accountId=account)

    def webproperty(self, account, id):
        return self._item(self.webproperties(account), id)

    def profiles(self, account, webproperty):
        return self._list("profiles", accountId=account,
                          webPropertyId=webproperty)

    def profile(self, account, webproperty, id):
        return self._item(self.profiles(account, webproperty), id)

    def segments(self):
        return self._list("segments")

    def _list(self, name, **kwargs):
        return ManagementResponse(
            getattr(self._service.management(), name)().list(
                **kwargs).execute()
        )

    def _item(self, response, id):
        for item in response:
            if item["id"] == id:
                return item
        raise GapyError("Id not found")


class QueryClient(object):

    def __init__(self, service, ga_hook=None):
        self._service = service
        self._ga_hook = ga_hook or (lambda kwargs: None)

    def _to_list(self, value):
        """Turn an argument into a list"""
        if value is None:
            return []
        elif isinstance(value, list):
            return value
        else:
            return [value]

    def _to_ga_param(self, values):
        """Turn a list of values into a GA list parameter"""
        return ','.join(map(_prefix_ga, values))

    def get(self, ids, start_date, end_date, metrics,
            dimensions=None, filters=None,
            max_results=None, sort=None, segment=None):
        ids = self._to_list(ids)
        metrics = self._to_list(metrics)

        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")

        dimensions = self._to_list(dimensions)
        filters = self._to_list(filters)

        sort = self._to_list(sort)

        return self._get_response(
            metrics, dimensions,
            ids=self._to_ga_param(ids),
            start_date=start_date,
            end_date=end_date,
            metrics=self._to_ga_param(metrics),
            dimensions=self._to_ga_param(dimensions) or None,
            filters=self._to_ga_param(filters) or None,
            sort=self._to_ga_param(sort) or None,
            max_results=max_results,
            segment=segment
        )

    def _filter_empty(self, kwargs, key):
        if key in kwargs and kwargs[key] is None:
            del kwargs[key]
        return kwargs

    def get_raw_response(self, **kwargs):
        self._ga_hook(kwargs)
        # Remove specific keyword arguments if they are `None`
        for arg in "dimensions filters sort max_results segment".split():
            kwargs = self._filter_empty(kwargs, arg)
        return self._service.data().ga().get(**kwargs).execute()

    def _get_response(self, m, d, **kwargs):
        return QueryResponse(
            self,
            self.get_raw_response(**kwargs),
            m, d,
            max_results=kwargs.get("max_results", None),
        )


def _prefix_ga(value):
    """Prefix a string with 'ga:' if it is not already

    Sort values may be prefixed with '-' to indicate negative sort.

    >>> _prefix_ga('foo')
    'ga:foo'
    >>> _prefix_ga('ga:foo')
    'ga:foo'
    >>> _prefix_ga('-foo')
    '-ga:foo'
    >>> _prefix_ga('-ga:foo')
    '-ga:foo'
    """
    prefix = ''
    if value[0] == '-':
        value = value[1:]
        prefix = '-'
    if not value.startswith('ga:'):
        prefix += 'ga:'
    return prefix + value
