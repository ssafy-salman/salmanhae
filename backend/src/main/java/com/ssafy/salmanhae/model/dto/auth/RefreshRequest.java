package com.ssafy.salmanhae.model.dto.auth;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;

@Getter
public class RefreshRequest {
    @NotBlank
    private String refreshToken;
}
