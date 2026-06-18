create table if not exists public.transaction_history (
    id bigserial primary key,
    source_api varchar(50) not null,
    source_transaction_key varchar(160) not null,
    property_type varchar(20) not null,
    transaction_type varchar(20) not null,
    sido varchar(20) not null,
    sigungu varchar(30) not null,
    dong varchar(30) not null,
    legal_dong_code varchar(10) not null,
    jibun varchar(50),
    building_name varchar(200),
    building_key varchar(260) not null,
    contract_year_month varchar(6) not null,
    contract_day integer,
    deposit bigint,
    monthly_rent integer,
    price bigint,
    area_m2 numeric(8, 2) not null,
    floor integer,
    build_year integer,
    raw_json jsonb,
    created_at timestamptz not null default now(),
    constraint transaction_history_property_type_check check (
        property_type in ('OFFICETEL', 'VILLA', 'APARTMENT', 'MULTI_FAMILY')
    ),
    constraint transaction_history_transaction_type_check check (
        transaction_type in ('MONTHLY_RENT', 'JEONSE', 'SALE')
    ),
    constraint transaction_history_price_shape_check check (
        (
            transaction_type = 'MONTHLY_RENT'
            and deposit is not null
            and monthly_rent is not null
            and price is null
        )
        or (
            transaction_type = 'JEONSE'
            and deposit is not null
            and monthly_rent is null
            and price is null
        )
        or (
            transaction_type = 'SALE'
            and deposit is null
            and monthly_rent is null
            and price is not null
        )
    ),
    constraint transaction_history_source_unique unique (source_api, source_transaction_key)
);

create table if not exists public.properties (
    id bigserial primary key,
    title varchar(200) not null,
    building_name varchar(200),
    building_key varchar(260) not null,
    anchor_transaction_id bigint references public.transaction_history(id),
    property_type varchar(20) not null,
    transaction_type varchar(20) not null,
    deposit bigint,
    monthly_rent integer,
    price bigint,
    maintenance_fee integer,
    area_m2 numeric(8, 2) not null,
    floor integer,
    total_floor integer,
    address text not null,
    road_address text,
    sido varchar(20) not null,
    sigungu varchar(30) not null,
    dong varchar(30) not null,
    legal_dong_code varchar(10) not null,
    latitude numeric(10, 7) not null,
    longitude numeric(10, 7) not null,
    geocoding_provider varchar(30),
    geocoding_quality varchar(20) not null default 'BUILDING_EXACT',
    geocoded_at timestamptz,
    description text,
    source varchar(40) not null default 'MVP_SYNTHETIC',
    source_property_id varchar(100) not null,
    source_url text,
    crawled_at timestamptz,
    registered_at date,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint properties_property_type_check check (
        property_type in ('ONE_ROOM', 'OFFICETEL', 'VILLA', 'APARTMENT', 'MULTI_FAMILY')
    ),
    constraint properties_transaction_type_check check (
        transaction_type in ('MONTHLY_RENT', 'JEONSE', 'SALE')
    ),
    constraint properties_source_check check (
        source in ('MVP_SYNTHETIC', 'NAVER_REAL_ESTATE')
    ),
    constraint properties_geocoding_quality_check check (
        geocoding_quality in ('BUILDING_EXACT', 'ADDRESS_EXACT', 'DONG_APPROX', 'FAILED')
    ),
    constraint properties_price_shape_check check (
        (
            transaction_type = 'MONTHLY_RENT'
            and deposit is not null
            and monthly_rent is not null
            and price is null
        )
        or (
            transaction_type = 'JEONSE'
            and deposit is not null
            and monthly_rent is null
            and price is null
        )
        or (
            transaction_type = 'SALE'
            and deposit is null
            and monthly_rent is null
            and price is not null
        )
    ),
    constraint properties_source_unique unique (source, source_property_id)
);

create index if not exists idx_transaction_history_building
    on public.transaction_history (building_key, contract_year_month desc);

create index if not exists idx_transaction_history_match
    on public.transaction_history (
        legal_dong_code,
        property_type,
        transaction_type,
        area_m2,
        contract_year_month desc
    );

create index if not exists idx_properties_viewport
    on public.properties (is_active, longitude, latitude);

create index if not exists idx_properties_filters
    on public.properties (transaction_type, property_type, deposit, price);

create index if not exists idx_properties_region
    on public.properties (sido, sigungu, dong);

create index if not exists idx_properties_building
    on public.properties (building_key);

create or replace function public.set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists trg_properties_updated_at on public.properties;
create trigger trg_properties_updated_at
before update on public.properties
for each row
execute function public.set_updated_at();
