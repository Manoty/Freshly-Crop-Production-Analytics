with source as (
    select * from read_csv_auto(
        'data/raw/Production_Crops_Livestock_E_ItemCodes.csv',
        header = true,
        ignore_errors = true
    )
)

select
    "Item Code"   as item_code,
    "Item"        as item_name
from source