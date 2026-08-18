from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _register_font():
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"),
    ]
    for path in candidates:
        if path.exists():
            pdfmetrics.registerFont(TTFont("AppUnicode", str(path)))
            return "AppUnicode"
    return "Helvetica"


def _text(value):
    if value is None:
        return ""
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _paragraph(value, style):
    return Paragraph(_text(value).replace("\n", "<br/>"), style)


def _table(rows, font, widths=None, small=False):
    if not rows:
        return Spacer(1, 1)
    styles = getSampleStyleSheet()
    fs = 7 if small else 8
    cell = ParagraphStyle("cell", fontName=font, fontSize=fs, leading=fs + 2)
    header = ParagraphStyle("header", fontName=font, fontSize=fs, leading=fs + 2, textColor=colors.white)
    converted = []
    for r_i, row in enumerate(rows):
        converted.append([Paragraph(_text(x), header if r_i == 0 else cell) for x in row])
    t = Table(converted, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def _records_table(records, font, max_rows=100):
    if not records:
        return None
    keys = []
    for row in records:
        for k in row.keys():
            if k not in keys:
                keys.append(k)
    keys = keys[:8]
    rows = [keys]
    for row in records[:max_rows]:
        rows.append([row.get(k, "") for k in keys])
    return _table(rows, font, small=True)


def build_integrated_report(profile, financials, case01, case02, case03, consistency_results):
    font = _register_font()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="Báo cáo tích hợp Blockchain trong Tài chính và Ngân hàng",
        author="FutureBank Case Study",
    )
    base = getSampleStyleSheet()
    title = ParagraphStyle("title_vn", parent=base["Title"], fontName=font, alignment=TA_CENTER, fontSize=18, leading=23)
    h1 = ParagraphStyle("h1_vn", parent=base["Heading1"], fontName=font, fontSize=14, leading=18, spaceBefore=10, spaceAfter=6)
    h2 = ParagraphStyle("h2_vn", parent=base["Heading2"], fontName=font, fontSize=11, leading=14, spaceBefore=7, spaceAfter=4)
    body = ParagraphStyle("body_vn", parent=base["BodyText"], fontName=font, fontSize=9.2, leading=13, spaceAfter=5)
    note = ParagraphStyle("note_vn", parent=body, fontSize=8, leading=11, textColor=colors.HexColor("#475569"))

    story = []
    story += [Spacer(1, 25 * mm), _paragraph("ĐỀ ÁN XÂY DỰNG HỆ SINH THÁI BLOCKCHAIN TÍCH HỢP TÍN DỤNG, HUY ĐỘNG VỐN VÀ ĐẦU TƯ", title), Spacer(1, 8 * mm)]
    story += [_paragraph("Vai trò của FutureBank", title), Spacer(1, 12 * mm)]
    story += [_paragraph(f"Sinh viên: {profile.get('student_id', '')}", body), _paragraph(f"Doanh nghiệp: {profile.get('business_type', '')} · Ngành: {profile.get('industry', '')}", body), _paragraph("Báo cáo được tạo từ dữ liệu Case 01, Case 02, Case 03 và Consistency Checker trong ứng dụng.", note), PageBreak()]

    story += [_paragraph("Tóm tắt điều hành", h1)]
    executive = [
        f"Doanh nghiệp thuộc ngành {profile.get('industry', '')} và có vấn đề ngân hàng trọng tâm là {profile.get('banking_problem', '')}.",
        f"Tổng nhu cầu vốn V là {financials.get('V', 0):,.2f} tỷ đồng; khoản vay là {financials.get('LoanAmount', 0):,.2f} tỷ đồng; phần vốn còn thiếu là {financials.get('ExternalCapital', 0):,.2f} tỷ đồng.",
        f"Mô hình blockchain được lựa chọn trong Case 01 là {case01.get('architecture', {}).get('blockchain_type', '')}.",
        f"Công cụ huy động vốn Case 03 theo hồ sơ cá nhân hóa là {profile.get('funding_instrument', '')}.",
    ]
    for x in executive:
        story.append(_paragraph(x, body))

    story += [_paragraph("1. Hồ sơ case cá nhân", h1)]
    profile_rows = [["Thông số", "Giá trị"], ["MSSV", profile.get("student_id", "")], ["D1", profile.get("D1", "")], ["D2", profile.get("D2", "")], ["D3", profile.get("D3", "")], ["D4", profile.get("D4", "")], ["Ngành", profile.get("industry", "")], ["Loại hình", profile.get("business_type", "")], ["Vấn đề ngân hàng", profile.get("banking_problem", "")], ["Công cụ huy động", profile.get("funding_instrument", "")]]
    story.append(_table(profile_rows, font, widths=[55 * mm, 125 * mm]))
    story.append(Spacer(1, 5 * mm))
    financial_rows = [["Chỉ tiêu", "Giá trị"], ["V tổng nhu cầu vốn", f"{financials.get('V', 0):,.2f} tỷ"], ["Loan Amount", f"{financials.get('LoanAmount', 0):,.2f} tỷ"], ["External Capital", f"{financials.get('ExternalCapital', 0):,.2f} tỷ"], ["Thời hạn", f"{financials.get('T', 0):,.2f} năm"], ["Lãi suất", f"{financials.get('r', 0) * 100:,.2f}%"], ["Collateral Ratio", f"{financials.get('CollateralRatio', 0) * 100:,.2f}%"]]
    story.append(_table(financial_rows, font, widths=[70 * mm, 110 * mm]))

    story += [_paragraph("2. Case 01 · Phân tích và kiến trúc Blockchain", h1)]
    story += [_paragraph("As Is Process", h2)]
    story.append(_records_table(case01.get("as_is", []), font))
    story.append(Spacer(1, 4 * mm))
    story += [_paragraph("Đánh giá cơ sở dữ liệu và Blockchain/DLT", h2)]
    story.append(_records_table(case01.get("assessment", []), font))
    story += [_paragraph("Kiến trúc và quản trị", h2)]
    arch = case01.get("architecture", {})
    arch_rows = [["Thuộc tính", "Giá trị"], ["Quyết định", arch.get("decision", "")], ["Mô hình", arch.get("blockchain_type", "")], ["Thành viên/nút", ", ".join(map(str, arch.get("nodes", [])))], ["Đồng thuận", arch.get("consensus", "")], ["Số nút xác thực", arch.get("validator_count", "")], ["Hoàn tất giao dịch", arch.get("completion", "")]]
    story.append(_table(arch_rows, font, widths=[60 * mm, 120 * mm]))
    story += [_paragraph("Ma trận quyền", h2), _records_table(case01.get("permissions", []), font), _paragraph("On Chain và Off Chain", h2), _records_table(case01.get("data", []), font), _paragraph("Risk Register", h2), _records_table(case01.get("risks", []), font), _paragraph("Kết luận Case 01", h2), _paragraph(case01.get("conclusion", "Chưa nhập"), body)]

    story += [_paragraph("3. Case 02 · Sản phẩm tín dụng", h1)]
    story += [_paragraph("Các chỉ tiêu tài chính", h2)]
    case02_rows = [["Chỉ tiêu", "Giá trị"], ["DSCR", case02.get("DSCR", financials.get("DSCR", ""))], ["LTV", case02.get("LTV", financials.get("LTV", ""))], ["Mô hình blockchain", case02.get("blockchain_type", arch.get("blockchain_type", ""))], ["Oracle", case02.get("oracle", "")], ["Quyền nâng cấp", case02.get("upgrade_authority", "")]]
    story.append(_table(case02_rows, font, widths=[65 * mm, 115 * mm]))
    story += [_paragraph("To Be Process", h2), _records_table(case02.get("to_be", []), font), _paragraph("Kịch bản", h2), _records_table(case02.get("scenarios", []), font), _paragraph("Risk Register", h2), _records_table(case02.get("risks", []), font), _paragraph("Kết luận Case 02", h2), _paragraph(case02.get("conclusion", "Chưa nhập"), body)]

    story += [_paragraph("4. Case 03 · Huy động vốn và đầu tư bằng token", h1)]
    c3_rows = [["Chỉ tiêu", "Giá trị"], ["Vốn cần huy động", case03.get("external_capital", financials.get("ExternalCapital", ""))], ["Giá phát hành", case03.get("issue_price", "")], ["Số token", case03.get("token_count", "")], ["Cơ chế thanh toán", case03.get("payment_priority", "")], ["Cấu trúc pháp lý", case03.get("legal_structure", "")], ["Khoảng cách kỹ thuật pháp lý", case03.get("legal_technical_gap", "")]]
    story.append(_table(c3_rows, font, widths=[70 * mm, 110 * mm]))
    story += [_paragraph("Term Sheet", h2), _records_table(case03.get("term_sheet", []), font), _paragraph("Vòng đời token", h2), _records_table(case03.get("token_lifecycle", []), font), _paragraph("Pseudocode hợp đồng thông minh", h2), _paragraph(case03.get("smart_contract", "Chưa nhập"), body), _paragraph("Kịch bản", h2), _records_table(case03.get("scenarios", []), font), _paragraph("Risk Register", h2), _records_table(case03.get("risks", []), font), _paragraph("Khuyến nghị Case 03", h2), _paragraph(case03.get("recommendation", "Chưa nhập"), body)]

    story += [_paragraph("5. Consistency Checker", h1)]
    status_rows = [["STT", "Hạng mục", "Trạng thái", "Chi tiết"]]
    for r in consistency_results or []:
        status_rows.append([r.get("STT", ""), r.get("Hạng mục", ""), r.get("Trạng thái", ""), r.get("Chi tiết", "")])
    story.append(_table(status_rows, font, small=True))
    errors = sum(1 for r in consistency_results or [] if r.get("Trạng thái") == "Lỗi")
    story.append(Spacer(1, 4 * mm))
    story.append(_paragraph(f"Tổng kiểm tra: {len(consistency_results or [])}. Số điểm cần xử lý: {errors}.", body))

    story += [_paragraph("6. Kết luận chung", h1)]
    story.append(_paragraph("Kết luận cuối cùng cần phản ánh đồng thời kết quả của Case 01, Case 02 và Case 03, đồng thời không được bỏ qua các điểm chưa nhất quán được Consistency Checker phát hiện.", body))
    story.append(_paragraph("Báo cáo này là bản tổng hợp dữ liệu đã nhập trong ứng dụng. Sinh viên cần rà soát nội dung, bổ sung phân tích, trích dẫn và tài liệu tham khảo theo yêu cầu của học phần trước khi nộp.", note))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(font, 7)
        canvas.drawString(15 * mm, 8 * mm, "Blockchain trong Tài chính và Ngân hàng · FutureBank")
        canvas.drawRightString(195 * mm, 8 * mm, f"Trang {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
