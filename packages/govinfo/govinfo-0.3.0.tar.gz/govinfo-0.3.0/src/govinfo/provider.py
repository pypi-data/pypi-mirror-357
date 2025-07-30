from json import JSONDecodeError

import httpx

from govinfo.config import BASE_URL, KEYS, OFFSET_DEFAULT, PAGE_DEFAULT
from govinfo.exceptions import GovInfoException
from govinfo.models import Collection, Granule, Package


class GovInfoProvider:
    def __init__(self, api_key, transport):
        self._url = f"{BASE_URL}"
        self._api_key = api_key
        self._params = {
            "offsetMark": OFFSET_DEFAULT,
            "pageSize": PAGE_DEFAULT,
        }
        self._transport = transport

    def _get_list(self, endpoint, **kwargs):
        try:
            yield from self._call_endpoint(
                endpoint=endpoint,
                **kwargs,
            )
        except GovInfoException as e:
            raise e

    def _get(self, endpoint: str):
        headers = {"x-api-key": self._api_key}
        with httpx.Client(headers=headers, transport=self._transport) as client:
            response = client.get(
                "/".join((self._url, self._path)), params=self._params
            )
            try:
                payload = response.json()
            except (ValueError, JSONDecodeError) as e:
                raise GovInfoException("Bad JSON in response") from e
            if response.status_code == 200:
                if endpoint is None:
                    yield payload
                else:
                    payload_key = self._set_payload_key(endpoint, self._path)
                    for item in payload[payload_key]:
                        yield item
                    while next_page := payload.get("nextPage"):
                        response = client.get(next_page)
                        payload = response.json()
                        for item in payload[payload_key]:
                            yield item
            else:
                raise GovInfoException(
                    f"{response.status_code}: {response.reason_phrase}"
                )

    def _is_api_key_set(self) -> bool:
        return self._api_key != "DEMO_KEY"

    def _set_path_and_params(self, **kwargs):
        match kwargs:
            case {
                "endpoint": endpoint,
                "start_date": start_date,
                **params,
            }:
                end_date = params.get("end_date")
                collection = params.get("collection")
                if end_date:
                    del params["end_date"]
                if endpoint == "collections":
                    endpoint_parts = [endpoint, collection, start_date, end_date]
                    del params["collection"]
                    params = params
                elif endpoint == "published":
                    endpoint_parts = [endpoint, start_date, end_date]
                    params = params
            case {"endpoint": "packages", "package_id": package_id, **params}:
                endpoint_parts = ["packages", package_id, "granules"]
                params = params
            case {"endpoint": "collections", **params}:
                endpoint_parts = ["collections"]
                params = params
            case _:
                raise GovInfoException

        self._path = "/".join(part for part in endpoint_parts if part is not None)
        self._set_params(**params)

    def _call_endpoint(self, **kwargs):
        self._set_path_and_params(**kwargs)

        endpoint = kwargs.get("endpoint")
        collection = kwargs.get("collection")
        match (endpoint, collection):
            case ("collections", None):
                model = Collection
            case ("collections" | "published", _):
                model = Package
            case ("packages", None):
                model = Granule

        try:
            for item in self._get(endpoint):
                yield model(**item).model_dump()
        except GovInfoException as e:
            raise e

    def _set_params(self, **params):
        self._params |= {
            key.split("_")[0]
            + "".join(word.capitalize() for word in key.split("_")[1:]): value
            for key, value in params.items()
        }

    def _set_payload_key(self, endpoint: str, path: str) -> str:
        if endpoint == "collections" and path == "collections":
            return "collections"
        return KEYS[endpoint]
