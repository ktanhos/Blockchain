import pandas as pd

AS_IS_DEFAULT = [
    {"Bước": 1, "Chủ thể": "Doanh nghiệp", "Hành động": "Khởi tạo hồ sơ/giao dịch", "Dữ liệu": "Hồ sơ doanh nghiệp", "Hệ thống": "Hệ thống doanh nghiệp", "Thời gian": "", "Nhập lại": "Có", "Đối chiếu": "Không", "Rủi ro": "Dữ liệu không đồng nhất", "Trách nhiệm": "Doanh nghiệp"},
    {"Bước": 2, "Chủ thể": "Ngân hàng", "Hành động": "Tiếp nhận và kiểm tra KYC", "Dữ liệu": "KYC", "Hệ thống": "Core/KYC", "Thời gian": "", "Nhập lại": "Có", "Đối chiếu": "Có", "Rủi ro": "KYC lặp lại", "Trách nhiệm": "Ngân hàng"},
    {"Bước": 3, "Chủ thể": "Nhà cung cấp", "Hành động": "Phát hành hóa đơn/chứng từ", "Dữ liệu": "Hóa đơn", "Hệ thống": "Hệ thống nhà cung cấp", "Thời gian": "", "Nhập lại": "Có", "Đối chiếu": "Có", "Rủi ro": "Hóa đơn giả hoặc trùng", "Trách nhiệm": "Nhà cung cấp"},
    {"Bước": 4, "Chủ thể": "Logistics", "Hành động": "Xác nhận giao hàng", "Dữ liệu": "Trạng thái giao hàng", "Hệ thống": "Hệ thống logistics", "Thời gian": "", "Nhập lại": "Có", "Đối chiếu": "Có", "Rủi ro": "Sai trạng thái", "Trách nhiệm": "Logistics"},
    {"Bước": 5, "Chủ thể": "Ngân hàng", "Hành động": "Đối chiếu hồ sơ và phê duyệt", "Dữ liệu": "Hồ sơ tín dụng", "Hệ thống": "Core tín dụng", "Thời gian": "", "Nhập lại": "Có", "Đối chiếu": "Có", "Rủi ro": "Đối chiếu thủ công", "Trách nhiệm": "Ngân hàng"},
    {"Bước": 6, "Chủ thể": "Đơn vị bảo hiểm/thẩm định", "Hành động": "Xác nhận tài sản hoặc bảo hiểm", "Dữ liệu": "Tài sản bảo đảm", "Hệ thống": "Hệ thống đối tác", "Thời gian": "", "Nhập lại": "Có", "Đối chiếu": "Có", "Rủi ro": "Trạng thái tài sản chậm cập nhật", "Trách nhiệm": "Đơn vị cung cấp dữ liệu"},
    {"Bước": 7, "Chủ thể": "Ngân hàng", "Hành động": "Giải ngân", "Dữ liệu": "Lệnh giải ngân", "Hệ thống": "Core banking", "Thời gian": "", "Nhập lại": "Có", "Đối chiếu": "Có", "Rủi ro": "Giải ngân sai điều kiện", "Trách nhiệm": "Ngân hàng"},
    {"Bước": 8, "Chủ thể": "Ngân hàng/Doanh nghiệp", "Hành động": "Theo dõi dòng tiền và tất toán", "Dữ liệu": "Thanh toán, dư nợ", "Hệ thống": "Core banking", "Thời gian": "", "Nhập lại": "Có", "Đối chiếu": "Có", "Rủi ro": "Sai lệch thu nợ/phân bổ", "Trách nhiệm": "Ngân hàng"},
]

BLOCKCHAIN_CRITERIA = [
    "Số lượng tổ chức tham gia", "Mức độ tin cậy giữa các bên", "Nhu cầu chia sẻ dữ liệu", "Nhu cầu truy xuất lịch sử",
    "Khả năng sửa hoặc xóa dữ liệu", "Tốc độ xử lý", "Quyền riêng tư", "Chi phí triển khai",
    "Khả năng tích hợp hệ thống hiện hữu", "Yêu cầu pháp lý", "Giá trị kinh tế tạo ra", "Khả năng phục hồi hệ thống",
]
MEMBERS = ["FutureBank", "Ngân hàng đối tác", "Doanh nghiệp", "Nhà cung cấp", "Khách hàng/người mua", "Logistics", "Kiểm toán viên", "Cơ quan quản lý"]
DATA_TYPES = ["Thông tin định danh", "Hồ sơ KYC", "Hóa đơn", "Hợp đồng mua bán", "Trạng thái tài sản bảo đảm", "Chứng từ giao hàng", "Báo cáo tài chính", "Kết quả chấm điểm tín dụng", "Cảnh báo AML", "Lịch sử thay đổi trạng thái"]
RISK_DEFAULT = [
    ("Dữ liệu đầu vào sai", "Nguồn dữ liệu sai hoặc không đầy đủ", 3, 5, "Xác minh nhiều nguồn; kiểm tra chéo", "Đơn vị cung cấp dữ liệu"),
    ("Quyền riêng tư", "Dữ liệu nhạy cảm bị truy cập sai quyền", 3, 5, "Phân quyền; mã hóa; tối thiểu hóa dữ liệu", "FutureBank"),
    ("Khóa riêng", "Mất hoặc lộ khóa", 2, 5, "Quản lý khóa; đa chữ ký; khôi phục", "FutureBank"),
    ("Thành viên cung cấp dữ liệu sai", "Động cơ gian lận hoặc lỗi nghiệp vụ", 3, 5, "Xác thực nguồn; cơ chế trách nhiệm", "Thành viên cung cấp dữ liệu"),
    ("Hợp đồng thông minh", "Lỗi logic hoặc triển khai", 3, 5, "Kiểm thử; kiểm toán; tạm dừng khẩn cấp", "Đơn vị phát triển"),
    ("Oracle", "Dữ liệu bên ngoài sai hoặc ngừng hoạt động", 3, 5, "Nhiều nguồn; nguồn dự phòng; kiểm tra sai lệch", "Nhà cung cấp Oracle"),
    ("Tích hợp core banking", "API hoặc dữ liệu không tương thích", 3, 4, "Kiểm thử tích hợp; đối soát", "FutureBank"),
    ("Pháp lý", "Mô hình kỹ thuật chưa được pháp luật công nhận", 2, 5, "Rà soát pháp lý trước Pilot", "FutureBank/Pháp chế"),
    ("Quản trị", "Một thành viên tập trung quá nhiều quyền", 3, 4, "Phân quyền; biểu quyết nhiều bên", "Hội đồng quản trị mạng"),
    ("Hệ thống ngừng hoạt động", "Lỗi nút hoặc hạ tầng", 2, 5, "Dự phòng nút; sao lưu; kế hoạch phục hồi", "Nhà vận hành mạng"),
]


def default_case01():
    return {
        "as_is": AS_IS_DEFAULT,
        "assessment": [{"Tiêu chí": c, "CSDL tập trung": 3, "Blockchain/DLT": 3, "Giải thích": ""} for c in BLOCKCHAIN_CRITERIA],
        "architecture": {"decision": "Hybrid", "blockchain_type": "Blockchain liên minh", "nodes": MEMBERS[:], "consensus": "PBFT hoặc biến thể", "validator_count": 4, "completion": "Khi đạt ngưỡng xác nhận của các nút hợp lệ"},
        "permissions": [{"Chủ thể": m, "Đọc": True, "Ghi": False, "Xác thực": False, "Quản trị": False, "Tạm dừng": False} for m in MEMBERS],
        "data": [{"Loại dữ liệu": d, "On-chain": False, "Off-chain": True, "Chủ thể được truy cập": "", "Lý do": ""} for d in DATA_TYPES],
        "governance": {"Chủ sở hữu nền tảng": "FutureBank và liên minh thành viên", "Tiếp nhận thành viên": "Hội đồng quản trị mạng", "Thay đổi quy tắc": "Biểu quyết theo quy chế liên minh", "Nâng cấp hợp đồng": "Quy trình phê duyệt nhiều bên", "Tạm dừng hệ thống": "Quyền hạn chế theo quy chế khẩn cấp", "Trách nhiệm giao dịch sai": "Theo nguồn dữ liệu và quy trình phê duyệt", "Bồi thường": "Theo thỏa thuận thành viên", "Tranh chấp": "Theo thỏa thuận và pháp luật áp dụng", "Lưu trữ dữ liệu": "Theo yêu cầu pháp lý và chính sách dữ liệu", "Thành viên rời mạng": "Thu hồi quyền và xử lý dữ liệu/quyền truy cập"},
        "risks": [{"Rủi ro": r, "Nguyên nhân": cause, "P": p, "I": i, "Điểm": p*i, "Biện pháp kiểm soát": control, "Chủ sở hữu": owner} for r, cause, p, i, control, owner in RISK_DEFAULT],
        "conclusion": "Chưa kết luận. Hoàn thành đánh giá và giải thích trước khi quyết định Go, No-Go hoặc Hybrid.",
    }


def risk_dataframe(data):
    df = pd.DataFrame(data)
    if not df.empty and "P" in df.columns and "I" in df.columns:
        df["Điểm"] = pd.to_numeric(df["P"], errors="coerce").fillna(0) * pd.to_numeric(df["I"], errors="coerce").fillna(0)
    return df
