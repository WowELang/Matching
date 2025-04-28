package org.example.wowelang_backend.board.dto;

import lombok.Builder;
import lombok.Getter;
import org.example.wowelang_backend.board.domain.Board;

@Getter
public class BoardListResponseDTO {

    private final Long id;
    private final String boardName;

    @Builder
    public BoardListResponseDTO(Long id, String boardName) {
        this.id = id;
        this.boardName = boardName;
    }

    public static BoardListResponseDTO of(Board board) {
        return BoardListResponseDTO.builder()
                .id(board.getId())
                .boardName(board.getBoardName())
                .build();
    }
}