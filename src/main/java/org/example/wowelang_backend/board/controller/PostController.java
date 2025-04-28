package org.example.wowelang_backend.board.controller;

import org.example.wowelang_backend.board.dto.*;
import org.example.wowelang_backend.board.service.PostService;
import org.example.wowelang_backend.common.apiPayLoad.ApiResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/post")
public class PostController {

    @Autowired
    private final PostService postService;

    public PostController(PostService postService) {
        this.postService = postService;
    }

    @GetMapping("/list")
    public ApiResponse<PageResponseDTO<PostResponseDTO>> getPostList(@RequestParam Long boardId, @PageableDefault(page = 0, size = 10, sort = "updatedAt", direction = Sort.Direction.DESC) Pageable pageable) throws Exception {

        return ApiResponse.onSuccess(postService.getPostList(boardId, pageable));
    }

    @PostMapping("")
    public ApiResponse<Long> createPost(@RequestParam Long boardId,
                                        @RequestBody PostCreateDTO postCreateDto) {

        return ApiResponse.created(postService.createPost(boardId, postCreateDto));
    }

    @GetMapping("/{postId}")
    public ApiResponse<PostResponseDTO.PostDetailDTO> getPost(@PathVariable Long postId) {

        return ApiResponse.onSuccess(postService.getPost(postId));
    }

    @PatchMapping("/{postId}")
    public ApiResponse<PostUpdateResponseDTO> updatePost(@PathVariable Long postId,
                                                        @RequestBody PostUpdateDTO postUpdateDto) {

        return ApiResponse.onSuccess(postService.updatePost(postId, postUpdateDto));
    }

    @DeleteMapping("/{postId}")
    public ResponseEntity<Void> deletePost(@PathVariable Long postId) {
        postService.deletePost(postId);

        // TODO: 추후 커스텀 응답 추가
        return ResponseEntity.noContent().build();
    }
}