select distinct
    area_code,
    area_name
from {{ ref('stg_areas') }}
where area_code is not null
order by area_name