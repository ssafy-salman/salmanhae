package com.ssafy.salmanhae.model.dto.auth;

import lombok.Getter;

@Getter
public class SignupRequest {
    private String email;
    private String password;
    private String nickname;
}
