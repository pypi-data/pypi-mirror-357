from json import JSONDecodeError

import httpx

from govinfo.config import BASE_URL, KEYS, OFFSET_DEFAULT, PAGE_DEFAULT, RequestArgs
from govinfo.exceptions import GovInfoException
from govinfo.models import Granule, Package, Collection


class GovInfo:
    """Wrapper class for the GovInfo API.

    Users can supply an API key or use the default value, DEMO_KEY"""

    def __init__(self, api_key: str = "DEMO_KEY"):
        self._url = f"{BASE_URL}"
        self._api_key = api_key

    def collections(
        self,
        collection: str = None,
        start_date: str = None,
        end_date: str = None,
        **kwargs,
    ):
        """Call the collections endpoint of the GovInfo API."""

        try:
            return self._call_endpoint(
                endpoint="collections",
                collection=collection,
                start_date=start_date,
                end_date=end_date,
                **kwargs,
            )
        except GovInfoException as e:
            raise e

    def granules(self, package_id: str, **kwargs):
        """Call the packages/{package_id}/granules endpoint of the GovInfo API."""

        try:
            return self._call_endpoint(
                endpoint="packages", package_id=package_id, **kwargs
            )
        except GovInfoException as e:
            raise e

    def summary(self, package_id: str, granule_id: str | None = None, **kwargs):
        path = (
            f"packages/{package_id}/granules/{granule_id}/summary"
            if granule_id
            else f"packages/{package_id}/summary"
        )
        params = self._set_params(**kwargs)
        try:
            for item in self._get(
                endpoint=None,
                args=(
                    path,
                    params,
                ),
            ):
                return item
        except GovInfoException as e:
            raise e

    def published(
        self,
        collection: str,
        start_date: str = None,
        end_date: str = None,
        **kwargs,
    ):
        """Call the published endpoint of the GovInfo API."""

        try:
            return self._call_endpoint(
                endpoint="published",
                collection=collection,
                start_date=start_date,
                end_date=end_date,
                **kwargs,
            )
        except GovInfoException as e:
            raise e

    def _get(self, endpoint: str, args: RequestArgs):
        headers = {"x-api-key": self._api_key}
        path, params = args
        with httpx.Client(headers=headers) as client:
            response = client.get("/".join([self._url, path]), params=params)
            try:
                payload = response.json()
            except (ValueError, JSONDecodeError) as e:
                raise GovInfoException("Bad JSON in response") from e
            is_success = 299 >= response.status_code >= 200
            if is_success:
                if endpoint is None:
                    yield payload
                else:
                    payload_key = self._set_payload_key(endpoint, path)
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

    def __repr__(self) -> str:
        api_key = "user supplied" if self._is_api_key_set() else self._api_key
        return f"GovInfo(url={self._url!r}, api_key={api_key!r})"

    def _is_api_key_set(self) -> bool:
        return self._api_key != "DEMO_KEY"

    def _build_request(self, **kwargs) -> RequestArgs:
        match kwargs:
            case {
                "endpoint": endpoint,
                "collection": collection,
                "start_date": start_date,
                **params,
            }:
                if endpoint == "collections":
                    endpoint_parts = [endpoint, collection, start_date]
                    params = params
                elif endpoint == "published":
                    endpoint_parts = [endpoint, start_date]
                    params = params
                    params["collection"] = collection
            case {
                "endpoint": endpoint,
                "collection": collection,
                "start_date": start_date,
                "end_date": end_date,
                **params,
            }:
                if endpoint == "collections":
                    endpoint_parts = [endpoint, collection, start_date, end_date]
                    params = params
                elif endpoint == "published":
                    endpoint_parts = [endpoint, start_date, end_date]
                    params = params
                    params["collection"] = collection
            case {"endpoint": endpoint, "package_id": package_id, **params}:
                endpoint_parts = [endpoint, package_id, "granules"]
                params = params
            case {"endpoint": endpoint, **params}:
                endpoint_parts = [endpoint]
                params = params
            case _:
                raise GovInfoException

        path = "/".join(part for part in endpoint_parts if part is not None)
        params = self._set_params(**params)
        return (path, params)

    def _call_endpoint(self, **kwargs):
        args = self._build_request(**kwargs)
        endpoint = kwargs.get("endpoint")
        collection = kwargs.get("collection")
        match (endpoint, collection):
            case ("collections", None):
                model = Collection
            case ("collections", _):
                model = Package
            case ("packages", None):
                model = Granule
            case ("published", _):
                model = Package

        try:
            for item in self._get(endpoint, args):
                yield model(**item).model_dump()
        except GovInfoException as e:
            raise e

    def _set_params(self, **params) -> dict[str, str]:
        default_params = {"offsetMark": OFFSET_DEFAULT, "pageSize": PAGE_DEFAULT}
        params = (
            default_params
            if not params
            else default_params
            | {
                key.split("_")[0]
                + "".join(word.capitalize() for word in key.split("_")[1:]): value
                for key, value in params.items()
            }
        )
        return params

    def _set_payload_key(self, endpoint: str, path: str) -> str:
        if endpoint == "collections" and path == "collections":
            payload_key = "collections"
        else:
            payload_key = KEYS[endpoint]
        return payload_key
