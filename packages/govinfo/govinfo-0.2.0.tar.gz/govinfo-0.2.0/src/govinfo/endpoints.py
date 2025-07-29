from govinfo.config import RequestArgs
from govinfo.exceptions import GovInfoException
from govinfo.models import Collection, Granule, Package


class Collections:
    def _build_collections_request(
        self,
        collection: str = None,
        start_date: str = None,
        end_date: str = None,
        **kwargs,
    ) -> RequestArgs:
        endpoint_parts = ["collections", collection, start_date, end_date]
        path = "/".join(part for part in endpoint_parts if part is not None)
        params = self._set_params(**kwargs)
        return (path, params)

    def collections(
        self,
        collection: str = None,
        start_date: str = None,
        end_date: str = None,
        **kwargs,
    ):
        """Call the collections endpoint of the GovInfo API."""
        args = self._build_collections_request(
            collection, start_date, end_date, **kwargs
        )

        try:
            if collection:
                for item in self._get("collections", args):
                    yield Package(**item).model_dump()
            else:
                for item in self._get("collections", args):
                    yield Collection(**item).model_dump()
        except GovInfoException as e:
            raise e


class Packages:
    def _build_granules_request(
        self,
        package_id: str,
        **kwargs,
    ) -> RequestArgs:
        path = f"packages/{package_id}/granules"
        params = self._set_params(**kwargs)
        return (path, params)

    def granules(self, package_id: str, **kwargs):
        """Call the packages/{package_id}/granules endpoint of the GovInfo API."""
        args = self._build_granules_request(package_id, **kwargs)

        try:
            for item in self._get("granules", args):
                yield Granule(**item).model_dump()
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


class Published:
    def _build_published_request(
        self,
        collection: str,
        start_date: str = None,
        end_date: str = None,
        **kwargs,
    ) -> RequestArgs:
        endpoint_parts = ["published", start_date, end_date]
        path = "/".join(part for part in endpoint_parts if part is not None)
        params = self._set_params(**kwargs)
        params["collection"] = collection
        return (path, params)

    def published(
        self,
        collection: str,
        start_date: str = None,
        end_date: str = None,
        **kwargs,
    ):
        """Call the published endpoint of the GovInfo API."""
        args = self._build_published_request(collection, start_date, end_date, **kwargs)

        try:
            for item in self._get("published", args):
                yield Package(**item).model_dump()
        except GovInfoException as e:
            raise e
