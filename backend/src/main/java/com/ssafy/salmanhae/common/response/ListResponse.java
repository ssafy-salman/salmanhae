package com.ssafy.salmanhae.common.response;

import java.util.List;

public record ListResponse<T>(
		List<T> items,
		int totalCount
) {

	public static <T> ListResponse<T> from(List<T> items) {
		List<T> snapshot = List.copyOf(items);
		return new ListResponse<>(snapshot, snapshot.size());
	}
}
