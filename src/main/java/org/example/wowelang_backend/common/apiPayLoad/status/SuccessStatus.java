package org.example.wowelang_backend.common.apiPayLoad.status;

import lombok.AllArgsConstructor;
import lombok.Getter;
import org.example.wowelang_backend.common.apiPayLoad.BaseCode;
import org.example.wowelang_backend.common.apiPayLoad.GlobalResponseDTO;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum SuccessStatus implements BaseCode {

    OK(HttpStatus.OK, "OK"),
    CREATED(HttpStatus.CREATED, "CREATED");

    private final HttpStatus httpStatus;
    private final String message;

    @Override
    public GlobalResponseDTO getGlobalResponse() {
        return GlobalResponseDTO.builder()
                .isSuccess(true)
                .httpStatus(httpStatus)
                .message(message)
                .build();
    }
}
