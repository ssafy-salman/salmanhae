"""Prepare legal document chunks for the F-3 legal RAG index."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from app.rag.chunker import chunk_text


REQUIRED_FIELDS = ("lawId", "lawName", "articleNo", "title", "content", "sourceUrl")


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

        documents.append(
            LegalDocument(
                law_id=str(item["lawId"]).strip(),
                law_name=str(item["lawName"]).strip(),
                article_no=str(item["articleNo"]).strip(),
                title=str(item["title"]).strip(),
                content=normalize_content(str(item["content"])),
                source_url=str(item["sourceUrl"]).strip(),
                effective_date=optional_str(item.get("effectiveDate")),
                source_name=optional_str(item.get("sourceName")) or "law.go.kr",
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


def normalize_content(content: str) -> str:
    return "\n".join(line.strip() for line in content.splitlines() if line.strip())


def optional_str(value: Any) -> str | None:
    if value is None:
        return None
    stripped = str(value).strip()
    return stripped or None


def content_hash(document: LegalDocument, content: str, chunk_index: int) -> str:
    key = "\n".join(
        [document.law_id, document.article_no, document.title, str(chunk_index), content]
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare legal document chunks for pgvector ingestion.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and summarize chunks without DB writes.")
    parser.add_argument("source", type=Path, help="Path to a legal document JSON array.")
    parser.add_argument("--chunk-size", type=int, default=800)
    parser.add_argument("--overlap", type=int, default=120)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    documents = load_legal_documents(args.source)
    rows = prepare_legal_chunks(documents, chunk_size=args.chunk_size, overlap=args.overlap)

    if args.dry_run:
        print(f"Legal ingestion dry-run: documents={len(documents)} chunks={len(rows)}")
        return 0

    raise RuntimeError("Database writes are not enabled in Phase 2. Use --dry-run.")


if __name__ == "__main__":
    raise SystemExit(main())
