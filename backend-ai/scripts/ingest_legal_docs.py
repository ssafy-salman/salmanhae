"""Prepare legal document chunks for the F-3 legal RAG index."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Sequence

from app.clients.embedding_client import EmbeddingClient
from app.clients.supabase_client import SupabaseVectorClient
from app.rag.chunker import chunk_text


REQUIRED_FIELDS = ("lawId", "lawName", "articleNo", "title", "content", "sourceUrl")
FIELD_LIMITS = {
    "lawId": 120,
    "lawName": 200,
    "articleNo": 50,
    "title": 200,
    "sourceName": 80,
}


@dataclass(frozen=True)
class LegalDocument:
    law_id: str
    law_name: str
    article_no: str
    title: str
    content: str
    source_url: str
    effective_date: str | None = None
    source_name: str = "law.go.kr"


def load_legal_documents(source_path: str | Path) -> list[LegalDocument]:
    path = Path(source_path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Legal document source must be a JSON array.")

    documents: list[LegalDocument] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"Document at index {index} must be an object.")

        missing = [field for field in REQUIRED_FIELDS if not optional_str(item.get(field))]
        if missing:
            raise ValueError(f"Document at index {index} is missing required field: {missing[0]}")

        law_id = str(item["lawId"]).strip()
        law_name = str(item["lawName"]).strip()
        article_no = str(item["articleNo"]).strip()
        title = str(item["title"]).strip()
        source_url = str(item["sourceUrl"]).strip()
        effective_date = optional_str(item.get("effectiveDate"))
        source_name = optional_str(item.get("sourceName")) or "law.go.kr"
        validate_document_fields(
            index,
            {
                "lawId": law_id,
                "lawName": law_name,
                "articleNo": article_no,
                "title": title,
                "sourceName": source_name,
            },
            effective_date,
        )

        documents.append(
            LegalDocument(
                law_id=law_id,
                law_name=law_name,
                article_no=article_no,
                title=title,
                content=normalize_content(str(item["content"])),
                source_url=source_url,
                effective_date=effective_date,
                source_name=source_name,
            )
        )
    return documents


def prepare_legal_chunks(
    documents: Sequence[LegalDocument],
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for document in documents:
        chunks = chunk_text(document.content, chunk_size=chunk_size, overlap=overlap)
        for chunk_index, content in enumerate(chunks):
            rows.append(
                {
                    "law_id": document.law_id,
                    "law_name": document.law_name,
                    "article_no": document.article_no,
                    "article_title": document.title,
                    "effective_date": document.effective_date,
                    "source_name": document.source_name,
                    "source_url": document.source_url,
                    "chunk_index": chunk_index,
                    "content": content,
                    "content_hash": content_hash(document, content, chunk_index),
                    "embedding": None,
                    "metadata_json": {
                        "sourceUrl": document.source_url,
                        "effectiveDate": document.effective_date,
                    },
                }
            )
    return rows


def embed_legal_chunks(
    rows: Sequence[dict[str, Any]],
    embedding_client: Any,
) -> list[dict[str, Any]]:
    embedded_rows: list[dict[str, Any]] = []
    for row in rows:
        content = str(row.get("content", ""))
        embedded_row = dict(row)
        embedded_row["embedding"] = embedding_client.embed_query(content)
        embedded_rows.append(embedded_row)
    return embedded_rows


def write_legal_chunks(
    rows: Sequence[dict[str, Any]],
    embedding_client: Any | None = None,
    vector_client: Any | None = None,
) -> dict[str, int]:
    embedding_client = embedding_client or EmbeddingClient()
    vector_client = vector_client or SupabaseVectorClient()
    embedded_rows = embed_legal_chunks(rows, embedding_client)
    upserted = vector_client.upsert_legal_document_chunks(embedded_rows)
    return {"chunks": len(embedded_rows), "upserted": int(upserted)}


def normalize_content(content: str) -> str:
    return "\n".join(line.strip() for line in content.splitlines() if line.strip())


def optional_str(value: Any) -> str | None:
    if value is None:
        return None
    stripped = str(value).strip()
    return stripped or None


def validate_document_fields(
    index: int,
    values: dict[str, str],
    effective_date: str | None,
) -> None:
    for field, limit in FIELD_LIMITS.items():
        if len(values[field]) > limit:
            raise ValueError(
                f"Document at index {index} field {field} exceeds {limit} characters."
            )

    if effective_date is not None:
        try:
            date.fromisoformat(effective_date)
        except ValueError as exc:
            raise ValueError(
                f"Document at index {index} field effectiveDate must use YYYY-MM-DD."
            ) from exc


def content_hash(document: LegalDocument, content: str, chunk_index: int) -> str:
    key = "\n".join(
        [document.law_id, document.article_no, document.title, str(chunk_index), content]
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare legal document chunks for pgvector ingestion.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and summarize chunks without DB writes.")
    parser.add_argument("--write", action="store_true", help="Embed chunks and upsert them into Supabase.")
    parser.add_argument("source", type=Path, help="Path to a legal document JSON array.")
    parser.add_argument("--chunk-size", type=int, default=800)
    parser.add_argument("--overlap", type=int, default=120)
    return parser


def main(
    argv: Sequence[str] | None = None,
    embedding_client: Any | None = None,
    vector_client: Any | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.dry_run and args.write:
        parser.error("Use only one of --dry-run or --write.")
    if not args.dry_run and not args.write:
        parser.error("Use --dry-run to validate or --write to upsert legal chunks.")
    if args.chunk_size <= 0:
        parser.error("--chunk-size must be greater than 0.")
    if args.overlap < 0 or args.overlap >= args.chunk_size:
        parser.error("--overlap must satisfy 0 <= overlap < chunk-size.")

    documents = load_legal_documents(args.source)
    rows = prepare_legal_chunks(documents, chunk_size=args.chunk_size, overlap=args.overlap)

    if args.dry_run:
        print(f"Legal ingestion dry-run: documents={len(documents)} chunks={len(rows)}")
        return 0

    summary = write_legal_chunks(rows, embedding_client, vector_client)
    print(
        "Legal ingestion write: "
        f"documents={len(documents)} chunks={summary['chunks']} upserted={summary['upserted']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
