#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== 새 작업 시작 ===${NC}\n"

# 1. 타입 선택
echo "타입 선택:"
echo "  1) FEAT   2) BUG   3) CHORE   4) REFACTOR   5) TEST   6) DOCS"
read -p "번호 입력: " type_num

case $type_num in
  1) TYPE="FEAT" ;;
  2) TYPE="BUG" ;;
  3) TYPE="CHORE" ;;
  4) TYPE="REFACTOR" ;;
  5) TYPE="TEST" ;;
  6) TYPE="DOCS" ;;
  *) echo "잘못된 입력"; exit 1 ;;
esac

# 2. 기능 ID (선택)
read -p "기능 ID (예: F-1, 없으면 엔터): " FEATURE_ID

# 3. 제목
read -p "이슈 제목: " TITLE

# 4. 브랜치 슬러그
read -p "브랜치 슬러그 (예: property-api): " SLUG

# 5. 이슈 제목 조합
if [ -n "$FEATURE_ID" ]; then
  ISSUE_TITLE="[$TYPE][$FEATURE_ID] $TITLE"
else
  ISSUE_TITLE="[$TYPE] $TITLE"
fi

# 6. GitHub 이슈 생성
echo -e "\n${BLUE}이슈 생성 중...${NC}"
ISSUE_URL=$(gh issue create \
  --title "$ISSUE_TITLE" \
  --body "## 목표
$TITLE

## 작업 범위
- [ ]

## 참고
- 기능 명세: artifact/docs/02_mvp_scope.md
- 컨벤션: artifact/docs/12_git_convention.md")

ISSUE_NUMBER=$(echo "$ISSUE_URL" | grep -o '[0-9]*$')

# 7. 브랜치 생성 + checkout
BRANCH="feature/${ISSUE_NUMBER}-${SLUG}"
git checkout -b "$BRANCH"

echo -e "\n${GREEN}완료!${NC}"
echo "이슈: $ISSUE_URL"
echo "브랜치: $BRANCH"
