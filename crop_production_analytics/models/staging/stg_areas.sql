with source as (
    select * from read_csv_auto(
        'data/raw/Production_Crops_Livestock_E_AreaCodes.csv',
        header = true,
        ignore_errors = true
    )
)

select
    "Area Code"   as area_code,
    "Area"        as area_name
from source