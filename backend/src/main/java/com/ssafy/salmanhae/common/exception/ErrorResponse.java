package com.ssafy.salmanhae.common.exception;

public record ErrorResponse(
		String code,
		String message,
		int status
) {

	public static ErrorResponse from(ErrorCode errorCode) {
		return new ErrorResponse(
				errorCode.name(),
				errorCode.getMessage(),
				errorCode.getStatus().value()
		);
	}
}
