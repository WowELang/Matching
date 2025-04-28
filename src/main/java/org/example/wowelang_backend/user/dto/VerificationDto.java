package org.example.wowelang_backend.user.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class VerificationDto {
    private Long userId;
    private String univEmail;
    private String univName;
    private int code;
}
