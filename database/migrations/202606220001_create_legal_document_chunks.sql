create extension if not exists vector;

create table if not exists public.legal_document_chunks (
    id bigserial primary key,
    law_id varchar(120) not null,
    law_name varchar(200) not null,
    article_no varchar(50) not null,
    article_title varchar(200) not null,
    effective_date date,
    source_name varchar(80) not null default 'law.go.kr',
    source_url text not null,
    chunk_index integer not null,
    content text not null,
    content_hash char(64) not null,
    embedding vector(1536),
    metadata_json jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint legal_document_chunks_chunk_index_check check (chunk_index >= 0),
    constraint legal_document_chunks_content_hash_unique unique (content_hash)
);

create index if not exists idx_legal_document_chunks_law_article
    on public.legal_document_chunks (law_id, article_no, chunk_index);

create index if not exists idx_legal_document_chunks_law_name
    on public.legal_document_chunks (law_name);

create index if not exists idx_legal_document_chunks_metadata
    on public.legal_document_chunks using gin (metadata_json);

create index if not exists idx_legal_document_chunks_embedding
    on public.legal_document_chunks
    using ivfflat (embedding vector_cosine_ops)
    with (lists = 100)
    where embedding is not null;

drop trigger if exists trg_legal_document_chunks_updated_at on public.legal_document_chunks;
create trigger trg_legal_document_chunks_updated_at
before update on public.legal_document_chunks
for each row
execute function public.set_updated_at();
