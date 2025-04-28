package org.example.wowelang_backend.board.dto;

import lombok.Getter;
import lombok.experimental.SuperBuilder;
import org.example.wowelang_backend.board.domain.Post;
import org.example.wowelang_backend.board.domain.Reply;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@SuperBuilder
public class PostResponseDTO {

    private Long id;
    private String title;
    private String content;
    private Long replyCnt;
    private Long views;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public static PostResponseDTO from(Post post) {
        return PostResponseDTO.builder()
                .id(post.getId())
                .title(post.getTitle())
                .content(post.getContent())
                .replyCnt(post.getReplyCnt())
                .views(post.getViews())
                .createdAt(post.getCreatedAt())
                .updatedAt(post.getUpdatedAt())
                .build();
    }

    @Getter
    @SuperBuilder
    public static class PostDetailDTO extends PostResponseDTO {

        // TODO: ReplyDTO로 가져오기
        private List<Reply> reply;

        public static PostDetailDTO from(Post post) {
            return PostDetailDTO.builder()
                    .id(post.getId())
                    .title(post.getTitle())
                    .content(post.getContent())
                    .replyCnt(post.getReplyCnt())
                    .views(post.getViews())
                    .createdAt(post.getCreatedAt())
                    .updatedAt(post.getUpdatedAt())
                    .reply(post.getReply())
                    .build();
        }
    }
}
