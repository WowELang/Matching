package org.example.wowelang_backend.report;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.example.wowelang_backend.user.domain.User;

import java.time.LocalDateTime;

@Getter
@Entity
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Report {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "report_id")
    private Long id;

    @Column(name = "report_time")
    private LocalDateTime reportTime;

    @Column(name = "report_reason")
    private String reportReason;

    @ManyToOne
    @JoinColumn(name = "reporting_user_id")
    private User reportingUser;

    @ManyToOne
    @JoinColumn(name = "reported_user_id")
    private User reportedUser;

    @ManyToOne
    @JoinColumn(name = "report_category_id")
    private ReportCategory reportCategory;
}
