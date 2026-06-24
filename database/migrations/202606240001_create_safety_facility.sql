create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create table if not exists public.safety_facility (
    id bigserial primary key,
    type varchar(30) not null,
    name varchar(200) not null,
    address text,
    latitude numeric(10, 7) not null,
    longitude numeric(10, 7) not null,
    source varchar(80) not null,
    source_id varchar(160) not null,
    description text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint uq_safety_facility_source unique (type, source, source_id),
    constraint ck_safety_facility_type check (type in ('CCTV', 'EMERGENCY_BELL', 'SECURITY_LIGHT', 'POLICE')),
    constraint ck_safety_facility_latitude check (latitude between -90 and 90),
    constraint ck_safety_facility_longitude check (longitude between -180 and 180)
);

create index if not exists idx_safety_facility_bounds
    on public.safety_facility (longitude, latitude);

create index if not exists idx_safety_facility_type_bounds
    on public.safety_facility (type, longitude, latitude);

drop trigger if exists trg_safety_facility_updated_at on public.safety_facility;
create trigger trg_safety_facility_updated_at
before update on public.safety_facility
for each row
execute function public.set_updated_at();
