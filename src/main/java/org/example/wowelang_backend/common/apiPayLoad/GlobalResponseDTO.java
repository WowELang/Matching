package org.example.wowelang_backend.common.apiPayLoad;

import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import lombok.Builder;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public class GlobalResponseDTO {

    private final Boolean isSuccess;
    private final HttpStatus httpStatus;
    private final String message;

    @Builder
    public GlobalResponseDTO(Boolean isSuccess, HttpStatus httpStatus, String message) {
        this.isSuccess = isSuccess;
        this.httpStatus = httpStatus;
        this.message = message;
    }
}
