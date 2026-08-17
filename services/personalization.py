INDUSTRIES = {
    0: "Năng lượng mặt trời",
    1: "Nông nghiệp công nghệ cao",
    2: "Logistics và kho vận",
    3: "Thiết bị y tế",
    4: "Dệt may xuất khẩu",
    5: "Vật liệu xây dựng xanh",
    6: "Linh kiện xe điện",
    7: "Chế biến và xuất khẩu thủy sản",
    8: "Công nghệ tài chính",
    9: "Tái chế và kinh tế tuần hoàn",
}

BUSINESS_TYPES = {
    0: "Doanh nghiệp khởi nghiệp",
    1: "Doanh nghiệp nhỏ",
    2: "Doanh nghiệp vừa",
    3: "Doanh nghiệp gia đình",
    4: "Hợp tác xã",
    5: "Doanh nghiệp dẫn đầu chuỗi cung ứng",
    6: "Công ty dự án SPV",
    7: "Doanh nghiệp xuất khẩu",
    8: "Công ty đại chúng",
    9: "Doanh nghiệp xã hội",
}

BANKING_PROBLEMS = {
    0: "Một hóa đơn được dùng để vay tại nhiều ngân hàng",
    1: "Quy trình KYC bị lặp lại giữa nhiều tổ chức",
    2: "Thanh toán quốc tế chậm và khó theo dõi",
    3: "Tranh chấp trạng thái tài sản bảo đảm",
    4: "Đối chiếu dữ liệu trong khoản vay hợp vốn",
    5: "Gian lận chứng từ tài trợ thương mại",
    6: "Khó kiểm soát mục đích sử dụng vốn vay",
    7: "Chia sẻ thông tin AML và giao dịch đáng ngờ",
    8: "Sai lệch trong tính lãi, thu nợ và phân bổ dòng tiền",
    9: "Sai lệch danh sách nhà đầu tư và quyền sở hữu tài sản",
}

FUNDING_INSTRUMENTS = {
    0: "Trái phiếu doanh nghiệp token hóa",
    1: "Trái phiếu doanh nghiệp token hóa",
    2: "Cổ phần token hóa",
    3: "Cổ phần token hóa",
    4: "Chứng chỉ quỹ token hóa",
    5: "Chứng chỉ quỹ token hóa",
    6: "Gọi vốn cộng đồng bằng token",
    7: "Gọi vốn cộng đồng bằng token",
    8: "Token đại diện cho khoản phải thu",
    9: "Trái phiếu xanh token hóa",
}


def build_case_profile(student_id: str) -> dict:
    digits = "".join(ch for ch in str(student_id) if ch.isdigit())
    if len(digits) < 4:
        raise ValueError("Mã số sinh viên phải có ít nhất 4 chữ số.")

    d = digits[-4:]
    d1, d2, d3, d4 = map(int, d)
    n = int(digits[-3:])

    return {
        "student_id": student_id,
        "D1": d1,
        "D2": d2,
        "D3": d3,
        "D4": d4,
        "N": n,
        "industry": INDUSTRIES[d4],
        "business_type": BUSINESS_TYPES[d3],
        "banking_problem": BANKING_PROBLEMS[d2],
        "funding_instrument": FUNDING_INSTRUMENTS[d1],
    }
