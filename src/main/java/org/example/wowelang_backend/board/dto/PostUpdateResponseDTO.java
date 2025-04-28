package org.example.wowelang_backend.board.dto;

import lombok.Builder;
import lombok.Getter;
import org.example.wowelang_backend.board.domain.Post;

import java.time.LocalDateTime;

@Getter
@Builder
public class PostUpdateResponseDTO {

    private String title;
    private String content;

    public static PostUpdateResponseDTO from(Post post) {
        return PostUpdateResponseDTO.builder()
                .title(post.getTitle())
                .content(post.getContent())
                .build();
    }

}
