package com.ssafy.salmanhae.model.dto.auth;

import lombok.Getter;

@Getter
public class EmailVerifyRequest {
    private String email;
    private String code;
}
