import httpx

from govinfo.exceptions import GovInfoException
from govinfo.provider import GovInfoProvider


class GovInfo(GovInfoProvider):
    """
    Wrapper class for the GovInfo API.

    Users can supply an API key or use the default value, DEMO_KEY
    """

    def __init__(self, api_key: str = "DEMO_KEY", transport=httpx.HTTPTransport()):
        super().__init__(api_key, transport)

    def collections(
        self,
        **kwargs,
    ):
        """
        Call the collections endpoint of the GovInfo API.

        Returns collections available from the GovInfo API.
        """
        yield from self._get_list(
            "collections",
            **kwargs,
        )

    def collection(
        self, collection: str, start_date: str, end_date: str = None, **kwargs
    ):
        """
        Returns new or updated packages for the specified collection since
        the start date or with in the date range.
        """
        yield from self._get_list(
            "collections",
            collection=collection,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

    def granules(self, package_id: str, **kwargs):
        """Call the packages/{package_id}/granules endpoint of the GovInfo API."""

        yield from self._get_list(
            "packages",
            package_id=package_id,
            **kwargs,
        )

    def summary(self, package_id: str, granule_id: str | None = None, **kwargs):
        self._path = (
            f"packages/{package_id}/granules/{granule_id}/summary"
            if granule_id
            else f"packages/{package_id}/summary"
        )
        self._set_params(**kwargs)
        try:
            for item in self._get(endpoint=None):
                return item
        except GovInfoException as e:
            raise e

    def published(
        self,
        collection: str,
        start_date: str,
        end_date: str = None,
        **kwargs,
    ):
        """Call the published endpoint of the GovInfo API."""
        yield from self._get_list(
            "published",
            collection=collection,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

    def __repr__(self) -> str:
        api_key = "user supplied" if self._is_api_key_set() else self._api_key
        return f"GovInfo(url={self._url!r}, api_key={api_key!r})"
