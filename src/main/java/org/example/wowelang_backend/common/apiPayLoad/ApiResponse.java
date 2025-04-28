package org.example.wowelang_backend.common.apiPayLoad;

import lombok.AllArgsConstructor;
import lombok.Getter;
import org.example.wowelang_backend.common.apiPayLoad.status.ErrorStatus;
import org.example.wowelang_backend.common.apiPayLoad.status.SuccessStatus;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public class ApiResponse<T> {

    private Boolean isSuccess; // true / false
    private  int httpStatusCode; // 200, 404 같은 HTTP 코드
    private String message; // status에 맞는 메세지
    private T result; // 담겨지는 data들

    public static <T> ApiResponse<T> onSuccess(T result) {
        return new ApiResponse<>(true, SuccessStatus.OK.getHttpStatus().value(), SuccessStatus.OK.getMessage(), result);
    }

    public static <T> ApiResponse<T> created(T result) {
        return new ApiResponse<>(true, SuccessStatus.CREATED.getHttpStatus().value(), SuccessStatus.CREATED.getMessage(), result);
    }

    public static <T> ApiResponse<T> onFail(HttpStatus httpStatus, String message, T data) {
        return new ApiResponse<>(false, httpStatus.value(), message, data);
    }
}
