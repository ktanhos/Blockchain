import json
import pandas as pd
import streamlit as st

from database import load_project, save_project
from services.report_builder import REPORT_SECTIONS, default_report, report_word_count, suggested_text, word_count
from services.instruction_engine import validate_case01, validate_case02, validate_case03
from services.consistency import check_consistency
from services.report_quality import build_quality_report, quality_summary
from services.report_docx_enhanced import build_docx
from services.report_preview import preview_figures


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
        term_sheet = [{"Trường": "Tên doanh nghiệp", "Giá trị": case03.get("business_name", "")}, {"Trường": "Tên dự án", "Giá trị": case03.get("project_name", "")}, {"Trường": "Tên token", "Giá trị": case03.get("token_name", "")}, {"Trường": "Mã token", "Giá trị": case03.get("token_code", "")}, {"Trường": "Công cụ huy động", "Giá trị": case03.get("instrument", "")}, {"Trường": "Tài sản cơ sở", "Giá trị": case03.get("asset_base", "")}, {"Trường": "Giá phát hành", "Giá trị": case03.get("issue_price", "")}, {"Trường": "Lợi suất giả định", "Giá trị": case03.get("annual_return_rate", "")}, {"Trường": "Thứ tự ưu tiên thanh toán", "Giá trị": case03.get("payment_priority", "")}, {"Trường": "Cấu trúc pháp lý", "Giá trị": case03.get("legal_structure", "")}]
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
    if hasattr(records, "to_dict"):
        records = records.to_dict("records")
    elif isinstance(records, list) and records and not isinstance(records[0], dict):
        records = [{"Giá trị": x} for x in records]
    st.dataframe(pd.DataFrame(records), width="stretch", hide_index=True)


def _save_report(project_id, student_id, profile, case01, case02, case03, report):
    save_project(project_id, student_id, profile, case01, case02, case03, report)


def _show_diagram_preview(case01, case02, case03):
    st.divider()
    st.markdown("### Xem trước sơ đồ trước khi tạo Word")
    st.caption("Các hình dưới đây là đúng nguồn hình mà bộ xuất Word sử dụng. Nếu Word hiển thị không đúng, có thể chụp hoặc tải trực tiếp hình từ đây để đưa vào báo cáo thủ công.")
    figures = preview_figures(case01, case02, case03)
    names = list(figures.keys())
    tabs = st.tabs(names)
    for tab, name in zip(tabs, names):
        with tab:
            image = figures[name]
            st.image(image, width="stretch")
            st.download_button(f"Tải hình {name}", data=image.getvalue(), file_name=f"{name.replace(' ', '_').replace('/', '_')}.png", mime="image/png", key=f"download_figure_{name}")


def render_report_builder(st_module, project_id, student_id, profile, financials, case01, case02, case03):
    project = load_project(project_id) or {}
    report = project.get("report") or default_report()
    for section in REPORT_SECTIONS:
        report.setdefault(section["id"], "")

    consistency = check_consistency(profile, financials, case01, case02, case03)
    c1 = validate_case01(case01); c2 = validate_case02(case02); c3 = validate_case03(case03)
    instruction_done = sum(c1.values()) + sum(c2.values()) + sum(c3.values())
    instruction_total = len(c1) + len(c2) + len(c3)
    instruction_pct = instruction_done / instruction_total if instruction_total else 0
    quality_checks, quality_consistency = build_quality_report(profile, financials, case01, case02, case03, report)
    qs = quality_summary(quality_checks)

    st.markdown("## Report Builder")
    st.caption("Bộ xuất báo cáo 5 lớp: chuẩn hóa dữ liệu → chuẩn hóa nội dung → bảng Word thật → hình và mục lục tự động → Quality Gate trước khi xuất.")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Instruction", f"{instruction_pct * 100:.0f}%")
    m2.metric("Số từ phân tích", f"{report_word_count(report):,}")
    m3.metric("Lỗi chất lượng", qs["errors"])
    m4.metric("Cảnh báo", qs["warnings"])
    st.progress(instruction_pct)
    if qs["errors"]:
        st.error(f"Quality Gate còn {qs['errors']} lỗi. Báo cáo chỉ nên dùng làm bản nháp cho đến khi xử lý xong.")
    elif qs["warnings"]:
        st.warning(f"Không còn lỗi cứng, nhưng còn {qs['warnings']} cảnh báo cần xem xét trước khi nộp.")
    else:
        st.success("Quality Gate đạt.")
    with st.expander("Quality Gate · Kiểm tra trước khi xuất", expanded=True):
        st.dataframe(pd.DataFrame(quality_checks), width="stretch", hide_index=True)
        st.caption("Cảnh báo không tự động biến thành lỗi. Các tiêu chí học thuật và liên kết Case vẫn phải được sinh viên kiểm tra.")

    section_labels = [f"{i + 1}. {s['title']}" for i, s in enumerate(REPORT_SECTIONS)]
    selected = st.selectbox("Chọn phần đang viết", section_labels, key="report_section_selector")
    section = REPORT_SECTIONS[section_labels.index(selected)]
    sid = section["id"]
    left, right = st.columns([1.7, 1], gap="large")
    with left:
        st.markdown(f"### {section['title']}")
        target_words = section.get("target_words")
        size_note = f" {target_words}." if target_words else ""
        st.caption(f"Quy mô theo Instruction: {section['target_pages']}.{size_note}")
        with st.expander("Câu hỏi hướng dẫn", expanded=True):
            for i, question in enumerate(section["questions"], 1):
                st.markdown(f"**{i}.** {question}")
        text_key = f"report_text_{sid}"
        if text_key not in st.session_state:
            st.session_state[text_key] = report.get(sid, "")
        b1, b2 = st.columns(2)
        if b1.button("Gợi ý từ dữ liệu", key=f"suggest_{sid}"):
            st.session_state[text_key] = suggested_text(sid, profile, financials, case01, case02, case03)
            st.rerun()
        if b2.button("Xóa phần này", key=f"clear_{sid}"):
            st.session_state[text_key] = ""
            st.rerun()
        report[sid] = st.text_area("Phân tích và nhận xét của sinh viên", key=text_key, height=420, placeholder="Viết lập luận của bạn tại đây. App cung cấp câu hỏi và dữ liệu, không thay thế phần phân tích.")
        st.caption(f"Số từ: {word_count(report[sid]):,}")
        if st.button("Lưu phần này", type="primary", key=f"save_report_{sid}"):
            _save_report(project_id, student_id, profile, case01, case02, case03, report)
            st.success("Đã lưu phần báo cáo.")
    with right:
        with st.container(border=True):
            st.markdown("### Trợ lý viết")
            st.write("Cấu trúc đoạn khuyến nghị: nhận định → dữ liệu → giải thích → tác động → kết luận.")
            st.info("Các bảng, số liệu và sơ đồ được lấy tự động từ Case. Sinh viên chịu trách nhiệm kiểm tra lập luận và giả định.")
        with st.expander("Dữ liệu tự động từ Case", expanded=True):
            arch = case01.get("architecture", {})
            st.write(f"Blockchain: {arch.get('blockchain_type', '')}")
            st.write(f"Đồng thuận: {arch.get('consensus', '')}")
            st.write(f"Tổng nhu cầu vốn: {financials.get('V', 0):,.2f} tỷ đồng")
            st.write(f"Khoản vay: {financials.get('LoanAmount', 0):,.2f} tỷ đồng")
            st.write(f"Vốn còn thiếu: {financials.get('ExternalCapital', 0):,.2f} tỷ đồng")
            if sid == "part4":
                st.write(f"DSCR: {case02.get('DSCR', financials.get('DSCR', 0)):,.2f}")
                st.write(f"LTV: {case02.get('LTV', financials.get('LTV', 0)) * 100:,.2f}%")
            if sid == "part5":
                st.write(f"Công cụ huy động: {profile.get('funding_instrument', '')}")
            for title, rows in _records_for_section(sid, case01, case02, case03):
                _show_records(title, rows)
    st.divider()
    st.markdown("### Xem trước cấu trúc báo cáo")
    st.caption("Bản xem trước dùng chính dữ liệu sẽ đi vào Word; không còn bước chuyển Markdown sang Word.")
    for i, s in enumerate(REPORT_SECTIONS, 1):
        with st.expander(f"{i}. {s['title']}", expanded=False):
            text = report.get(s["id"], "")
            if text: st.write(text)
            else: st.warning("Chưa có phần phân tích.")
            for title, rows in _records_for_section(s["id"], case01, case02, case03): _show_records(title, rows)
    _show_diagram_preview(case01, case02, case03)
    _save_report(project_id, student_id, profile, case01, case02, case03, report)
    st.divider()
    st.markdown("### Tạo báo cáo Word")
    st.write("Bộ xuất mới dùng bảng Word thật, không thụt đầu dòng trong ô, tự chuyển bảng nhiều cột sang trang ngang, và dùng chính các sơ đồ đã xem trước ở trên.")
    if qs["errors"] == 0:
        docx_bytes = build_docx(profile, financials, case01, case02, case03, report, consistency, quality_checks)
        st.download_button("Tạo và tải báo cáo Word", data=docx_bytes, file_name=f"Bao_cao_Blockchain_{''.join(ch for ch in student_id if ch.isdigit())}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", width="stretch", type="primary")
    else:
        st.warning("Chưa bật nút báo cáo sẵn sàng nộp vì Quality Gate còn lỗi. Bạn vẫn có thể tạo bản nháp để kiểm tra bố cục.")
        draft_bytes = build_docx(profile, financials, case01, case02, case03, report, consistency, quality_checks)
        st.download_button("Tạo và tải bản nháp Word", data=draft_bytes, file_name=f"Bao_cao_Blockchain_{''.join(ch for ch in student_id if ch.isdigit())}_DRAFT.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", width="stretch")
    project_json = {"student_id": student_id, "profile": profile, "financials": financials, "case01": case01, "case02": case02, "case03": case03, "report": report, "consistency": consistency, "quality": quality_checks}
    st.download_button("Sao lưu toàn bộ dự án", data=json.dumps(project_json, ensure_ascii=False, indent=2, default=str), file_name=f"Blockchain_Project_{''.join(ch for ch in student_id if ch.isdigit())}.json", mime="application/json", width="stretch")
