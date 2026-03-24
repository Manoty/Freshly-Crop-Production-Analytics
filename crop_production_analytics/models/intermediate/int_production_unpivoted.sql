with production as (
    select * from {{ ref('stg_production') }}
),

unpivoted as (
    -- unpivot wide year columns into long format (year, value)
    select
        area_code,
        area_name,
        item_code,
        item_name,
        element_code,
        element_name,
        unit,
        year,
        value
    from production
    unpivot (value for year in (
        y1990, y1995, y2000, y2005, y2010,
        y2015, y2018, y2019, y2020, y2021,
        y2022, y2023, y2024
    ))
),

cleaned as (
    select
        area_code,
        area_name,
        item_code,
        item_name,
        element_code,
        element_name,
        unit,

        -- clean year column: 'y2023' → 2023
        cast(replace(year, 'y', '') as integer)  as year,

        -- cast value, nullify zeros
        case
            when value = 0 then null
            else cast(value as double)
        end                                       as value,

        -- classify element into a readable category
        case
            when element_code in (5510, 5513, 5322, 5323) then 'Production'
            when element_code in (5412, 5413, 5422)       then 'Yield'
            when element_code = 5312                       then 'Area Harvested'
            when element_code in (5320, 5321)              then 'Animals Slaughtered'
            when element_code in (5111, 5112, 5114)        then 'Stocks'
            when element_code in (5417, 5424)              then 'Yield/Carcass Weight'
            when element_code in (5319, 5314)              then 'Producing Population'
            when element_code = 5318                       then 'Milk Animals'
            when element_code = 5313                       then 'Laying'
            when element_code = 5423                       then 'Extraction Rate'
            else 'Other'
        end                                       as element_category

    from unpivoted
    where value is not null
)

select * from cleaned