create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create table if not exists public.property_score_stat (
    property_id bigint primary key references public.properties(id) on delete cascade,
    safety_score integer,
    price_score integer,
    cctv_count_300m integer not null default 0,
    bell_count_300m integer not null default 0,
    light_count_300m integer not null default 0,
    police_count_500m integer not null default 0,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

drop trigger if exists trg_property_score_stat_updated_at on public.property_score_stat;
create trigger trg_property_score_stat_updated_at
before update on public.property_score_stat
for each row
execute function public.set_updated_at();
