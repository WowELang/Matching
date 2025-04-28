package org.example.wowelang_backend.user.repository;

import org.example.wowelang_backend.user.domain.KoreanTutorAttribute;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface KoreanTutorRepository extends JpaRepository<KoreanTutorAttribute, Long> {
    Optional<KoreanTutorAttribute> findByUserId(Long userId); // User 엔티티의 pk
}
