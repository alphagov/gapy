from gapy.response import ManagementResponse, QueryResponse
from gapy.error import GapyError

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
