with production as (
    select * from {{ ref('int_production_unpivoted') }}
),

filtered as (
    select
        area_code,
        area_name,
        item_code,
        item_name,
        element_category,
        unit,
        year,
        value
    from production
    where element_category in (
        'Production',
        'Yield',
        'Area Harvested',
        'Animals Slaughtered'
    )
    and value is not null  -- ← add this line
)

select * from filtered