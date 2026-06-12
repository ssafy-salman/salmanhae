#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# 현재 브랜치에서 이슈 번호 추출
BRANCH=$(git branch --show-current)
ISSUE_NUMBER=$(echo "$BRANCH" | grep -o '[0-9]\+' | head -1)

if [ -z "$ISSUE_NUMBER" ]; then
  read -p "이슈 번호를 찾을 수 없습니다. 직접 입력: " ISSUE_NUMBER
fi

echo -e "${BLUE}브랜치: $BRANCH | 이슈: #$ISSUE_NUMBER${NC}\n"

# 변경 파일 확인
echo -e "${BLUE}변경 파일:${NC}"
git status --short

# 커밋 메시지 입력
echo -e "\n커밋 형식: type(scope): 설명"
echo "예: feat(property): 매물 조회 API 구현"
read -p "커밋 메시지: " COMMIT_MSG

# 커밋
git add .
git commit -m "$COMMIT_MSG (#$ISSUE_NUMBER)"

echo -e "\n${GREEN}커밋 완료!${NC}"
