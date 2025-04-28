package org.example.wowelang_backend.common.apiPayLoad.exception;

import jakarta.servlet.http.HttpServletRequest;
import org.example.wowelang_backend.common.apiPayLoad.ApiResponse;
import org.example.wowelang_backend.common.apiPayLoad.GlobalResponseDTO;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.context.request.ServletWebRequest;
import org.springframework.web.context.request.WebRequest;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

// RestController 붙은 클래스들만 에러처리 해준다!
@RestControllerAdvice(annotations = {RestController.class})
public class ExceptionAdvice extends ResponseEntityExceptionHandler {


    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<?> handleIlleglArgumentException(IllegalArgumentException e, HttpServletRequest request) {
        GlobalResponseDTO errorResponseHttpStatus = GlobalResponseDTO.builder()
                .isSuccess(false)
                .httpStatus(HttpStatus.BAD_REQUEST)
                .message(e.getMessage())
                .build();

        return handleExceptionInternal(e, errorResponseHttpStatus, null, request);
    }

    private ResponseEntity<Object> handleExceptionInternal(Exception e, GlobalResponseDTO globalResponse, HttpHeaders headers, HttpServletRequest httpServletRequest) {
        WebRequest webRequest = new ServletWebRequest(httpServletRequest);
        return handleExceptionInternal(e, globalResponse, headers, globalResponse.getHttpStatus(), webRequest);
    }

    private ResponseEntity<Object> handleExceptionInternal(Exception e, GlobalResponseDTO globalResponse, HttpHeaders headers, WebRequest request) {
        ApiResponse<Object> body = ApiResponse.onFail(globalResponse.getHttpStatus(), globalResponse.getMessage(), null );
        return super.handleExceptionInternal(
                e,
                body,
                headers,
                globalResponse.getHttpStatus(),
                request
        );
    }


}
