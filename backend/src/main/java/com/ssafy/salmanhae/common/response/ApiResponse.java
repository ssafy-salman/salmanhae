package com.ssafy.salmanhae.common.response;

public record ApiResponse<T>(
		T data,
		String message
) {

	public static <T> ApiResponse<T> ok(T data) {
		return new ApiResponse<>(data, "OK");
	}
}
