package org.example.wowelang_backend.board.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.data.domain.Slice;

import java.util.List;

@Getter
@AllArgsConstructor
public class PageResponseDTO<T> {

    private List<T> content;
    private boolean hasNext;
    private int page;
    private int size;

    public static <T> PageResponseDTO<T> from (Slice<T> slice) {
        return new PageResponseDTO<>(
                slice.getContent(),
                slice.hasNext(),
                slice.getNumber(),
                slice.getSize()
        );
    }
}
