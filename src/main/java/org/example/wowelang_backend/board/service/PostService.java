package org.example.wowelang_backend.board.service;


import org.example.wowelang_backend.board.domain.Board;
import org.example.wowelang_backend.board.domain.Post;
import org.example.wowelang_backend.board.dto.*;
import org.example.wowelang_backend.board.repository.BoardRepository;
import org.example.wowelang_backend.board.repository.PostRepository;
import org.example.wowelang_backend.user.domain.User;
import org.example.wowelang_backend.user.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Slice;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import static org.example.wowelang_backend.common.apiPayLoad.status.ErrorStatus.*;

@Service
public class PostService {

    @Autowired
    private final PostRepository postRepository;
    private final BoardRepository boardRepository;
    private final UserRepository userRepository;

    public PostService(PostRepository postRepository, BoardRepository boardRepository, UserRepository userRepository) {
        this.postRepository = postRepository;
        this.boardRepository = boardRepository;
        this.userRepository = userRepository;
    }

    @Transactional
    public PageResponseDTO<PostResponseDTO> getPostList(Long boardId, Pageable pageable) throws Exception {

        Board board = boardRepository.findById(boardId)
                .orElseThrow(() -> new IllegalArgumentException(BOARD_NOT_FOUND.getMessage()));

        Slice<Post> slice = postRepository.findAllByBoardAndIsDeleteFalse(board, pageable);

        // TODO: 커스텀 예외처리 필요합니다.
        if(slice.getContent().isEmpty() && pageable.getPageNumber()==0) {
            throw new Exception(POST_NO_CONTENT.getMessage());
        } else if (slice.getContent().isEmpty() && pageable.getPageNumber()>0) {
            throw new Exception(POST_NO_MORE.getMessage());
        }

        return PageResponseDTO.from(slice.map(PostResponseDTO::from));
    }

    @Transactional
    public Long createPost(Long boardId, PostCreateDTO postCreateDto) {

        Board board = boardRepository.findById(boardId)
                .orElseThrow(() -> new IllegalArgumentException(BOARD_NOT_FOUND.getMessage()));

        // TODO: 인증 로직과 합친 후 변경 예정
        User user = userRepository.findById(1L)
                .orElseThrow(() -> new IllegalArgumentException(("등록되지 않은 유저입니다.")));

        Post post = Post.createPost(postCreateDto, user, board);

        postRepository.save(post);
        return post.getId();
    }

    @Transactional
    public PostResponseDTO.PostDetailDTO getPost(Long postId) {

        postRepository.upPostViews(postId);

        Post afterUpdatePost = postRepository.findByIdAndIsDeleteFalse(postId)
                .orElseThrow(() -> new IllegalArgumentException(POST_NOT_FOUND.getMessage()));

        return PostResponseDTO.PostDetailDTO.from(afterUpdatePost);
    }

    @Transactional
    public PostUpdateResponseDTO updatePost(Long postId, PostUpdateDTO postUpdateDto) {

        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new IllegalArgumentException(POST_NOT_FOUND.getMessage()));

        post.updatePost(postUpdateDto.getTitle(), postUpdateDto.getContent());

        return PostUpdateResponseDTO.from(post);
    }

    @Transactional
    public void deletePost(Long postId) {
        Post post = postRepository.findByIdAndIsDeleteFalse(postId)
                .orElseThrow(() -> new IllegalArgumentException(POST_NOT_FOUND.getMessage()));

        post.softDeletePost();
    }
}