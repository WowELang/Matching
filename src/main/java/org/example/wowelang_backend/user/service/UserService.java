package org.example.wowelang_backend.user.service;

import lombok.RequiredArgsConstructor;
import org.example.wowelang_backend.common.apiPayLoad.status.ErrorStatus;
import org.example.wowelang_backend.user.domain.ForeignTuteeAttribute;
import org.example.wowelang_backend.user.domain.KoreanTutorAttribute;
import org.example.wowelang_backend.user.domain.User;
import org.example.wowelang_backend.user.domain.Usertype;
import org.example.wowelang_backend.user.dto.UserSignupReqDto;
import org.example.wowelang_backend.user.dto.VerificationDto;
import org.example.wowelang_backend.user.repository.ForeignTuteeRepository;
import org.example.wowelang_backend.user.repository.KoreanTutorRepository;
import org.example.wowelang_backend.user.repository.UserRepository;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.ResponseEntity;
//import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Transactional
public class UserService {

    private final UserRepository userRepository;
    private final KoreanTutorRepository koreanTutorRepository;
    private final ForeignTuteeRepository foreignTuteeRepository;
    //private final PasswordEncoder passwordEncoder;
    private final UnivcertService univcertService;

    // 1단계: 기본 정보 입력 후 임시 사용자 생성
    // 기본정보는 저장하지만 이메일 인증은 되지 않은 상태
    public Long createTempUser(UserSignupReqDto dto) {
        //이메일, 로그인 아이디 중복체크
        if (userRepository.existsByEmail(dto.getEmail())) {
            throw new IllegalArgumentException(ErrorStatus.DUPLICATE_EMAIL.getMessage());
        }
        if (userRepository.existsByLoginId(dto.getLoginId())) {
            throw new IllegalArgumentException(ErrorStatus.LOGINID_DUPLICATE.getMessage());
        }


        //임시 사용자 생성(isEmailVerified 기본값 false)
        User user = User.builder()
                .loginId(dto.getLoginId())
                .email(dto.getEmail())
                //.password(passwordEncoder.encode(dto.getPassword()))
                .password(dto.getPassword())//로그인 구현시 변경
                .name(dto.getName())
                .birthday(dto.getBirthday())
                .major(dto.getMajor())
                .gender(dto.getGender())
                .usertype(dto.getUsertype())
                .isEmailVerified(false)
                .build();

        userRepository.save(user); // 유저 타입에 따라 외국인이면 바로 가입, 재학생이면 메일인증으로 진행

        //유저타입별 추가 정보(이후 최종 가입 단계에서 사용)
        if (dto.getUsertype() == Usertype.NATIVE) {//재학생
            KoreanTutorAttribute tutor = KoreanTutorAttribute.builder()
                    .user(user)
                    .reputation(0L)
                    .fixCount(0L)
                    .build();
            koreanTutorRepository.save(tutor);

        } else if (dto.getUsertype() == Usertype.FOREIGN) {//유학생
            ForeignTuteeAttribute tutee = ForeignTuteeAttribute.builder()
                    .user(user)
                    .country(dto.getCountry())
                    .build();
            foreignTuteeRepository.save(tutee);
        }

        return user.getId();
    }

    // 2단계: 재학생 튜터일 경우, 인증 진행
    public boolean sendVerificationEmail(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException(ErrorStatus.USER_NOT_FOUND.getMessage()));
        if (user.getUsertype() == Usertype.FOREIGN) {
            // 유학생은 메일 인증이 필요 없음
            return true;
        }
        //재학생일 때만 진행
        if (!Boolean.TRUE.equals(user.getIsEmailVerified())) { //인증된 적이 없는 유저면 우선적으로 메일 전송 여부를 초기화.
            clearCertification(user.getEmail());
        }

        boolean mailSent = univcertService.sendCertifyMail(user.getEmail());
        if (!mailSent) {
            throw new IllegalStateException(ErrorStatus.CERTIFICATION_MAIL_FAILED.getMessage());
        }

        return mailSent; // true 반환
    }

    /*
    2-1단계: 인증 코드 검증 및 대학 이메일 인증 업데이트
    @param dto 인증 요청 정보를 담은 DTO (userId, univEmail, univName, code)
    */
    public boolean verifyUnivEmail(VerificationDto dto) {
        User user = userRepository.findById(dto.getUserId())
                .orElseThrow(() -> new IllegalArgumentException(ErrorStatus.USER_NOT_FOUND.getMessage()));

        if (user.getUsertype() != Usertype.NATIVE) {
            throw new IllegalArgumentException(ErrorStatus.ONLY_NATIVE_EMAIL_AUTH_REQUIRED.getMessage());
        }

        boolean success = univcertService.verifyCode(user.getEmail(), dto.getCode());

        if (!success) {
            throw new IllegalStateException(ErrorStatus.CERTIFICATION_CODE_MISMATCH.getMessage());
        }
        user.setIsEmailVerified(true);
        userRepository.save(user);
        return true;
    }

    //3단계: 최종 회원가입 완료 처리
    public Long completeSignUp(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException(ErrorStatus.USER_NOT_FOUND.getMessage()));

        if ((user.getUsertype() == Usertype.NATIVE) && (!user.getIsEmailVerified())) {
            throw new IllegalStateException(ErrorStatus.EMAIL_NOT_VERIFIED.getMessage());
        }

        //이후 추가 로직 구현 가능 ex) 캐릭터 선택..
        return user.getId();
    }

    //인증된 이메일 초기화
    public String clearCertification(String email) {
        try {
            Map<String, Object> resp = univcertService.clear(email);
            boolean success = Boolean.TRUE.equals(resp.get("success"));
            if (!success) {
                throw new IllegalStateException(ErrorStatus.UNIVCERT_CLEAR_FAILED.getMessage() + ": " + resp.get("message"));
            }
        } catch (IOException e) {
            throw new IllegalStateException("UnivCert clear API 호출 오류", e);
        }
        return "인증 상태가 초기화되었습니다.";
    }

    //아이디 중복확인
    public void checkLoginId(String loginId) {
        if (userRepository.existsByLoginId(loginId)) {
            throw new IllegalArgumentException(ErrorStatus.LOGINID_DUPLICATE.getMessage());
        }
    }
}