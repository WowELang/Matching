package org.example.wowelang_backend.board.service;

import org.example.wowelang_backend.board.dto.BoardListResponseDTO;
import org.example.wowelang_backend.board.repository.BoardRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class BoardService {

    @Autowired
    private final BoardRepository boardRepository;

    public BoardService (BoardRepository boardRepository) {
        this.boardRepository = boardRepository;
    }

    public List<BoardListResponseDTO> getBoardList() {

        return boardRepository.findAll().stream()
                .map(BoardListResponseDTO::of)
                .toList();
    }
}
