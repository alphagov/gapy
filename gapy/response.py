from datetime import datetime
import urlparse


def parse_ga_url(url):
    escape_semicolons = url.replace(";", "%3B")
    query = urlparse.parse_qsl(
        urlparse.urlparse(escape_semicolons).query)
    return dict(
        (key.replace("-", "_"), values) for key, values in query)


class BaseResponse(object):
    def __init__(self, response):
        self._response = response

    def data(self):
        return self._response

    def __getattr__(self, key):
        return self._response[key]


class ManagementResponse(BaseResponse):
    def __iter__(self):
        for item in self._response["items"]:
            yield item


class QueryResponse(BaseResponse):
    def __init__(self, service, response, metrics, dimensions):
        super(QueryResponse, self).__init__(response)
        self._service = service
        self._metrics = metrics
        self._dimensions = dimensions

    def __len__(self):
        return len(self._response.get("rows", []))

    def __iter__(self):
        while True:
            for row in self._response.get("rows", []):
                result = {
                    "metrics": dict(
                        zip(self._metrics, row[len(self._dimensions):])),
                    "start_date": datetime.strptime(
                        self._response["query"]["start-date"],
                        "%Y-%m-%d").date(),
                    "end_date": datetime.strptime(
                        self._response["query"]["end-date"], "%Y-%m-%d").date()
                }
                if self._dimensions:
                    result["dimensions"] = dict(
                        zip(self._dimensions, row[:len(self._dimensions)]))
                    self._add_datetime(result["dimensions"])
                yield result
            if self._response.get("nextLink"):
                next_kwargs = parse_ga_url(self._response.get("nextLink"))
                self._response = self._service.get_raw_response(**next_kwargs)
            else:
                break

    def _add_datetime(self, dimensions):
        if "date" in dimensions:
            if "hour" in dimensions:
                dimensions["datetime"] = datetime.strptime(
                    dimensions["date"] + dimensions["hour"], "%Y%m%d%H")
            else:
                dimensions["datetime"] = datetime.strptime(dimensions["date"],
                                                           "%Y%m%d")
