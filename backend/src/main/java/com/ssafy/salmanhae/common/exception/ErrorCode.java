package com.ssafy.salmanhae.common.exception;

import org.springframework.http.HttpStatus;

public enum ErrorCode {
	INVALID_REQUEST(HttpStatus.BAD_REQUEST, "요청 파라미터가 올바르지 않습니다."),
	INVALID_BOUNDS(HttpStatus.BAD_REQUEST, "지도 범위 파라미터가 올바르지 않습니다."),
	UNAUTHORIZED(HttpStatus.UNAUTHORIZED, "이메일 또는 비밀번호가 올바르지 않습니다."),
	EMAIL_ALREADY_EXISTS(HttpStatus.CONFLICT, "이미 가입된 이메일입니다."),
	PROPERTY_NOT_FOUND(HttpStatus.NOT_FOUND, "해당 매물을 찾을 수 없습니다."),
	AI_SERVICE_UNAVAILABLE(HttpStatus.BAD_GATEWAY, "AI 서비스 응답이 없습니다."),
	INTERNAL_SERVER_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, "서버 내부 오류가 발생했습니다.");

	private final HttpStatus status;
	private final String message;

	ErrorCode(HttpStatus status, String message) {
		this.status = status;
		this.message = message;
	}

	public HttpStatus getStatus() {
		return status;
	}

	public String getMessage() {
		return message;
	}
}
