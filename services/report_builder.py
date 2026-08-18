"""Report Builder aligned with the required final-report structure.

The builder does not invent conclusions. It places case data and calculations into
fixed report chapters and gives the student guided questions and writing space.
"""

REPORT_SECTIONS = [
    {
        "id": "executive",
        "title": "Tóm tắt điều hành",
        "target_pages": "1–2",
        "target_words": "500–700 từ",
        "questions": [
            "Doanh nghiệp đang gặp vấn đề gì?",
            "Dự án cần tổng số vốn bao nhiêu?",
            "Blockchain được sử dụng để giải quyết vấn đề nào?",
            "Sản phẩm tín dụng và công cụ token hóa được đề xuất là gì?",
            "Rủi ro lớn nhất là gì?",
            "Khuyến nghị cuối cùng là triển khai, thí điểm hay không triển khai?",
        ],
    },
    {
        "id": "part1",
        "title": "Phần 1. Hồ sơ case cá nhân",
        "target_pages": "2–3",
        "questions": [
            "Cách xác định các biến từ mã số sinh viên là gì?",
            "Hồ sơ doanh nghiệp và dự án là gì?",
            "Tổng nhu cầu vốn, ngành hoạt động và vấn đề ngân hàng là gì?",
            "Công cụ huy động vốn được phân bổ là gì?",
            "Doanh nghiệp, dự án, ngân hàng và token đã được đặt tên chưa?",
        ],
    },
    {
        "id": "part2",
        "title": "Phần 2. Phân tích vấn đề và quy trình hiện tại",
        "target_pages": "3–4",
        "questions": [
            "Các bên liên quan là ai?",
            "As-is Process hiện tại diễn ra như thế nào?",
            "Điểm nghẽn và nguyên nhân gốc rễ là gì?",
            "Rủi ro hiện tại nằm ở đâu?",
            "Chi phí và thời gian xử lý hiện tại là bao nhiêu?",
        ],
    },
    {
        "id": "part3",
        "title": "Phần 3. Thiết kế kiến trúc blockchain",
        "target_pages": "4–5",
        "questions": [
            "Vì sao chọn blockchain, cơ sở dữ liệu truyền thống hoặc Hybrid?",
            "Loại blockchain nào phù hợp?",
            "Thành viên mạng và vai trò của từng thành viên là gì?",
            "Cơ chế đồng thuận nào được lựa chọn và vì sao?",
            "Ma trận quyền, dữ liệu On-chain và Off-chain được thiết kế thế nào?",
            "Quản trị, bảo mật và quyền riêng tư được xử lý ra sao?",
        ],
    },
    {
        "id": "part4",
        "title": "Phần 4. Thiết kế sản phẩm tín dụng",
        "target_pages": "4–5",
        "questions": [
            "Điều khoản khoản vay là gì?",
            "To-be Process hoạt động như thế nào?",
            "Hợp đồng thông minh tín dụng thực hiện những điều kiện nào?",
            "Oracle nào được sử dụng và cách xử lý sai lệch ra sao?",
            "DSCR và LTV cho thấy điều gì?",
            "Ba kịch bản và xử lý sự cố được thiết kế thế nào?",
        ],
    },
    {
        "id": "part5",
        "title": "Phần 5. Thiết kế phương án huy động vốn",
        "target_pages": "4–5",
        "questions": [
            "Nhu cầu vốn còn lại sau khoản vay là bao nhiêu?",
            "Các phương án huy động vốn được so sánh như thế nào?",
            "Cấu trúc token là gì?",
            "Term Sheet quy định những gì?",
            "Nhà đầu tư có quyền gì?",
            "Vòng đời token và cơ chế thanh toán, phân phối dòng tiền hoạt động thế nào?",
        ],
    },
    {
        "id": "part6",
        "title": "Phần 6. Quản trị rủi ro tích hợp",
        "target_pages": "3–4",
        "questions": [
            "Rủi ro doanh nghiệp là gì?",
            "Rủi ro tín dụng và rủi ro của FutureBank là gì?",
            "Rủi ro công nghệ và nhà đầu tư là gì?",
            "Rủi ro pháp lý và hệ thống là gì?",
            "Integrated Risk Heat Map tối thiểu 15 rủi ro được xây dựng thế nào?",
        ],
    },
    {
        "id": "part7",
        "title": "Phần 7. Đánh giá hiệu quả",
        "target_pages": "2–3",
        "questions": [
            "Ít nhất 10 KPI được lựa chọn là gì?",
            "Công thức hoặc cách đo lường từng KPI là gì?",
            "Nguồn dữ liệu và tần suất báo cáo là gì?",
            "KPI nào đo hiệu quả quy trình, rủi ro, huy động vốn, vận hành, thị trường và khách hàng?",
        ],
    },
    {
        "id": "part8",
        "title": "Phần 8. Lộ trình triển khai",
        "target_pages": "2–3",
        "questions": [
            "Proof of Concept gồm hoạt động, dữ liệu và thành viên nào?",
            "Điều kiện chuyển từ PoC sang Pilot là gì?",
            "Pilot có bao nhiêu khách hàng và giới hạn giá trị giao dịch thế nào?",
            "Ai kiểm toán hệ thống trước vận hành chính thức?",
            "Điều kiện triển khai chính thức, đào tạo, dự phòng và phục hồi là gì?",
        ],
    },
    {
        "id": "part9",
        "title": "Phần 9. Kết luận và khuyến nghị",
        "target_pages": "2–3",
        "questions": [
            "Blockchain có thực sự cần thiết không?",
            "Giá trị lớn nhất và hạn chế lớn nhất là gì?",
            "Rủi ro lớn nhất là gì?",
            "FutureBank nên triển khai toàn bộ hay từng phần?",
            "Doanh nghiệp và nhà đầu tư có nên tham gia không?",
            "Những điều kiện nào phải được đáp ứng trước khi triển khai?",
        ],
    },
]


def default_report():
    return {s["id"]: "" for s in REPORT_SECTIONS}


def word_count(text):
    return len((text or "").split())


def report_completion(report):
    result = {}
    for section in REPORT_SECTIONS:
        text = report.get(section["id"], "")
        result[section["id"]] = word_count(text) > 30
    return result


def suggested_text(section_id, profile, financials, case01, case02, case03):
    arch = case01.get("architecture", {}) if isinstance(case01, dict) else {}
    if section_id == "executive":
        return (
            f"Doanh nghiệp thuộc ngành {profile.get('industry', '')}. "
            f"Vấn đề ngân hàng trọng tâm là {profile.get('banking_problem', '')}. "
            f"Tổng nhu cầu vốn là {financials.get('V', 0):,.2f} tỷ đồng, khoản vay là "
            f"{financials.get('LoanAmount', 0):,.2f} tỷ đồng và vốn còn thiếu là "
            f"{financials.get('ExternalCapital', 0):,.2f} tỷ đồng. "
            f"Case 01 lựa chọn {arch.get('blockchain_type', '')}. "
            "Sinh viên cần bổ sung phân tích về giá trị kinh tế, rủi ro và khuyến nghị cuối cùng."
        )
    if section_id == "part1":
        return (
            f"Hồ sơ cá nhân hóa xác định doanh nghiệp thuộc ngành {profile.get('industry', '')}, "
            f"loại hình {profile.get('business_type', '')}. Vấn đề ngân hàng trọng tâm là "
            f"{profile.get('banking_problem', '')}. Công cụ huy động vốn Case 03 là "
            f"{profile.get('funding_instrument', '')}. "
            "Sinh viên cần giải thích cách xác định các biến từ mã số sinh viên và các giả định bổ sung."
        )
    if section_id == "part2":
        return "Case 01 đã xây dựng As-is Process. Hãy phân tích các điểm nghẽn, nguyên nhân gốc rễ, rủi ro, chi phí và thời gian xử lý; không chỉ mô tả lại bảng quy trình."
    if section_id == "part3":
        return f"Kiến trúc được lựa chọn là {arch.get('blockchain_type', '')} với cơ chế đồng thuận {arch.get('consensus', '')}. Hãy giải thích vì sao lựa chọn này phù hợp với nhu cầu chia sẻ và xác minh dữ liệu, quyền truy cập, dữ liệu On-chain và Off-chain, quản trị, bảo mật và quyền riêng tư."
    if section_id == "part4":
        return f"Khoản vay theo hồ sơ tài chính là {financials.get('LoanAmount', 0):,.2f} tỷ đồng trên tổng nhu cầu vốn {financials.get('V', 0):,.2f} tỷ đồng. Hãy phân tích điều khoản, To-be Process, Oracle, hợp đồng thông minh, DSCR, LTV, ba kịch bản và xử lý sự cố."
    if section_id == "part5":
        return f"Vốn còn thiếu sau khoản vay là {financials.get('ExternalCapital', 0):,.2f} tỷ đồng. Hãy giải thích phương án huy động, so sánh phương án, cấu trúc token, Term Sheet, quyền nhà đầu tư, vòng đời token và phân phối dòng tiền."
    if section_id == "part6":
        return "Hãy tổng hợp rủi ro từ Case 01, Case 02 và Case 03 thành một hệ thống rủi ro tích hợp, thay vì sao chép ba Risk Register riêng biệt."
    if section_id == "part7":
        return "Hãy đề xuất ít nhất 10 KPI, nêu công thức hoặc cách đo lường, nguồn dữ liệu và tần suất báo cáo."
    if section_id == "part8":
        return "Hãy xây dựng lộ trình theo ba giai đoạn Proof of Concept, Pilot và Triển khai chính thức; nêu điều kiện chuyển giai đoạn, kiểm toán, đào tạo, dự phòng và phục hồi."
    if section_id == "part9":
        return "Kết luận phải phản ánh cả ba Case. Hãy trả lời trực tiếp mức độ cần thiết của Blockchain, giá trị, hạn chế, rủi ro lớn nhất, phạm vi triển khai, điều kiện tiên quyết, khả năng token hóa và vai trò của FutureBank."
    return ""


def report_word_count(report):
    return sum(word_count(report.get(s["id"], "")) for s in REPORT_SECTIONS)
