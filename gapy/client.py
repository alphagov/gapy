from apiclient.discovery import build
import httplib2
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.file import Storage

from gapy.response import ManagementResponse, QueryResponse
from gapy.error import GapyError

GOOGLE_API_SCOPE = "https://www.googleapis.com/auth/analytics"

def service_account(account_name, private_key=None, private_key_path=None, storage=None, storage_path=None):
  """Create a client for a service account.

   Args:
    account_name: str, the account identifier (probably the account email).
    private_key: str, the private key as a string.
    private_key_path: str, path to a file with the private key in.
    storage: oauth2client.client.Storage, a Storage implementation to store credentials.
    storage_path: str, path to a file storage.
  """
  if not private_key:
    if not private_key_path:
      raise GapyError("Must provide either a private_key or a private_key_file")
    if isinstance(private_key_path, basestring):
      private_key_path = open(private_key_path)
    private_key = private_key_path.read()

  if not storage:
    if not storage_path:
      raise GapyError("Must provide either a storage object or a storage_path")
    storage = Storage(filename=storage_path)

  credentials = SignedJwtAssertionCredentials(account_name, private_key, GOOGLE_API_SCOPE)
  credentials.set_store(storage)

  http = httplib2.Http()
  http = credentials.authorize(http)

  return Client(_build(http))

def _build(http):
  """Build the client object."""
  return build("analytics", "v3", http=http)

class Client(object):
  def __init__(self, service):
    self._service = service

  @property
  def management(self):
    return ManagementClient(self._service)

  @property
  def query(self):
    return QueryClient(self._service)

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
    return self._list("profiles", accountId=account, webPropertyId=webproperty)

  def profile(self, account, webproperty, id):
    return self._item(self.profiles(account, webproperty), id)

  def _list(self, name, **kwargs):
    return ManagementResponse(
      getattr(self._service.management(), name)().list(**kwargs).execute()
    )

  def _item(self, response, id):
    for item in response:
      if item["id"] == id:
        return item
    raise GapyError("Id not found")

class QueryClient(object):
  def __init__(self, service):
    self._service = service

  def get(self, ids, start_date, end_date, metrics, dimensions=None):
    if not isinstance(ids, list):
      ids = [ids]
    if not isinstance(metrics, list):
      metrics = [metrics]
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    if dimensions:
      if not isinstance(dimensions, list):
        dimensions = [dimensions]
    else:
      dimensions = []

    return self._get_response(metrics, dimensions,
      ids=",".join("ga:%s" % id for id in ids),
      start_date=start_date,
      end_date=end_date,
      metrics=",".join("ga:%s" % metric for metric in metrics),
      dimensions=",".join("ga:%s" % dimension for dimension in dimensions)
    )

  def get_raw_response(self, **kwargs):
    return self._service.data().ga().get(**kwargs).execute()

  def _get_response(self, m, d, **kwargs):
    return QueryResponse(
      self,
      self.get_raw_response(**kwargs),
      m, d
    )
