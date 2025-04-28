package org.example.wowelang_backend.user.domain;

import jakarta.persistence.*;
import lombok.*;

@Getter
@Setter
@Entity
@Table
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KoreanTutorAttribute {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "korean_tutor_attribute_id")
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", unique = true, nullable = false)// 단방향 매핑인지, 양방향 매핑인지 생각해보기
    private User user;

    //교정 관련 정보
    private Long reputation;
    private Long fixCount;
}
