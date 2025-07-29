import os
from pprint import pprint

from govinfo import GovInfo

api_key = os.getenv("GPO_API_KEY")
govinfo = GovInfo(api_key=api_key)
start_date = "2025-06-20T00:00:00Z"
collections = govinfo.collections()
collections = govinfo.collections("bills", start_date=start_date)
package_id = "CREC-2018-01-04"
granule_id = "CREC-2018-01-04-pt1-PgD7-2"

pprint(list(collections))

granules = govinfo.granules(package_id)
pprint(list(granules))

crec_summary = govinfo.summary(package_id)
pprint(crec_summary)

published = govinfo.published("bills", "2025-06-20")
pprint(list(published))
