package org.example.wowelang_backend.user.dto;

import lombok.*;
import org.example.wowelang_backend.user.domain.Gender;
import org.example.wowelang_backend.user.domain.Usertype;

import java.time.LocalDate;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserSignupReqDto {

    //공용 사항
    private String loginId;
    private String email;
    private String password;
    private String name;
    private LocalDate birthday;
    private String major;
    private Gender gender;
    private Usertype usertype;

    //유학생 튜티 국적 정보
    private String country;

    //재학생 인증 대학 이름 정보
    private String univName;
}
