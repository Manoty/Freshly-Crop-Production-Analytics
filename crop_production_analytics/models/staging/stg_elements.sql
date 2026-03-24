with source as (
    select * from read_csv_auto(
        'data/raw/Production_Crops_Livestock_E_Elements.csv',
        header = true,
        ignore_errors = true
    )
)

select
    "Element Code"   as element_code,
    "Element"        as element_name
from source