from apiclient.discovery import build
from gapy.error import GapyError
import httplib2
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.file import Storage

from gapy.client import Client

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
