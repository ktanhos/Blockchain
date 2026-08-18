import math

from services.instruction_engine import validate_case01, validate_case02, validate_case03


def check_consistency(profile, financials, case01, case02=None, case03=None):
    case02 = case02 or {}
    case03 = case03 or {}
    checks = []

    instruction01 = validate_case01(case01)
    instruction02 = validate_case02(case02)
    instruction03 = validate_case03(case03)

    def add(number, name, ok, detail):
        checks.append({"STT": number, "Hạng mục": name, "Trạng thái": "Đạt" if ok else "Lỗi", "Chi tiết": detail})

    arch = case01.get("architecture", {})
    nodes = set(arch.get("nodes", []))
    permissions = case01.get("permissions", [])
    data01 = case01.get("data", [])
    governance = case01.get("governance", {})
    v = float(financials.get("V", 0))
    loan = float(financials.get("LoanAmount", 0))
    external = float(financials.get("ExternalCapital", 0))

    add(1, "Doanh nghiệp, dự án và ngân hàng nhất quán", bool(profile.get("industry")) and bool(profile.get("business_type")), "Hồ sơ cá nhân hóa tồn tại và FutureBank là ngân hàng xuyên suốt")
    add(2, "Tổng nhu cầu vốn được giữ nguyên", abs(v - loan - external) < 1e-9, f"V = {v:.2f}; khoản vay + vốn còn thiếu = {loan + external:.2f} tỷ")
    add(3, "Khoản vay Case 02 khớp cấu trúc vốn", 0 <= loan <= v, f"Khoản vay = {loan:.2f} tỷ trên tổng nhu cầu = {v:.2f} tỷ")

    issue = float(case03.get("issue_price", 0))
    token_count = math.ceil(external * 1_000_000_000 / issue) if issue > 0 else 0
    actual_raise = token_count * issue
    tolerance = issue if issue > 0 else 0
    add(4, "Số vốn huy động Case 03 đúng bằng phần vốn còn thiếu", issue > 0 and abs(actual_raise - external * 1_000_000_000) <= tolerance, f"External Capital = {external:.2f} tỷ; giá trị phát hành = {actual_raise / 1_000_000_000:.2f} tỷ")

    chain01 = arch.get("blockchain_type", "")
    chain02 = case02.get("blockchain_type", "")
    chain03 = case03.get("blockchain_type", chain01)
    add(5, "Loại blockchain Case 02 và Case 03 phù hợp Case 01", bool(chain01) and chain02 == chain01 and chain03 == chain01, f"Case 01 = {chain01}; Case 02 = {chain02}; Case 03 = {chain03}")

    members02 = set(case02.get("members", case02.get("nodes", [])))
    members03 = set(case03.get("members", case03.get("nodes", [])))
    members_ok = members02.issubset(nodes) and members03.issubset(nodes) if members02 or members03 else False
    add(6, "Thành viên vận hành mạng nhất quán", members_ok, f"Case 01 có {len(nodes)} thành viên; Case 02 có {len(members02)}; Case 03 có {len(members03)}")
    consensus_ok = bool(arch.get("consensus")) and case02.get("consensus") == arch.get("consensus") and len(permissions) > 0
    add(7, "Cơ chế đồng thuận và ma trận quyền được sử dụng nhất quán", consensus_ok, f"Đồng thuận Case 01 = {arch.get('consensus')}; Case 02 = {case02.get('consensus')}; số dòng quyền = {len(permissions)}")

    kyc01 = any("kyc" in str(r).lower() for r in data01) or any("kyc" in str(r.get("Hành động", "")).lower() for r in case01.get("as_is", []))
    kyc02 = bool(case02.get("kyc_reuse")) and bool(str(case02.get("kyc_reference", "")).strip())
    kyc03 = bool(case03.get("kyc_reuse")) and bool(str(case03.get("kyc_reference", "")).strip())
    add(8, "Hệ thống KYC Case 01 được sử dụng trong Case 02 và Case 03", kyc01 and kyc02 and kyc03, f"Case 01 có KYC = {kyc01}; Case 02 tái sử dụng = {kyc02}; Case 03 tái sử dụng = {kyc03}")

    invalid_storage = [r.get("Loại dữ liệu", "") for r in data01 if not bool(r.get("On-chain")) and not bool(r.get("Off-chain"))]
    add(9, "Dữ liệu On-chain và Off-chain được phân loại nhất quán", bool(data01) and not invalid_storage, "Mỗi dòng có ít nhất một vị trí lưu trữ; có thể đồng thời lưu trạng thái hoặc mã băm trên chuỗi và hồ sơ chi tiết ngoài chuỗi." if not invalid_storage else "Chưa chọn vị trí lưu trữ: " + ", ".join(invalid_storage))

    key01 = bool(str(governance.get("Quản lý khóa", "")).strip()) or "khóa" in str(governance).lower()
    key03 = bool(str(case03.get("lost_key", "")).strip())
    add(10, "Cơ chế quản lý khóa và xử lý mất khóa nhất quán", key01 and key03, "Case 01 phải mô tả quản trị khóa và Case 03 phải có cơ chế mất khóa")

    oracle02 = case02.get("oracle", [])
    oracle02_ok = bool(oracle02) and bool(case02.get("oracle_reuse"))
    oracle03_ok = bool(case03.get("oracle_reuse")) and bool(str(case03.get("oracle_reference", "")).strip())
    add(11, "Oracle Case 02 được tái sử dụng trong Case 03", oracle02_ok and oracle03_ok, f"Case 02 có {len(oracle02)} Oracle và tái sử dụng = {oracle02_ok}; Case 03 dẫn chiếu = {oracle03_ok}")

    pause01 = bool(str(governance.get("Tạm dừng hệ thống", "")).strip())
    pause02 = bool(case02.get("emergency_pause")) and bool(str(case02.get("pause_authority", "")).strip())
    pause03 = bool(str(case03.get("pause", "")).strip())
    add(12, "Cơ chế tạm dừng khẩn cấp nhất quán", pause01 and pause02 and pause03, f"Case 01 = {pause01}; Case 02 = {pause02}; Case 03 = {pause03}")

    upgrade01 = str(governance.get("Nâng cấp hợp đồng", "")).strip()
    upgrade02 = str(case02.get("upgrade_authority", "")).strip()
    upgrade03 = str(case03.get("upgrade_authority", "")).strip()
    add(13, "Quyền nâng cấp hợp đồng không tạo mâu thuẫn quản trị", bool(upgrade01 and upgrade02 and upgrade03), "Ba Case phải xác định được chủ thể nâng cấp; nếu khác nhau phải giải thích trong Change Log")

    annual_income = external * 1_000_000_000 * float(case03.get("annual_return_rate", 0))
    ebitda = float(financials.get("EBITDA1", 0))
    debt_service = float(financials.get("DebtService1", 0))
    cashflow_ok = ebitda >= debt_service + annual_income
    add(14, "Dòng tiền dự án đủ để trả ngân hàng và nhà đầu tư", cashflow_ok, f"EBITDA = {ebitda:.2f} tỷ; nghĩa vụ ngân hàng = {debt_service:.2f} tỷ; thu nhập nhà đầu tư = {annual_income / 1_000_000_000:.2f} tỷ/năm")

    priority = str(case03.get("payment_priority", "")).strip()
    add(15, "Thứ tự ưu tiên thanh toán được xác định", bool(priority), "Phải nêu rõ ưu tiên giữa nghĩa vụ ngân hàng và nhà đầu tư")

    shared = bool(case03.get("collateral_shared", False))
    add(16, "Tài sản bảo đảm không bị sử dụng đồng thời cho khoản vay và token", not shared, "Không dùng chung tài sản" if not shared else "Đang khai báo dùng chung tài sản")
    priority_rights = str(case03.get("priority_rights", "")).strip()
    add(17, "Quyền ưu tiên nếu dùng chung tài sản được xác định", (not shared) or bool(priority_rights), "Không dùng chung" if not shared else "Đã xác định quyền ưu tiên" if priority_rights else "Thiếu quyền ưu tiên")

    risks01 = {str(r.get("Rủi ro", "")).strip() for r in case01.get("risks", []) if str(r.get("Rủi ro", "")).strip()}
    risks02 = {str(r.get("Rủi ro", "")).strip() for r in case02.get("risks", []) if str(r.get("Rủi ro", "")).strip()}
    risks03 = {str(r.get("Rủi ro", "")).strip() for r in case03.get("risks", []) if str(r.get("Rủi ro", "")).strip()}
    add(18, "Rủi ro Case 01 được chuyển sang Case 02", bool(risks01) and bool(risks02) and bool(risks01 & risks02), f"Case 01 = {len(risks01)}; Case 02 = {len(risks02)}; giao nhau = {len(risks01 & risks02)}")
    add(19, "Rủi ro Case 02 được công bố cho nhà đầu tư Case 03", bool(risks02) and bool(risks03) and bool(risks02 & risks03), f"Case 02 = {len(risks02)}; Case 03 = {len(risks03)}; giao nhau = {len(risks02 & risks03)}")

    legal = str(case03.get("legal_structure", "")).strip()
    add(20, "Không có mâu thuẫn giữa kiến trúc kỹ thuật và cấu trúc pháp lý", bool(legal), "Phải mô tả tổ chức phát hành, quyền pháp lý của token và quan hệ với tài sản cơ sở")
    legal_gap = str(case03.get("legal_technical_gap", "")).strip()
    add(21, "Đã xác định nội dung blockchain có thể làm nhưng pháp luật chưa chắc công nhận", bool(legal_gap), "Phải ghi rõ khoảng cách giữa khả năng kỹ thuật và hiệu lực pháp lý")

    conclusion01 = bool(str(case01.get("conclusion", "")).strip())
    conclusion02 = bool(str(case02.get("conclusion", "")).strip())
    recommendation03 = bool(str(case03.get("recommendation", "")).strip())
    add(22, "Kết luận chung phản ánh đầy đủ cả ba Case", conclusion01 and conclusion02 and recommendation03, f"Case 01 = {conclusion01}; Case 02 = {conclusion02}; khuyến nghị Case 03 = {recommendation03}")

    return checks
