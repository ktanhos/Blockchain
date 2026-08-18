from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
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
    table = document.add_table(rows=1, cols=max(1, len(keys)))
    table.style = "Table Grid"
    for i, key in enumerate(keys):
        table.rows[0].cells[i].text = str(key)
    for row in records[:max_rows]:
        cells = table.add_row().cells
        for i, key in enumerate(keys):
            cells[i].text = str(row.get(key, ""))


def _add_toc_field(document):
    p = document.add_paragraph()
    run = p.add_run()
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), 'TOC \\o "1-3" \\h \\z \\u')
    run._r.addnext(fld)


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

    document.add_heading("Mục lục", level=1)
    _add_toc_field(document)
    document.add_page_break()
    document.add_heading("Danh mục bảng", level=1)
    document.add_paragraph("Danh mục bảng được cập nhật khi mở file trong Word.")
    document.add_heading("Danh mục hình", level=1)
    document.add_paragraph("Sinh viên bổ sung các hình, sơ đồ As-is, To-be và kiến trúc theo yêu cầu của học phần.")
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
            records = [
                {"Thông số": "MSSV", "Giá trị": profile.get("student_id", "")},
                {"Thông số": "D1", "Giá trị": profile.get("D1", "")},
                {"Thông số": "D2", "Giá trị": profile.get("D2", "")},
                {"Thông số": "D3", "Giá trị": profile.get("D3", "")},
                {"Thông số": "D4", "Giá trị": profile.get("D4", "")},
                {"Thông số": "Ngành", "Giá trị": profile.get("industry", "")},
                {"Thông số": "Loại hình", "Giá trị": profile.get("business_type", "")},
                {"Thông số": "Vấn đề ngân hàng", "Giá trị": profile.get("banking_problem", "")},
                {"Thông số": "Công cụ huy động", "Giá trị": profile.get("funding_instrument", "")},
                {"Thông số": "Tổng nhu cầu vốn", "Giá trị": f"{financials.get('V', 0):,.2f} tỷ đồng"},
                {"Thông số": "Khoản vay", "Giá trị": f"{financials.get('LoanAmount', 0):,.2f} tỷ đồng"},
                {"Thông số": "Vốn còn thiếu", "Giá trị": f"{financials.get('ExternalCapital', 0):,.2f} tỷ đồng"},
            ]
            _add_table(document, records, "Bảng thông tin cá nhân hóa")
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
            _add_table(document, case03.get("scenarios", []), "Ba kịch bản")
        elif section["id"] == "part6":
            _add_table(document, case01.get("risks", []), "Risk Register Case 01")
            _add_table(document, case02.get("risks", []), "Risk Register Case 02")
            _add_table(document, case03.get("risks", []), "Risk Register Case 03")
        elif section["id"] == "part7":
            document.add_paragraph("[Bảng KPI: sinh viên nhập ít nhất 10 KPI, công thức hoặc cách đo lường, nguồn dữ liệu và tần suất báo cáo.]", style="Intense Quote")
        elif section["id"] == "part8":
            document.add_paragraph("Proof of Concept → Pilot → Triển khai chính thức", style="Intense Quote")

    document.add_heading("Phụ lục", level=1)
    document.add_heading("Phụ lục 1. Bảng tính", level=2)
    for key, value in financials.items():
        document.add_paragraph(f"{key}: {value}")
    document.add_heading("Phụ lục 2. Pseudocode và Term Sheet", level=2)
    document.add_paragraph("Các nội dung pseudocode và Term Sheet được lấy từ Case 02 và Case 03 khi sinh viên đã hoàn thiện.")
    document.add_heading("Phụ lục 3. Risk Register", level=2)
    _add_table(document, case01.get("risks", []), "Risk Register Case 01")
    _add_table(document, case02.get("risks", []), "Risk Register Case 02")
    _add_table(document, case03.get("risks", []), "Risk Register Case 03")
    document.add_heading("Phụ lục 4. Change Log", level=2)
    document.add_paragraph("Nhật ký điều chỉnh thiết kế phải ghi ngày, nội dung thay đổi, lý do và tác động tới Case sau.", style="Intense Quote")
    document.add_heading("Phụ lục 5. Consistency Checker", level=2)
    _add_table(document, consistency_results or [], "Kết quả kiểm tra 22 câu")

    output = BytesIO()
    document.save(output)
    return output.getvalue()
