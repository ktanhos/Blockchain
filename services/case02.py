import copy
import pandas as pd


def calculate_credit_metrics(financials: dict) -> dict:
    loan = float(financials["LoanAmount"])
    collateral = float(financials["CollateralValue"])
    debt_service = float(financials["DebtService1"])
    ebitda = float(financials["EBITDA1"])
    dscr = ebitda / debt_service if debt_service else 0.0
    ltv = loan / collateral if collateral else 0.0
    return {"DSCR": dscr, "LTV": ltv, "LoanAmount": loan, "CollateralValue": collateral}


def oracle_defaults():
    return [
        {"Dữ liệu Oracle": "Giá tài sản bảo đảm", "Nhà cung cấp": "Công ty thẩm định giá, Ngân hàng", "Tần suất": "Hằng ngày hoặc khi tái định giá", "Nguồn dự phòng": "Đơn vị thẩm định khác", "Xử lý sai lệch": "Thẩm định lại trước khi xử lý", "Trách nhiệm": "Ngân hàng"},
        {"Dữ liệu Oracle": "Trạng thái hóa đơn", "Nhà cung cấp": "MedLink, Hóa đơn điện tử", "Tần suất": "Theo sự kiện", "Nguồn dự phòng": "Đối soát hệ thống hóa đơn", "Xử lý sai lệch": "Khóa giải ngân và kiểm tra", "Trách nhiệm": "Ngân hàng"},
        {"Dữ liệu Oracle": "Trạng thái giao hàng", "Nhà cung cấp": "Đơn vị logistics", "Tần suất": "Theo sự kiện", "Nguồn dự phòng": "Đối tác logistics khác", "Xử lý sai lệch": "Đối chiếu chứng từ", "Trách nhiệm": "Đơn vị logistics"},
        {"Dữ liệu Oracle": "KYC", "Nhà cung cấp": "Hệ thống KYC/đơn vị xác minh", "Tần suất": "Khi phát sinh hoặc cập nhật", "Nguồn dự phòng": "Nguồn xác minh thứ hai", "Xử lý sai lệch": "Tạm dừng quy trình", "Trách nhiệm": "Ngân hàng"},
        {"Dữ liệu Oracle": "Cảnh báo AML", "Nhà cung cấp": "Hệ thống AML", "Tần suất": "Theo sự kiện", "Nguồn dự phòng": "Bộ phận tuân thủ", "Xử lý sai lệch": "Chuyển kiểm tra thủ công", "Trách nhiệm": "Ngân hàng"},
        {"Dữ liệu Oracle": "Tỷ giá", "Nhà cung cấp": "Nguồn tỷ giá được phê duyệt", "Tần suất": "Theo ngày hoặc sự kiện", "Nguồn dự phòng": "Nguồn tỷ giá thứ hai", "Xử lý sai lệch": "So sánh và xác nhận", "Trách nhiệm": "Ngân hàng"},
        {"Dữ liệu Oracle": "Lãi suất tham chiếu", "Nhà cung cấp": "Nguồn lãi suất được phê duyệt", "Tần suất": "Theo kỳ", "Nguồn dự phòng": "Nguồn chính sách nội bộ", "Xử lý sai lệch": "Xác nhận thủ công", "Trách nhiệm": "Ngân hàng"},
        {"Dữ liệu Oracle": "Doanh thu", "Nhà cung cấp": "Hệ thống kế toán/doanh nghiệp", "Tần suất": "Theo kỳ báo cáo", "Nguồn dự phòng": "Sao kê ngân hàng và chứng từ", "Xử lý sai lệch": "Đối soát", "Trách nhiệm": "Doanh nghiệp và ngân hàng"},
    ]


def scenario_defaults(financials: dict):
    base = dict(financials)
    favorable = dict(financials)
    adverse = dict(financials)
    favorable["Revenue1"] *= 1.15
    favorable["EbitdaMargin"] += 0.02
    favorable["EBITDA1"] = favorable["Revenue1"] * favorable["EbitdaMargin"]
    favorable["DSCR"] = favorable["EBITDA1"] / favorable["DebtService1"]
    adverse["Revenue1"] *= 0.80
    adverse["CollateralValue"] *= 0.75
    adverse["EBITDA1"] = adverse["Revenue1"] * adverse["EbitdaMargin"]
    adverse["DSCR"] = adverse["EBITDA1"] / adverse["DebtService1"]
    adverse["LTV"] = adverse["LoanAmount"] / adverse["CollateralValue"] if adverse["CollateralValue"] else 0
    return {"Cơ sở": base, "Thuận lợi": favorable, "Bất lợi": adverse}


def evaluate_credit(financials: dict, scenario: str = "Cơ sở") -> dict:
    data = scenario_defaults(financials)[scenario]
    dscr = data["DSCR"]
    ltv = data["LTV"]
    if dscr < 1.0 or ltv >= 0.80:
        status = "Cảnh báo cao"
    elif dscr < 1.20 or ltv >= 0.70:
        status = "Cảnh báo"
    else:
        status = "Trong ngưỡng"
    return {"DSCR": dscr, "LTV": ltv, "Trạng thái": status}


def smart_contract_events(kyc_valid=True, invoice_valid=True, delivery_confirmed=True, aml_clear=True, ltv=0.0):
    events = []
    if not kyc_valid:
        return [{"Điều kiện": "KYC không hợp lệ", "Hành động": "Từ chối xử lý và tạm dừng"}]
    if not aml_clear:
        return [{"Điều kiện": "Có cảnh báo AML", "Hành động": "Chuyển kiểm tra thủ công và tạm dừng"}]
    if not invoice_valid:
        return [{"Điều kiện": "Hóa đơn không hợp lệ hoặc đã tài trợ", "Hành động": "Chặn giải ngân"}]
    if not delivery_confirmed:
        return [{"Điều kiện": "Chưa xác nhận giao hàng", "Hành động": "Chưa giải ngân"}]
    if ltv >= 0.80:
        events.append({"Điều kiện": "LTV từ 80%", "Hành động": "Tạm dừng và yêu cầu xử lý tài sản bảo đảm"})
    elif ltv >= 0.70:
        events.append({"Điều kiện": "LTV từ 70%", "Hành động": "Margin Call và yêu cầu bổ sung tài sản/giảm dư nợ"})
    else:
        events.append({"Điều kiện": "KYC, AML, hóa đơn và giao hàng hợp lệ", "Hành động": "Đủ điều kiện giải ngân theo quy trình"})
    events.append({"Điều kiện": "Nhận tiền", "Hành động": "Phân bổ tiền lãi, tiền gốc và phần còn lại cho doanh nghiệp"})
    return events


def scenario_dataframe(financials: dict) -> pd.DataFrame:
    rows = []
    for name, data in scenario_defaults(financials).items():
        rows.append({"Kịch bản": name, "Doanh thu": data["Revenue1"], "Biên EBITDA": data["EbitdaMargin"], "EBITDA": data["EBITDA1"], "DSCR": data["DSCR"], "Giá trị tài sản bảo đảm": data["CollateralValue"], "LTV": data["LTV"]})
    return pd.DataFrame(rows)


def default_case02(financials: dict, case01: dict | None = None) -> dict:
    case01 = case01 or {}
    inherited_risks = copy.deepcopy(case01.get("risks", []))
    if not inherited_risks:
        inherited_risks = [{"Rủi ro": "KYC và dữ liệu định danh", "Nguyên nhân": "Dữ liệu giữa các hệ thống không đồng nhất", "P": 3, "I": 5, "Điểm": 15, "Biện pháp kiểm soát": "Đối chiếu KYC và nguồn xác minh", "Chủ sở hữu": "FutureBank"}]
    return {
        "blockchain_type": case01.get("architecture", {}).get("blockchain_type", "Blockchain liên minh"),
        "members": list(case01.get("architecture", {}).get("nodes", [])),
        "consensus": case01.get("architecture", {}).get("consensus", "PBFT hoặc biến thể"),
        "kyc_reuse": True,
        "kyc_reference": "Sử dụng lại hệ thống KYC và quy trình xác minh đã xác định tại Case 01.",
        "oracle": oracle_defaults(),
        "oracle_reuse": True,
        "emergency_pause": True,
        "pause_authority": "FutureBank kích hoạt tạm dừng khẩn cấp trong phạm vi được cấp phép; khôi phục theo cơ chế quản trị liên minh.",
        "upgrade_authority": "Quyền nâng cấp hợp đồng thuộc cơ chế phê duyệt nhiều bên theo quản trị liên minh.",
        "smart_contract": "KYC hợp lệ, AML không có cảnh báo, hóa đơn hợp lệ và giao hàng đã xác nhận mới đủ điều kiện giải ngân; LTV vượt ngưỡng thì kích hoạt cơ chế cảnh báo hoặc xử lý tài sản.",
        "to_be": [],
        "scenarios": ["Cơ sở", "Thuận lợi", "Bất lợi"],
        "risks": inherited_risks,
        "DSCR": float(financials.get("DSCR", 0)),
        "LTV": float(financials.get("LTV", 0)),
        "conclusion": "Case 02 cần đánh giá tín dụng trên dữ liệu được chia sẻ và xác minh từ Case 01, kết hợp Oracle và hợp đồng thông minh để kiểm soát điều kiện giải ngân.",
    }
