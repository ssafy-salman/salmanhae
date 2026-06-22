create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create table if not exists public.region_price_stat (
    id bigserial primary key,
    region_level varchar(20) not null,
    region_code varchar(80) not null,
    sido varchar(20) not null,
    sigungu varchar(30),
    dong varchar(30),
    property_type varchar(20) not null,
    transaction_type varchar(20) not null,
    avg_deposit bigint,
    median_deposit bigint,
    avg_monthly_rent integer,
    median_monthly_rent integer,
    avg_price bigint,
    median_price bigint,
    transaction_count integer not null,
    sample_from_ym varchar(6),
    sample_to_ym varchar(6),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint region_price_stat_level_check check (
        region_level in ('SIDO', 'SIGUNGU', 'DONG')
    ),
    constraint region_price_stat_property_type_check check (
        property_type in ('OFFICETEL', 'VILLA', 'APARTMENT', 'MULTI_FAMILY')
    ),
    constraint region_price_stat_transaction_type_check check (
        transaction_type in ('MONTHLY_RENT', 'JEONSE', 'SALE')
    ),
    constraint region_price_stat_unique unique (
        region_level,
        region_code,
        property_type,
        transaction_type
    )
);

create table if not exists public.building_price_stat (
    id bigserial primary key,
    building_key varchar(260) not null,
    building_name varchar(200),
    sido varchar(20) not null,
    sigungu varchar(30) not null,
    dong varchar(30) not null,
    legal_dong_code varchar(10) not null,
    property_type varchar(20) not null,
    transaction_type varchar(20) not null,
    avg_deposit bigint,
    median_deposit bigint,
    avg_monthly_rent integer,
    median_monthly_rent integer,
    avg_price bigint,
    median_price bigint,
    transaction_count integer not null,
    sample_from_ym varchar(6),
    sample_to_ym varchar(6),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint building_price_stat_property_type_check check (
        property_type in ('OFFICETEL', 'VILLA', 'APARTMENT', 'MULTI_FAMILY')
    ),
    constraint building_price_stat_transaction_type_check check (
        transaction_type in ('MONTHLY_RENT', 'JEONSE', 'SALE')
    ),
    constraint building_price_stat_unique unique (
        building_key,
        property_type,
        transaction_type
    )
);

create index if not exists idx_region_price_stat_lookup
    on public.region_price_stat (region_level, region_code, property_type, transaction_type);

create index if not exists idx_building_price_stat_lookup
    on public.building_price_stat (building_key, property_type, transaction_type);

create index if not exists idx_building_price_stat_region
    on public.building_price_stat (legal_dong_code, property_type, transaction_type);

drop trigger if exists trg_region_price_stat_updated_at on public.region_price_stat;
create trigger trg_region_price_stat_updated_at
before update on public.region_price_stat
for each row
execute function public.set_updated_at();

drop trigger if exists trg_building_price_stat_updated_at on public.building_price_stat;
create trigger trg_building_price_stat_updated_at
before update on public.building_price_stat
for each row
execute function public.set_updated_at();
