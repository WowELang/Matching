package org.example.wowelang_backend.board.repository;

import org.example.wowelang_backend.board.domain.Board;
import org.example.wowelang_backend.board.domain.Post;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Slice;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface PostRepository extends JpaRepository<Post,Long> {
    Slice<Post> findAllByBoardAndIsDeleteFalse(Board board, Pageable pageable);

    @Modifying(clearAutomatically = true)
    @Query("UPDATE Post p SET p.views = p.views + 1 WHERE p.id = :id")
    void upPostViews(@Param("id") Long postId);

    Optional<Post> findByIdAndIsDeleteFalse(Long postId);
}
