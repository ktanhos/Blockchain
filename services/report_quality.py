"""Quality gates for the generated Word report.

The checker validates the report package before export. It never changes a case
result merely to make the report pass.
"""
from __future__ import annotations

from services.instruction_engine import validate_case01, validate_case02, validate_case03
from services.consistency import check_consistency
from services.report_builder import REPORT_SECTIONS, word_count


def _nonempty(value) -> bool:
    return bool(str(value or "").strip())


def _table_rows(value) -> int:
    return len(value) if isinstance(value, (list, tuple)) else 0


def build_quality_report(profile, financials, case01, case02, case03, report):
    checks = []

    def add(code, item, passed, detail, severity="Lỗi"):
        checks.append({
            "Mã": code,
            "Hạng mục": item,
            "Trạng thái": "Đạt" if passed else severity,
            "Chi tiết": detail,
        })

    c1 = validate_case01(case01)
    c2 = validate_case02(case02)
    c3 = validate_case03(case03)
    add("Q01", "Case 01 đáp ứng Instruction", all(c1.values()), f"{sum(c1.values())}/{len(c1)} yêu cầu")
    add("Q02", "Case 02 đáp ứng Instruction", all(c2.values()), f"{sum(c2.values())}/{len(c2)} yêu cầu")
    add("Q03", "Case 03 đáp ứng Instruction", all(c3.values()), f"{sum(c3.values())}/{len(c3)} yêu cầu")

    consistency = check_consistency(profile, financials, case01, case02, case03)
    consistency_errors = [r for r in consistency if r.get("Trạng thái") == "Lỗi"]
    add("Q04", "Consistency Checker", not consistency_errors,
        "Không còn lỗi liên kết ba Case" if not consistency_errors else f"Còn {len(consistency_errors)} lỗi liên kết")

    required_profile = ["student_id", "industry", "business_type", "banking_problem", "funding_instrument", "business_description"]
    missing_profile = [k for k in required_profile if not _nonempty(profile.get(k))]
    add("Q05", "Hồ sơ doanh nghiệp đầy đủ", not missing_profile,
        "Đủ thông tin hồ sơ" if not missing_profile else "Thiếu: " + ", ".join(missing_profile))

    missing_report = [s["title"] for s in REPORT_SECTIONS if not _nonempty(report.get(s["id"], ""))]
    add("Q06", "Không còn phần phân tích để trống", not missing_report,
        "Đã có nội dung cho toàn bộ chương" if not missing_report else "Chưa viết: " + "; ".join(missing_report))

    total_words = sum(word_count(report.get(s["id"], "")) for s in REPORT_SECTIONS)
    add("Q07", "Khối lượng nội dung chính", total_words >= 6500,
        f"{total_words:,} từ; mục tiêu báo cáo 30 đến 40 trang cần nội dung đủ dài",
        severity="Cảnh báo")
    add("Q08", "Không dùng văn bản hướng dẫn thay cho phân tích", not any("[Sinh viên bổ sung" in str(report.get(s["id"], "")) for s in REPORT_SECTIONS),
        "Không phát hiện placeholder" if not any("[Sinh viên bổ sung" in str(report.get(s["id"], "")) for s in REPORT_SECTIONS) else "Còn placeholder trong phần phân tích")

    numeric_keys = ["V", "LoanAmount", "ExternalCapital", "EBITDA1", "DebtService1", "DSCR", "CollateralValue", "LTV"]
    numeric_ok = all(k in financials for k in numeric_keys)
    add("Q09", "Bộ số liệu tài chính chuẩn hóa", numeric_ok,
        "Đủ biến tài chính để đưa vào báo cáo" if numeric_ok else "Thiếu một hoặc nhiều biến tài chính")

    has_investor = bool(case03.get("investor_return")) or _nonempty(case03.get("investor_return_text"))
    add("Q10", "Lợi ích nhà đầu tư", has_investor,
        "Đã có dữ liệu lợi ích nhà đầu tư" if has_investor else "Cần bổ sung hoặc xác nhận bảng lợi ích nhà đầu tư")

    add("Q11", "KPI", _table_rows(case03.get("kpis", [])) >= 10 or _table_rows(case01.get("kpis", [])) >= 10 or _table_rows(case02.get("kpis", [])) >= 10,
        "Có tối thiểu 10 KPI" if (_table_rows(case03.get("kpis", [])) >= 10 or _table_rows(case01.get("kpis", [])) >= 10 or _table_rows(case02.get("kpis", [])) >= 10) else "Chưa có bảng KPI tối thiểu 10 dòng",
        severity="Cảnh báo")

    risk_count = _table_rows(case01.get("risks", [])) + _table_rows(case02.get("risks", [])) + _table_rows(case03.get("risks", []))
    add("Q12", "Risk Register tích hợp", risk_count >= 15,
        f"Tổng số dòng rủi ro nguồn: {risk_count}; Heat Map sẽ sử dụng các dòng có P và I",
        severity="Cảnh báo")

    return checks, consistency


def quality_summary(checks):
    errors = sum(x["Trạng thái"] == "Lỗi" for x in checks)
    warnings = sum(x["Trạng thái"] == "Cảnh báo" for x in checks)
    return {"total": len(checks), "errors": errors, "warnings": warnings, "pass": errors == 0}
