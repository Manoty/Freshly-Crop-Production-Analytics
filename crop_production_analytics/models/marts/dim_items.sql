select distinct
    item_code,
    item_name
from {{ ref('stg_items') }}
where item_code is not null
order by item_name