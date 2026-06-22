package com.ssafy.salmanhae.model.dto.auth;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class RefreshResponse {
    private String accessToken;
    private String refreshToken;
}
