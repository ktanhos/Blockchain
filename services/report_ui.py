import json
import pandas as pd
import streamlit as st

from database import load_project, save_project
from services.report_builder import REPORT_SECTIONS, default_report, report_word_count, suggested_text, word_count
from services.instruction_engine import validate_case01, validate_case02, validate_case03
from services.consistency import check_consistency
from services.report_docx import build_docx


def _records_for_section(section_id, case01, case02, case03):
    if section_id == "part1":
        return [("Hồ sơ doanh nghiệp", [{"Thông số": "Mô tả hoạt động", "Giá trị": case01.get("business_description", "")}])]
    if section_id == "part2":
        return [("As-is Process", case01.get("as_is", []))]
    if section_id == "part3":
        return [("Đánh giá CSDL và Blockchain/DLT", case01.get("assessment", [])), ("Ma trận quyền", case01.get("permissions", [])), ("On-chain và Off-chain", case01.get("data", [])), ("Risk Register Case 01", case01.get("risks", []))]
    if section_id == "part4":
        return [("To-be Process", case02.get("to_be", [])), ("Oracle", case02.get("oracle", [])), ("Ba kịch bản", [{"Kịch bản": x} for x in case02.get("scenarios", [])]), ("Risk Register Case 02", case02.get("risks", []))]
    if section_id == "part5":
        term_sheet = [{"Trường": "Tên doanh nghiệp", "Giá trị": case03.get("business_name", "")}, {"Trường": "Tên dự án", "Giá trị": case03.get("project_name", "")}, {"Trường": "Tên token", "Giá trị": case03.get("token_name", "")}, {"Trường": "Mã token", "Giá trị": case03.get("token_code", "")}, {"Trường": "Giá phát hành", "Giá trị": case03.get("issue_price", "")}, {"Trường": "Lợi suất giả định", "Giá trị": case03.get("annual_return_rate", "")}, {"Trường": "Hạn chế chuyển nhượng", "Giá trị": case03.get("transfer_restrictions", "")}, {"Trường": "Thứ tự ưu tiên thanh toán", "Giá trị": case03.get("payment_priority", "")}]
        scenarios = [{"Kịch bản": x} for x in case03.get("scenarios", ["Cơ sở", "Tăng trưởng", "Suy giảm"])]
        return [("Term Sheet", term_sheet), ("Vòng đời token", case03.get("lifecycle", [])), ("Ba kịch bản", scenarios), ("Risk Register Case 03", case03.get("risks", []))]
    if section_id == "part6":
        return [("Rủi ro Case 01", case01.get("risks", [])), ("Rủi ro Case 02", case02.get("risks", [])), ("Rủi ro Case 03", case03.get("risks", []))]
    return []


def _show_records(title, records):
    if not records:
        st.caption(f"Chưa có dữ liệu {title}.")
        return
    st.markdown(f"**{title}**")
    if isinstance(records, list) and records and not isinstance(records[0], dict):
        records = [{"Giá trị": x} for x in records]
    st.dataframe(pd.DataFrame(records), width="stretch", hide_index=True)


def render_report_builder(st_module, project_id, student_id, profile, financials, case01, case02, case03):
    project = load_project(project_id) or {}
    report = project.get("report") or default_report()
    for section in REPORT_SECTIONS:
        report.setdefault(section["id"], "")

    consistency = check_consistency(profile, financials, case01, case02, case03)
    errors = sum(r.get("Trạng thái") == "Lỗi" for r in consistency)
    c1 = validate_case01(case01); c2 = validate_case02(case02); c3 = validate_case03(case03)
    instruction_done = sum(c1.values()) + sum(c2.values()) + sum(c3.values()); instruction_total = len(c1) + len(c2) + len(c3); instruction_pct = instruction_done / instruction_total if instruction_total else 0

    st.markdown("## Report Builder")
    st.caption("Xây dựng báo cáo theo đúng cấu trúc trong Instruction File. Case 01, Case 02 và Case 03 được tự động liên kết; sinh viên tập trung viết phân tích và nhận xét.")
    m1, m2, m3, m4 = st.columns(4); m1.metric("Hoàn thiện yêu cầu", f"{instruction_pct * 100:.0f}%"); m2.metric("Từ đã viết", f"{report_word_count(report):,}"); m3.metric("Kiểm tra còn lỗi", errors); m4.metric("Số phần", len(REPORT_SECTIONS)); st.progress(instruction_pct)
    if errors: st.warning(f"Còn {errors} điểm liên kết cần xử lý. Report Builder không tự che các điểm này.")
    else: st.success("22 kiểm tra liên kết không còn lỗi.")

    section_labels = [f"{i + 1}. {s['title']}" for i, s in enumerate(REPORT_SECTIONS)]
    selected = st.selectbox("Chọn phần đang viết", section_labels, key="report_section_selector")
    section = REPORT_SECTIONS[section_labels.index(selected)]; sid = section["id"]
    left, right = st.columns([1.7, 1], gap="large")
    with left:
        st.markdown(f"### {section['title']}")
        target_words = section.get("target_words"); size_note = f" {target_words}." if target_words else ""
        st.caption(f"Quy mô theo Instruction: {section['target_pages']}.{size_note}")
        with st.expander("Câu hỏi hướng dẫn", expanded=True):
            for i, question in enumerate(section["questions"], 1): st.markdown(f"**{i}.** {question}")
        text_key = f"report_text_{sid}"
        if text_key not in st.session_state: st.session_state[text_key] = report.get(sid, "")
        b1, b2 = st.columns(2)
        if b1.button("Gợi ý từ dữ liệu", key=f"suggest_{sid}"):
            st.session_state[text_key] = suggested_text(sid, profile, financials, case01, case02, case03); st.rerun()
        if b2.button("Xóa phần này", key=f"clear_{sid}"):
            st.session_state[text_key] = ""; st.rerun()
        report[sid] = st.text_area("Phân tích và nhận xét của sinh viên", key=text_key, height=380, placeholder="Viết lập luận của bạn tại đây. App cung cấp câu hỏi và dữ liệu, không thay thế phần phân tích.")
        st.caption(f"Số từ: {word_count(report[sid]):,}")
        if st.button("Lưu phần này", type="primary", key=f"save_report_{sid}"):
            save_project(project_id, student_id, profile, case01, case02, case03, report); st.success("Đã lưu phần báo cáo.")
    with right:
        with st.container(border=True):
            st.markdown("### Trợ lý viết"); st.write("Bắt đầu từ câu hỏi của Instruction, sau đó dùng số liệu và bảng đã làm để lập luận."); st.info("Cấu trúc một đoạn nên là: nhận định → dữ liệu → giải thích → tác động → kết luận.")
        with st.expander("Dữ liệu tự động từ Case", expanded=True):
            arch = case01.get("architecture", {}); st.write(f"Blockchain: {arch.get('blockchain_type', '')}"); st.write(f"Đồng thuận: {arch.get('consensus', '')}"); st.write(f"Tổng nhu cầu vốn: {financials.get('V', 0):,.2f} tỷ đồng"); st.write(f"Khoản vay: {financials.get('LoanAmount', 0):,.2f} tỷ đồng"); st.write(f"Vốn còn thiếu: {financials.get('ExternalCapital', 0):,.2f} tỷ đồng")
            if sid == "part4": st.write(f"DSCR: {case02.get('DSCR', financials.get('DSCR', ''))}"); st.write(f"LTV: {case02.get('LTV', financials.get('LTV', ''))}")
            if sid == "part5": st.write(f"Công cụ huy động: {profile.get('funding_instrument', '')}")
            for title, rows in _records_for_section(sid, case01, case02, case03): _show_records(title, rows)

    st.divider(); st.markdown("### Xem trước báo cáo"); st.caption("Các bảng và số liệu được tự động đặt vào đúng chương. Phần chữ lấy từ nội dung sinh viên đã viết.")
    for i, s in enumerate(REPORT_SECTIONS, 1):
        with st.expander(f"{i}. {s['title']}", expanded=False):
            text = report.get(s["id"], "")
            if text: st.write(text)
            else: st.warning("Chưa có phần phân tích.")
            for title, rows in _records_for_section(s["id"], case01, case02, case03): _show_records(title, rows)

    if st.button("Lưu toàn bộ Report Builder", type="primary", key="save_all_report"):
        save_project(project_id, student_id, profile, case01, case02, case03, report); st.success("Đã lưu toàn bộ nội dung báo cáo.")
    save_project(project_id, student_id, profile, case01, case02, case03, report)
    docx_bytes = build_docx(profile, financials, case01, case02, case03, report, consistency)
    st.download_button("Tải báo cáo Word để tiếp tục chỉnh sửa", data=docx_bytes, file_name=f"Bao_cao_Blockchain_{''.join(ch for ch in student_id if ch.isdigit())}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", width="stretch")
    project_json = {"student_id": student_id, "profile": profile, "financials": financials, "case01": case01, "case02": case02, "case03": case03, "report": report, "consistency": consistency}
    st.download_button("Sao lưu toàn bộ dự án", data=json.dumps(project_json, ensure_ascii=False, indent=2, default=str), file_name=f"Blockchain_Project_{''.join(ch for ch in student_id if ch.isdigit())}.json", mime="application/json", width="stretch")
