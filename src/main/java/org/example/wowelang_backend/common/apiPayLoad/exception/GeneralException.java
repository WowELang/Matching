package org.example.wowelang_backend.common.apiPayLoad.exception;

import lombok.Getter;
import org.example.wowelang_backend.common.apiPayLoad.GlobalResponseDTO;
import org.example.wowelang_backend.common.apiPayLoad.status.ErrorStatus;

@Getter
public class GeneralException extends RuntimeException {

    private final ErrorStatus errorStatus;

    public GeneralException(ErrorStatus errorStatus) {
        super(errorStatus.getMessage());
        this.errorStatus = errorStatus;
    }

    public GlobalResponseDTO getErrorStatus() {
        return this.errorStatus.getGlobalResponse();
    }
}
