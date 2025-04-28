package org.example.wowelang_backend.common.apiPayLoad.status;

import lombok.AllArgsConstructor;
import lombok.Getter;
import org.example.wowelang_backend.common.apiPayLoad.BaseCode;
import org.example.wowelang_backend.common.apiPayLoad.GlobalResponseDTO;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum ErrorStatus implements BaseCode {

    // 본인이 담당한 부분에 맞게 에러코드를 작성해주세요

    // 인증관련 에러
    TOKEN_INVALID(HttpStatus.BAD_REQUEST, "토큰이 유효하지 않습니다."),

    // 게시글 관련 에러
    POST_NOT_CREATED(HttpStatus.BAD_REQUEST, "제목과 내용을 입력해주세요"),
    POST_NOT_FOUND(HttpStatus.NOT_FOUND, "해당 게시글을 찾을 수 없습니다."),
    POST_NO_CONTENT(HttpStatus.NO_CONTENT, "게시글이 존재하지 않습니다."),
    POST_NO_MORE(HttpStatus.NOT_FOUND, "게시글 페이지네이션의 끝입니다."),

    //게시판 관련 에러
    BOARD_NOT_FOUND(HttpStatus.NOT_FOUND, "해당 게시판을 찾을 수 없습니다."),

    //아이디, 이메일 중복 관련 에러
    DUPLICATE_EMAIL(HttpStatus.CONFLICT, "이미 등록된 이메일입니다."),
    LOGINID_DUPLICATE(HttpStatus.CONFLICT, "이미 사용 중인 아이디입니다."),

    // 사용자 관련 에러
    USER_NOT_FOUND(HttpStatus.NOT_FOUND, "해당 사용자가 존재하지 않습니다."),

    // 인증 관련 에러
    ONLY_NATIVE_EMAIL_AUTH_REQUIRED(HttpStatus.BAD_REQUEST, "재학생 튜터만 이메일 인증이 필요합니다."),
    CERTIFICATION_CODE_MISMATCH(HttpStatus.BAD_REQUEST, "인증 코드가 일치하지 않거나 만료되었습니다."),
    CERTIFICATION_MAIL_FAILED(HttpStatus.INTERNAL_SERVER_ERROR, "인증 메일 발송에 실패했습니다."),
    EMAIL_NOT_VERIFIED(HttpStatus.BAD_REQUEST, "이메일 인증이 완료되지 않았습니다."),
    UNIVCERT_CLEAR_FAILED(HttpStatus.INTERNAL_SERVER_ERROR, "UnivCert 초기화 실패");



    private final HttpStatus httpStatus;
    private final String message;

    @Override
    public GlobalResponseDTO getGlobalResponse() {
        return GlobalResponseDTO.builder()
                .isSuccess(false)
                .httpStatus(httpStatus)
                .message(message)
                .build();
    }
}
