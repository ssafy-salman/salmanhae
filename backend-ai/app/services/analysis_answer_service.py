from typing import Any

from app.graph.state import AgentState


class AnalysisAnswerService:
    def generate_price_answer(self, state: AgentState) -> str:
        result = self._tool_result(state, "priceAnalysis")

        if result.get("requiresSelection"):
            return (
                "지역 시세를 분석하려면 지도에서 매물을 먼저 선택해 주세요. "
                "매물을 선택하시면 해당 위치 기준 실거래가와 지역 통계를 바탕으로 시세를 분석해 드릴게요."
            )

        card = self._analysis_card(state, "PRICE")
        metrics = self._combined_metrics(result, card)
        transactions = self._items(result.get("transactions"))
        price_analysis = result.get("priceAnalysis", {})
        if not isinstance(price_analysis, dict):
            price_analysis = {}
        region_stats = self._items(price_analysis.get("regionStats"))

        facts: list[str] = []
        comparable_count_metric = metrics.get("comparableTransactionCount")
        if comparable_count_metric is not None:
            comparable_count = comparable_count_metric
        elif transactions:
            comparable_count = len(transactions)
        else:
            comparable_count = None
        if comparable_count is not None:
            facts.append(f"최근 거래 {comparable_count}건을 기준으로 확인했습니다.")

        if transactions:
            transaction = transactions[0]
            parts: list[str] = []
            contract_ym = transaction.get("contractYearMonth")
            if contract_ym:
                parts.append(str(contract_ym))
            deposit = self._format_won(transaction.get("deposit"))
            if deposit:
                parts.append(f"보증금 {deposit}")
            monthly_rent = self._format_won(transaction.get("monthlyRent"))
            if monthly_rent:
                parts.append(f"월세 {monthly_rent}")
            area_m2 = transaction.get("areaM2")
            if area_m2 is not None:
                parts.append(f"전용면적 {area_m2}㎡")
            if parts:
                facts.append("최근 거래는 " + ", ".join(parts) + "입니다.")

        if region_stats:
            region_stat = region_stats[0]
            parts = []
            avg_deposit = self._format_won(region_stat.get("avgDeposit"))
            if avg_deposit:
                parts.append(f"지역 평균 보증금 {avg_deposit}")
            avg_monthly_rent = self._format_won(region_stat.get("avgMonthlyRent"))
            if avg_monthly_rent:
                parts.append(f"지역 평균 월세 {avg_monthly_rent}")
            transaction_count = region_stat.get("transactionCount")
            if transaction_count is not None:
                parts.append(f"통계 표본 {transaction_count}건")
            if parts:
                facts.append(", ".join(parts) + "입니다.")

        regional_stats = self._items(result.get("regionalStats"))
        if regional_stats and not facts:
            return self._format_regional_price_answer(regional_stats, result)

        if not facts:
            return "분석할 근거 데이터가 부족합니다. 매물을 선택하거나 시세 데이터가 쌓인 뒤 다시 확인해 주세요."

        return " ".join(facts) + " 보증보험 가능 여부나 법적 판단은 포함하지 않았습니다."

    def generate_safety_answer(self, state: AgentState) -> str:
        result = self._tool_result(state, "safetyAnalysis")

        if result.get("requiresSelection"):
            return (
                "주변 안전 정보를 분석하려면 지도에서 매물을 먼저 선택해 주세요. "
                "매물을 선택하시면 반경 500m 내 CCTV·비상벨·보안등·경찰시설 현황을 바탕으로 안전 점수를 알려드릴게요."
            )

        card = self._analysis_card(state, "SAFETY")
        safety_summary = result.get("safetySummary", {})
        if not isinstance(safety_summary, dict):
            safety_summary = {}
        result_metrics = result.get("metrics", {})
        if not isinstance(result_metrics, dict):
            result_metrics = {}
        metrics = {
            **self._combined_metrics(result, card),
            **safety_summary,
            **result_metrics,
        }

        facts: list[str] = []
        score = result.get("score")
        if score is None:
            score = safety_summary.get("safetyScore")
        if score is None:
            score = metrics.get("safetyScore")
        if score is None:
            score = card.get("score")
        if score is not None:
            facts.append(f"안전 점수 {score}점")

        radius = metrics.get("radius")
        if radius is not None:
            facts.append(f"반경 {radius}m")

        count_specs = [
            ("cctvCount300m", "CCTV"),
            ("bellCount300m", "비상벨"),
            ("lightCount300m", "보안등"),
            ("policeCount500m", "경찰시설"),
        ]
        for key, label in count_specs:
            value = metrics.get(key)
            if value is not None:
                facts.append(f"{label} {value}개")

        if not facts:
            return "분석할 근거 데이터가 부족합니다. 매물을 선택하거나 안전 데이터가 쌓인 뒤 다시 확인해 주세요."

        return "주변 안전 데이터는 " + ", ".join(facts) + "로 확인됩니다. 실제 체감 안전은 현장 환경에 따라 달라질 수 있습니다."

    def _tool_result(self, state: AgentState, key: str) -> dict[str, Any]:
        tool_results = state.get("tool_results", {})
        if not isinstance(tool_results, dict):
            return {}
        value = tool_results.get(key, {})
        return value if isinstance(value, dict) else {}

    def _analysis_card(self, state: AgentState, card_type: str) -> dict[str, Any]:
        analysis_cards = state.get("analysis_cards", [])
        if not isinstance(analysis_cards, list):
            return {}
        for card in reversed(analysis_cards):
            if isinstance(card, dict) and card.get("type") == card_type:
                return card
        return {}

    def _combined_metrics(self, result: dict[str, Any], card: dict[str, Any]) -> dict[str, Any]:
        result_metrics = result.get("metrics", {})
        card_metrics = card.get("metrics", {})
        if not isinstance(result_metrics, dict):
            result_metrics = {}
        if not isinstance(card_metrics, dict):
            card_metrics = {}
        return {**card_metrics, **result_metrics}

    def _items(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict)]

    def _format_regional_price_answer(
        self, stats: list[dict[str, Any]], result: dict[str, Any]
    ) -> str:
        metrics = result.get("metrics", {}) or {}
        region_name = metrics.get("dong") or metrics.get("sigungu") or "해당 지역"

        tx_label = {"JEONSE": "전세", "MONTHLY_RENT": "월세", "SALE": "매매"}
        prop_label = {
            "ONE_ROOM": "원룸", "OFFICETEL": "오피스텔", "VILLA": "빌라",
            "APARTMENT": "아파트", "MULTI_FAMILY": "다가구",
        }

        lines: list[str] = [f"**{region_name}** 지역 시세 현황입니다.\n"]
        for stat in stats[:5]:
            pt = prop_label.get(stat.get("property_type", ""), stat.get("property_type", ""))
            tt = tx_label.get(stat.get("transaction_type", ""), stat.get("transaction_type", ""))
            parts: list[str] = []
            if pt and tt:
                parts.append(f"{pt} {tt}")
            avg_deposit = self._format_won(stat.get("avg_deposit"))
            if avg_deposit:
                parts.append(f"평균 보증금 {avg_deposit}")
            avg_rent = self._format_won(stat.get("avg_monthly_rent"))
            if avg_rent:
                parts.append(f"평균 월세 {avg_rent}")
            avg_price = self._format_won(stat.get("avg_price"))
            if avg_price:
                parts.append(f"평균 매매가 {avg_price}")
            count = stat.get("transaction_count")
            if count:
                parts.append(f"표본 {count}건")
            if parts:
                lines.append("· " + " / ".join(parts))

        lines.append("\n실제 거래가는 층수·면적·시기에 따라 달라질 수 있습니다.")
        return "\n".join(lines)

    def _format_won(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return None
        if not isinstance(value, (int, float)):
            return None
        amount = int(value) if float(value).is_integer() else value
        return f"{amount:,}원"
