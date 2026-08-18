from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.shared import Pt

from services.report_builder import REPORT_SECTIONS


def _add_table(document, records, title=None, max_rows=80):
    if not records:
        return
    if title:
        document.add_heading(title, level=3)
    keys = []
    for row in records:
        for key in row.keys():
            if key not in keys:
                keys.append(key)
    keys = keys[:8]
    table = document.add_table(rows=1, cols=len(keys))
    table.style = "Table Grid"
    for i, key in enumerate(keys):
        table.rows[0].cells[i].text = str(key)
    for row in records[:max_rows]:
        cells = table.add_row().cells
        for i, key in enumerate(keys):
            cells[i].text = str(row.get(key, ""))


def build_docx(profile, financials, case01, case02, case03, report, consistency_results):
    document = Document()
    styles = document.styles
    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = Pt(11)

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("ĐỀ ÁN XÂY DỰNG HỆ SINH THÁI BLOCKCHAIN TÍCH HỢP TÍN DỤNG, HUY ĐỘNG VỐN VÀ ĐẦU TƯ")
    run.bold = True
    run.font.size = Pt(18)
    document.add_paragraph("")
    p = document.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(f"Sinh viên: {profile.get('student_id', '')}\n").bold = True
    p.add_run(f"Doanh nghiệp: {profile.get('business_name', profile.get('business_type', ''))}\n")
    p.add_run(f"Ngành: {profile.get('industry', '')}")
    document.add_page_break()

    document.add_heading("Tóm tắt điều hành", level=1)
    document.add_paragraph(report.get("executive", "Chưa hoàn thiện."))

    for section in REPORT_SECTIONS[1:]:
        document.add_heading(section["title"], level=1)
        text = report.get(section["id"], "")
        if text:
            document.add_paragraph(text)
        else:
            document.add_paragraph("[Sinh viên bổ sung phần phân tích và nhận xét.]", style="Intense Quote")

        if section["id"] == "part1":
            rows = [["Thông số", "Giá trị"], ["MSSV", profile.get("student_id", "")], ["D1", profile.get("D1", "")], ["D2", profile.get("D2", "")], ["D3", profile.get("D3", "")], ["D4", profile.get("D4", "")], ["Ngành", profile.get("industry", "")], ["Loại hình", profile.get("business_type", "")], ["Vấn đề ngân hàng", profile.get("banking_problem", "")], ["Công cụ huy động", profile.get("funding_instrument", "")]]
            _add_table(document, [dict([r]) for r in rows[1:]], "Bảng thông tin cá nhân hóa")
        elif section["id"] == "part2":
            _add_table(document, case01.get("as_is", []), "As-is Process")
        elif section["id"] == "part3":
            _add_table(document, case01.get("assessment", []), "Đánh giá CSDL và Blockchain/DLT")
            _add_table(document, case01.get("permissions", []), "Ma trận quyền")
            _add_table(document, case01.get("data", []), "On-chain và Off-chain")
        elif section["id"] == "part4":
            _add_table(document, case02.get("to_be", []), "To-be Process")
            _add_table(document, case02.get("scenarios", []), "Ba kịch bản")
        elif section["id"] == "part5":
            _add_table(document, case03.get("term_sheet", []), "Term Sheet")
            _add_table(document, case03.get("token_lifecycle", []), "Vòng đời token")
        elif section["id"] == "part6":
            _add_table(document, case01.get("risks", []), "Risk Register Case 01")
            _add_table(document, case02.get("risks", []), "Risk Register Case 02")
            _add_table(document, case03.get("risks", []), "Risk Register Case 03")
        elif section["id"] == "part7":
            document.add_paragraph("[Bảng KPI sẽ được bổ sung tại đây khi sinh viên nhập dữ liệu KPI.]", style="Intense Quote")

    document.add_heading("Phụ lục", level=1)
    document.add_heading("Phụ lục 1. Bảng tính và dữ liệu tài chính", level=2)
    for key, value in financials.items():
        document.add_paragraph(f"{key}: {value}")
    document.add_heading("Phụ lục 2. Change Log", level=2)
    document.add_paragraph("[Nhật ký điều chỉnh thiết kế được sinh viên hoàn thiện trong ứng dụng.]", style="Intense Quote")
    document.add_heading("Phụ lục 3. Consistency Checker", level=2)
    _add_table(document, consistency_results or [], "Kết quả kiểm tra 22 câu")

    output = BytesIO()
    document.save(output)
    return output.getvalue()
