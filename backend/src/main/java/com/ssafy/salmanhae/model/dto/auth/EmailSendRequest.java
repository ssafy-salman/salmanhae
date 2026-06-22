package com.ssafy.salmanhae.model.dto.auth;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.Getter;

@Getter
public class EmailSendRequest {
    @NotBlank
    @Email
    private String email;
}
