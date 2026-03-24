with source as (
    select * from read_csv_auto(
        'data/raw/Production_Crops_Livestock_E_All_Data_NOFLAG.csv',
        header = true,
        ignore_errors = true
    )
),

renamed as (
    select
        "Area Code"         as area_code,
        "Area"              as area_name,
        "Item Code"         as item_code,
        "Item"              as item_name,
        "Element Code"      as element_code,
        "Element"           as element_name,
        "Unit"              as unit,

        -- year columns unpivoted manually for key years
        "Y1990"             as y1990,
        "Y1995"             as y1995,
        "Y2000"             as y2000,
        "Y2005"             as y2005,
        "Y2010"             as y2010,
        "Y2015"             as y2015,
        "Y2018"             as y2018,
        "Y2019"             as y2019,
        "Y2020"             as y2020,
        "Y2021"             as y2021,
        "Y2022"             as y2022,
        "Y2023"             as y2023,
        "Y2024"             as y2024

    from source
)

select * from renamed