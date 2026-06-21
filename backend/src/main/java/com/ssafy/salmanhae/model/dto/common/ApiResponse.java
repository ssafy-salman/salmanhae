package com.ssafy.salmanhae.model.dto.common;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class ApiResponse<T> {
    private T data;
    private String message;

    public static <T> ApiResponse<T> ok(T data) {
        return new ApiResponse<>(data, "OK");
    }

    public static ApiResponse<Void> ok() {
        return new ApiResponse<>(null, "OK");
    }
}