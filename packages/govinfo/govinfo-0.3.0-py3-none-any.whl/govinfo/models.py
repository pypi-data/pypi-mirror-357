from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class GovInfoModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, extra="allow")


class Collection(GovInfoModel):
    collection_code: str
    collection_name: str
    package_count: int | None = None
    granule_count: int | None = None


class Package(GovInfoModel):
    package_id: str
    last_modified: str
    package_link: str
    doc_class: str
    title: str
    congress: str
    date_issued: str


class Granule(GovInfoModel):
    title: str
    granule_id: str
    granule_link: str
    granule_class: str
