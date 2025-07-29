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
    path, params = govinfo._build_collections_request()
    assert path == "collections"
    assert params == {"offsetMark": OFFSET_DEFAULT, "pageSize": PAGE_DEFAULT}


def test_build_collections_request_with_args():
    govinfo = GovInfo()
    path, params = govinfo._build_collections_request(
        "bills", "2025-06-16T00:00:00Z", page_size=10, offset_mark="something"
    )
    assert path == "collections/bills/2025-06-16T00:00:00Z"
    assert params == {"offsetMark": "something", "pageSize": 10}


def test_build_default_packages_granules_request():
    govinfo = GovInfo()
    path, params = govinfo._build_granules_request("CREC-2018-01-04")
    assert path == "packages/CREC-2018-01-04/granules"
    assert params == {"offsetMark": OFFSET_DEFAULT, "pageSize": PAGE_DEFAULT}


def test_build__packages_granules_request_with_args():
    govinfo = GovInfo()
    path, params = govinfo._build_granules_request(
        "CREC-2018-01-04", granule_class="something", md5="something"
    )
    assert path == "packages/CREC-2018-01-04/granules"
    assert params == {
        "offsetMark": OFFSET_DEFAULT,
        "pageSize": PAGE_DEFAULT,
        "granuleClass": "something",
        "md5": "something",
    }
