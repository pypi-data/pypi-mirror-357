import data
import httpx
import pytest

from govinfo import GovInfo
from govinfo.config import OFFSET_DEFAULT, PAGE_DEFAULT


def test_govinfo_default_api_key():
    govinfo = GovInfo()
    assert govinfo._api_key == "DEMO_KEY"


def test_govinfo_user_supplied_api_key():
    govinfo = GovInfo(api_key="dummy key")
    assert govinfo._api_key == "dummy key"


def test_govinfo_repr():
    govinfo = GovInfo()
    assert str(govinfo) == "GovInfo(url='https://api.govinfo.gov', api_key='DEMO_KEY')"
    govinfo = GovInfo(api_key="dummy key")
    assert (
        str(govinfo)
        == "GovInfo(url='https://api.govinfo.gov', api_key='user supplied')"
    )


def test_build_default_collections_request():
    govinfo = GovInfo()
    govinfo._set_path_and_params(endpoint="collections")
    assert govinfo._path == "collections"
    assert govinfo._params == {"offsetMark": OFFSET_DEFAULT, "pageSize": PAGE_DEFAULT}


def test_build_collections_request_with_args():
    govinfo = GovInfo()
    govinfo._set_path_and_params(
        endpoint="collections",
        collection="bills",
        start_date="2025-06-16T00:00:00Z",
        end_date="2025-06-17T00:00:00Z",
        page_size=10,
        offset_mark="something",
    )
    assert (
        govinfo._path == "collections/bills/2025-06-16T00:00:00Z/2025-06-17T00:00:00Z"
    )
    assert govinfo._params == {"offsetMark": "something", "pageSize": 10}


def test_build_default_packages_granules_request():
    govinfo = GovInfo()
    govinfo._set_path_and_params(endpoint="packages", package_id="CREC-2018-01-04")
    assert govinfo._path == "packages/CREC-2018-01-04/granules"
    assert govinfo._params == {"offsetMark": OFFSET_DEFAULT, "pageSize": PAGE_DEFAULT}


def test_build_packages_granules_request_with_args():
    govinfo = GovInfo()
    govinfo._set_path_and_params(
        endpoint="packages",
        package_id="CREC-2018-01-04",
        granule_class="something",
        md5="something",
    )
    assert govinfo._path == "packages/CREC-2018-01-04/granules"
    assert govinfo._params == {
        "offsetMark": OFFSET_DEFAULT,
        "pageSize": PAGE_DEFAULT,
        "granuleClass": "something",
        "md5": "something",
    }


def test_build_default_published_request():
    govinfo = GovInfo()
    govinfo._set_path_and_params(
        endpoint="published", collection="bills", start_date="2025-06-20"
    )
    assert govinfo._path == "published/2025-06-20"
    assert govinfo._params == {
        "offsetMark": OFFSET_DEFAULT,
        "pageSize": PAGE_DEFAULT,
        "collection": "bills",
    }


def test_collections():
    def handler(request):
        return httpx.Response(200, json=data.collections)

    transport = httpx.MockTransport(handler)
    govinfo = GovInfo(transport=transport)

    collections = list(govinfo.collections())

    assert len(collections) == 40


def test_collection_with_collection_no_start_date():
    govinfo = GovInfo()
    with pytest.raises(TypeError):
        list(govinfo.collection("bills"))


def test_collection():
    def handler(request):
        return httpx.Response(200, json=data.bills)

    transport = httpx.MockTransport(handler)
    govinfo = GovInfo(transport=transport)

    bills = list(govinfo.collection("bills", "2025-06-22T00:00:00Z", page_size=50))

    # well-constructed path
    assert govinfo._path == "collections/bills/2025-06-22T00:00:00Z"
    # snake to camel conversion
    assert "pageSize" in govinfo._params
    # param value set
    assert govinfo._params["pageSize"] == 50
    # pydantic to_camel works
    assert list(bills[0].keys()) == [
        "package_id",
        "last_modified",
        "package_link",
        "doc_class",
        "title",
        "congress",
        "date_issued",
    ]
