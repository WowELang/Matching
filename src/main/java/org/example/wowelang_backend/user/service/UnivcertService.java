package org.example.wowelang_backend.user.service;

import com.univcert.api.UnivCert;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.Map;


//univcert 라이브러리를 사용해 인증 처리
@Service
public class UnivcertService {

    @Value("${UNIVCERT_API_KEY}")
    private String apiKey;

    //인증 메일 발송: 대학 이메일로 인증 메일 전송
    public boolean sendCertifyMail(String email) {
        try{
            //api 호출
            String univName = "홍익대학교"; //앱 구성상 대학교 정보 받는 곳이 없으므로 홍대로 고정, 추후 수정 가능
            boolean univCheck = true; //true -> 재학여부 확인
            Map<String, Object> response = UnivCert.certify(apiKey, email, univName, univCheck);
            System.out.println("[UnivCert] sendCertifyMail response = " + response);
            return parseSuccess(response);

        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    //인증 코드 검증: 사용자가 입력한 인증 코드를 univcert API로 확인
    public boolean verifyCode(String email, int code) {
        try {
            String univName = "홍익대학교"; // 인증메일 보내는 학교와 같은 학교
            Map<String, Object> response = UnivCert.certifyCode(apiKey, email, univName, code);
            System.out.println("[UnivCert] verifyCode response = " + response);
            return parseSuccess(response);
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    // Map에서 "success" 키의 값을 추출하여 인증의 성공 여부 판단
    private boolean parseSuccess(Map<String, Object> resultMap) {
        if (resultMap == null) return false;
        Object success = resultMap.get("success");
        if (success instanceof Boolean) {
            return (Boolean) success;
        }
        // 혹은 성공 여부가 문자열("true") 형태로 온다면,
        if (success instanceof String) {
            return Boolean.parseBoolean((String) success);
        }
        return false;
    }

    // 특정 이메일의 인증 상태 초기화
    public Map<String, Object> clear(String email) throws IOException {
        return UnivCert.clear(apiKey, email);
    }
}
