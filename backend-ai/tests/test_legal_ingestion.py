import json

import pytest

from scripts.ingest_legal_docs import load_legal_documents, main, prepare_legal_chunks


def write_source(tmp_path, documents):
    source_path = tmp_path / "legal-documents.json"
    source_path.write_text(json.dumps(documents, ensure_ascii=False), encoding="utf-8")
    return source_path


def test_load_legal_documents_validates_required_fields(tmp_path) -> None:
    source_path = write_source(
        tmp_path,
        [
            {
                "lawId": "housing-lease-protection-act",
                "lawName": "주택임대차보호법",
                "articleNo": "제3조",
                "title": "대항력 등",
                "content": "임대차는 그 등기가 없는 경우에도 임차인이 주택의 인도와 주민등록을 마친 때에는 효력이 생긴다.",
                "sourceUrl": "https://www.law.go.kr/법령/주택임대차보호법",
                "effectiveDate": "2025-01-01",
            }
        ],
    )

    documents = load_legal_documents(source_path)

    assert len(documents) == 1
    assert documents[0].law_name == "주택임대차보호법"
    assert documents[0].article_no == "제3조"


def test_load_legal_documents_rejects_missing_required_fields(tmp_path) -> None:
    source_path = write_source(
        tmp_path,
        [
            {
                "lawName": "주택임대차보호법",
                "articleNo": "제3조",
                "content": "내용",
            }
        ],
    )

    with pytest.raises(ValueError, match="lawId"):
        load_legal_documents(source_path)


def test_load_legal_documents_rejects_blank_required_fields(tmp_path) -> None:
    source_path = write_source(
        tmp_path,
        [
            {
                "lawId": "housing-lease-protection-act",
                "lawName": "   ",
                "articleNo": "제3조",
                "title": "대항력",
                "content": "임차인은 주택의 인도와 주민등록을 마친 때 효력이 생긴다.",
                "sourceUrl": "https://www.law.go.kr/법령/주택임대차보호법",
            }
        ],
    )

    with pytest.raises(ValueError, match="lawName"):
        load_legal_documents(source_path)


def test_load_legal_documents_rejects_values_over_database_limits(tmp_path) -> None:
    source_path = write_source(
        tmp_path,
        [
            {
                "lawId": "x" * 121,
                "lawName": "주택임대차보호법",
                "articleNo": "제3조",
                "title": "대항력",
                "content": "임차인은 주택의 인도와 주민등록을 마친 때 효력이 생긴다.",
                "sourceUrl": "https://www.law.go.kr/법령/주택임대차보호법",
            }
        ],
    )

    with pytest.raises(ValueError, match="lawId"):
        load_legal_documents(source_path)


def test_load_legal_documents_rejects_invalid_effective_date(tmp_path) -> None:
    source_path = write_source(
        tmp_path,
        [
            {
                "lawId": "housing-lease-protection-act",
                "lawName": "주택임대차보호법",
                "articleNo": "제3조",
                "title": "대항력",
                "content": "임차인은 주택의 인도와 주민등록을 마친 때 효력이 생긴다.",
                "sourceUrl": "https://www.law.go.kr/법령/주택임대차보호법",
                "effectiveDate": "2025/01/01",
            }
        ],
    )

    with pytest.raises(ValueError, match="effectiveDate"):
        load_legal_documents(source_path)


def test_prepare_legal_chunks_creates_stable_rows(tmp_path) -> None:
    source_path = write_source(
        tmp_path,
        [
            {
                "lawId": "housing-lease-protection-act",
                "lawName": "주택임대차보호법",
                "articleNo": "제3조의2",
                "title": "보증금의 회수",
                "content": "확정일자를 갖춘 임차인은 경매 또는 공매 시 후순위권리자보다 우선하여 보증금을 변제받을 수 있습니다.",
                "sourceUrl": "https://www.law.go.kr/법령/주택임대차보호법",
                "effectiveDate": "2025-01-01",
            }
        ],
    )

    rows = prepare_legal_chunks(load_legal_documents(source_path), chunk_size=40, overlap=5)

    assert len(rows) >= 1
    first = rows[0]
    assert first["law_id"] == "housing-lease-protection-act"
    assert first["law_name"] == "주택임대차보호법"
    assert first["article_no"] == "제3조의2"
    assert first["article_title"] == "보증금의 회수"
    assert first["chunk_index"] == 0
    assert first["content"]
    assert len(first["content_hash"]) == 64
    assert first["embedding"] is None


def test_dry_run_outputs_summary(tmp_path, capsys) -> None:
    source_path = write_source(
        tmp_path,
        [
            {
                "lawId": "special-jeonse-fraud-act",
                "lawName": "전세사기피해자 지원 및 주거안정에 관한 특별법",
                "articleNo": "제1조",
                "title": "목적",
                "content": "이 법은 전세사기피해자를 지원하고 주거안정을 도모함을 목적으로 한다.",
                "sourceUrl": "https://www.law.go.kr/법령/전세사기피해자지원및주거안정에관한특별법",
                "effectiveDate": "2025-01-01",
            }
        ],
    )

    exit_code = main(["--dry-run", str(source_path)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "documents=1" in output
    assert "chunks=1" in output


def test_main_rejects_invalid_chunk_options(tmp_path) -> None:
    source_path = write_source(tmp_path, [])

    with pytest.raises(SystemExit):
        main(["--dry-run", "--chunk-size", "0", str(source_path)])

    with pytest.raises(SystemExit):
        main(["--dry-run", "--chunk-size", "10", "--overlap", "10", str(source_path)])
