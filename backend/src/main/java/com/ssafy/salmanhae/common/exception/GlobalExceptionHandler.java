package com.ssafy.salmanhae.common.exception;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

@RestControllerAdvice
public class GlobalExceptionHandler {

	@ExceptionHandler(ApiException.class)
	public ResponseEntity<ErrorResponse> handleApiException(ApiException exception) {
		ErrorCode errorCode = exception.getErrorCode();
		return ResponseEntity
				.status(errorCode.getStatus())
				.body(ErrorResponse.from(errorCode));
	}

	@ExceptionHandler({
			MissingServletRequestParameterException.class,
			MethodArgumentTypeMismatchException.class,
			IllegalArgumentException.class
	})
	public ResponseEntity<ErrorResponse> handleBadRequest(Exception exception) {
		return ResponseEntity
				.status(ErrorCode.INVALID_REQUEST.getStatus())
				.body(ErrorResponse.from(ErrorCode.INVALID_REQUEST));
	}
}
