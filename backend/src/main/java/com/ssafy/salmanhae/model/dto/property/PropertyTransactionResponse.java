package com.ssafy.salmanhae.model.dto.property;

import java.math.BigDecimal;

public record PropertyTransactionResponse(
		TransactionType transactionType,
		String contractYearMonth,
		Long deposit,
		Long monthlyRent,
		Long price,
		BigDecimal areaM2,
		Integer floor
) {
}
