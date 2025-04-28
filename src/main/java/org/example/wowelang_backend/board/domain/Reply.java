package org.example.wowelang_backend.board.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.example.wowelang_backend.common.BaseEntity;
import org.example.wowelang_backend.user.domain.User;

@Getter
@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Reply extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "reply_id")
    private Long id;

    private String content;

    @Column(name = "is_delete")
    private Boolean isDelete;

    private Long child;

    private Long next;

    @ManyToOne
    @JoinColumn(name = "post_id")
    private Post post;

//    TODO: fetchType Lazy로 바꾸기?
//    @ManyToOne
//    @JoinColumn(name = "user_id")
//    private User user;
}

