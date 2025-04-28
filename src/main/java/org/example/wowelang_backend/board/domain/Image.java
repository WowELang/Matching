package org.example.wowelang_backend.board.domain;

import jakarta.persistence.*;
import lombok.*;
import org.example.wowelang_backend.common.BaseEntity;

@Getter
@Entity
@Builder
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
public class Image extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "file_id")
    private Long id;

    @Column(name = "image_key", unique = true)
    private String imageKey;

    @Column(name = "image_url")
    private String imageUrl;

    @Column(name = "is_posted")
    private Boolean isPosted;


}
