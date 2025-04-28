package org.example.wowelang_backend.board.controller;

import lombok.RequiredArgsConstructor;
import org.example.wowelang_backend.board.dto.BoardListResponseDTO;
import org.example.wowelang_backend.board.service.BoardService;
import org.example.wowelang_backend.common.apiPayLoad.ApiResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/board")
public class BoardController {

    @Autowired
    private final BoardService boardService;

    public BoardController (BoardService boardService) {
        this.boardService = boardService;
    }

    @GetMapping("/list")
    public ApiResponse<List<BoardListResponseDTO>> getBoardList() {

        return ApiResponse.onSuccess(boardService.getBoardList());
    }

}