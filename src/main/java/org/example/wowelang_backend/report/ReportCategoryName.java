package org.example.wowelang_backend.report;

/**
 * 상업적 광고 및 판매 → Commercial Advertising & Sales
 * 유출 / 사칭 / 사기 → Leakage / Impersonation / Fraud
 * 음란물 / 불건전한 만남 및 대화 → Obscene Content / Inappropriate Meetings & Conversations
 * 낚시 / 놀람 / 도배 → Phishing / Shock Content / Spam
 * 욕설 / 비하 → Profanity / Defamation
 * 기타 → Other
 *
 * 일단 알파벳만 따왔어요
 */

public enum ReportCategoryName {
    CAS,
    LIF,
    OM,
    PSS,
    PD,
    OTHER
}
