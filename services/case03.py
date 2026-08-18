import math
import pandas as pd

INSTRUMENT_OPTIONS = ["Trái phiếu doanh nghiệp token hóa", "Cổ phần token hóa", "Chứng chỉ quỹ token hóa", "Gọi vốn cộng đồng bằng token", "Token đại diện cho khoản phải thu", "Trái phiếu xanh token hóa"]
LIFECYCLE_STEPS = ["Xác định tài sản cơ sở", "Thẩm định tài chính và pháp lý", "Thành lập cấu trúc phát hành", "Kiểm toán hợp đồng thông minh", "KYC/AML nhà đầu tư", "Nhà đầu tư chuyển tiền", "Phát hành token theo Delivery versus Payment", "Tiền được giữ hoặc giải ngân", "Dự án báo cáo sử dụng vốn", "Phân phối lãi, cổ tức hoặc lợi nhuận", "Chuyển nhượng có kiểm soát", "Mua lại, đáo hạn hoặc tiêu hủy token"]
RISK_DEFAULT = [("Rủi ro tín dụng", "Doanh nghiệp không tạo đủ dòng tiền để thực hiện nghĩa vụ", 3, 5, "Công bố DSCR, LTV; giới hạn phát hành; giám sát dòng tiền", "FutureBank/Doanh nghiệp"), ("Rủi ro thị trường", "Giá trị tài sản hoặc token biến động", 3, 4, "Công bố biến động; giới hạn nhà đầu tư", "Doanh nghiệp"), ("Rủi ro thanh khoản", "Không có thị trường thứ cấp đủ sâu", 4, 4, "Hạn chế quảng bá thanh khoản; cơ chế mua lại rõ ràng", "Đơn vị phát hành"), ("Rủi ro định giá", "Giá phát hành không phản ánh hợp lý tài sản cơ sở", 3, 4, "Thẩm định độc lập và công bố phương pháp định giá", "Đơn vị phát hành"), ("Rủi ro thông tin", "Thông tin dự án không đầy đủ hoặc không kịp thời", 3, 5, "Công bố định kỳ; kiểm toán; nhật ký trên nền tảng", "Doanh nghiệp"), ("Rủi ro pháp lý", "Quyền pháp lý của token hoặc cấu trúc phát hành chưa rõ", 2, 5, "Rà soát pháp lý trước phát hành", "FutureBank/Pháp chế"), ("Rủi ro hợp đồng thông minh", "Lỗi logic phát hành hoặc chuyển nhượng", 3, 5, "Kiểm toán độc lập; kiểm thử; quyền tạm dừng", "Đơn vị phát triển"), ("Rủi ro Oracle", "Dữ liệu tài sản hoặc sự kiện bên ngoài sai", 3, 5, "Nguồn kép; đối chiếu; quy trình xử lý sai lệch", "Nhà cung cấp Oracle"), ("Rủi ro lưu ký", "Tài sản hoặc khóa được lưu ký không an toàn", 2, 5, "Tách biệt tài sản; kiểm soát truy cập; kiểm toán", "Đơn vị lưu ký"), ("Rủi ro mất khóa", "Nhà đầu tư mất khóa riêng", 2, 5, "Cơ chế khôi phục hoặc lưu ký bên thứ ba", "Nhà đầu tư/Đơn vị lưu ký"), ("Rủi ro quản trị", "Quyền nâng cấp hoặc tạm dừng tập trung", 3, 4, "Đa chữ ký; phê duyệt nhiều bên", "Hội đồng quản trị mạng"), ("Rủi ro xuyên biên giới", "Khác biệt quy định giữa các thị trường", 2, 4, "Giới hạn khu vực và rà soát pháp lý", "FutureBank/Pháp chế"), ("Rủi ro AML", "Nhà đầu tư hoặc dòng tiền có dấu hiệu bất thường", 2, 5, "KYC/AML trước giao dịch; giám sát bất thường", "FutureBank"), ("Xung đột lợi ích của FutureBank", "Ngân hàng vừa cung cấp dịch vụ vừa có lợi ích trong sản phẩm", 2, 5, "Công bố vai trò; tách chức năng; quản trị xung đột", "FutureBank")]


def default_case03(profile: dict, financials: dict) -> dict:
    return {
        "business_name": "Doanh nghiệp khách hàng của FutureBank", "project_name": "Dự án mở rộng hoạt động kinh doanh", "platform_name": "FutureBank Blockchain Finance Network", "token_name": "FBF Token", "token_code": "FBF", "instrument": profile["funding_instrument"],
        "asset_base": "Tài sản, dòng tiền và quyền tài chính của dự án theo công cụ được chọn", "issue_price": 1000000.0, "target_investor": "Cá nhân và tổ chức phù hợp với điều kiện pháp lý", "minimum_investment": 10000000.0, "term_years": max(1, int(financials["T"])), "annual_return_rate": max(0.06, float(financials["r"])), "voting": "Không", "transfer_restrictions": "KYC/AML; thời gian khóa; giới hạn sở hữu", "custody": "Bên lưu ký thứ ba hoặc cơ chế lưu ký được phê duyệt", "buyback": "Theo điều kiện và lịch mua lại được công bố trong Term Sheet", "lost_key": "Khôi phục qua bên lưu ký hoặc quy trình xác minh đa bên", "pause": "Đa chữ ký hoặc quyết định của cơ quan có thẩm quyền",
        "kyc_reuse": True, "kyc_reference": "Sử dụng lại hệ thống KYC đã xác định ở Case 01 và kiểm soát tại Case 02.", "oracle_reuse": True, "oracle_reference": "Sử dụng lại các Oracle đã được xác minh trong Case 02, đặc biệt trạng thái hóa đơn, AML, giao hàng và dòng tiền.", "upgrade_authority": "Quyền nâng cấp hợp đồng thuộc cơ chế phê duyệt nhiều bên của mạng liên minh.", "payment_priority": "Ưu tiên nghĩa vụ đến hạn đối với FutureBank theo hợp đồng tín dụng; sau khi đáp ứng nghĩa vụ ngân hàng và các chi phí bắt buộc, phần dòng tiền còn lại được phân phối cho nhà đầu tư theo Term Sheet.", "legal_structure": "Tổ chức phát hành, quyền tài chính của token và quyền đối với khoản phải thu phải được xác lập bằng cấu trúc pháp lý phù hợp; token không mặc nhiên tạo ra quyền sở hữu pháp lý nếu hồ sơ pháp lý không xác lập quyền đó.", "legal_technical_gap": "Blockchain có thể thực hiện phát hành, chuyển nhượng có kiểm soát, khóa giao dịch và phân phối dòng tiền theo điều kiện lập trình; tuy nhiên hiệu lực pháp lý của token, quyền đối với khoản phải thu và khả năng chuyển nhượng phải được xác nhận theo pháp luật áp dụng.",
        "collateral_shared": False, "priority_rights": "Không dùng chung tài sản bảo đảm giữa khoản vay FutureBank và token trong cấu trúc cơ sở.", "lifecycle": [{"Bước": i + 1, "Giai đoạn": step, "Chủ thể": "", "Điều kiện": "", "Kết quả": ""} for i, step in enumerate(LIFECYCLE_STEPS)],
        "risks": [{"Rủi ro": r, "Nguyên nhân": c, "P": p, "I": i, "Điểm": p * i, "Biện pháp kiểm soát": control, "Chủ sở hữu": owner} for r, c, p, i, control, owner in RISK_DEFAULT],
        "recommendation": "Chưa kết luận. Đánh giá dòng tiền, tín dụng, pháp lý, thanh khoản và quản trị trước khi phát hành.",
    }


def token_metrics(case03: dict, financials: dict) -> dict:
    target_billion = float(financials["ExternalCapital"]); target_vnd = target_billion * 1_000_000_000; price = float(case03.get("issue_price", 0)); token_count = math.ceil(target_vnd / price) if price > 0 else 0; actual_raise = token_count * price; annual_rate = float(case03.get("annual_return_rate", 0)); annual_income = target_vnd * annual_rate
    return {"ExternalCapital": target_billion, "TargetVND": target_vnd, "TokenCount": token_count, "IssuePrice": price, "ActualRaise": actual_raise, "AnnualIncome": annual_income, "AnnualReturnRate": annual_rate, "TermYears": int(case03.get("term_years", 1))}


def investor_cashflows(case03: dict, financials: dict) -> list[float]:
    m = token_metrics(case03, financials); income = m["AnnualIncome"]; term = m["TermYears"]; return [-m["TargetVND"]] + [income] * max(0, term - 1) + [income + m["TargetVND"]]


def npv(rate: float, cashflows: list[float]) -> float:
    return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cashflows))


def irr(cashflows: list[float]) -> float | None:
    low, high = -0.99, 5.0; f_low, f_high = npv(low, cashflows), npv(high, cashflows)
    if f_low * f_high > 0: return None
    for _ in range(100):
        mid = (low + high) / 2; f_mid = npv(mid, cashflows)
        if abs(f_mid) < 1e-8: return mid
        if f_low * f_mid <= 0: high, f_high = mid, f_mid
        else: low, f_low = mid, f_mid
    return (low + high) / 2


def investor_benefits(case03: dict, financials: dict, discount_rate: float = 0.10) -> dict:
    flows = investor_cashflows(case03, financials); m = token_metrics(case03, financials); total_income = m["AnnualIncome"] * m["TermYears"]; roi = total_income / m["TargetVND"] if m["TargetVND"] else 0
    return {"Coupon hoặc lợi nhuận năm": m["AnnualIncome"], "Tổng thu nhập trong kỳ": total_income, "ROI tích lũy": roi, "NPV": npv(discount_rate, flows), "IRR": irr(flows), "Thời gian hoàn vốn": m["TermYears"]}


def investment_scenarios(case03: dict, financials: dict) -> pd.DataFrame:
    m = token_metrics(case03, financials)
    df = pd.DataFrame([{ "Kịch bản": "Cơ sở", "Doanh thu thay đổi": 0.0, "Giá trị tài sản cơ sở": 0.0, "Giá token": 0.0, "Thanh khoản": "Theo kế hoạch", "Khả năng phân phối": 1.0, "Khả năng mua lại": "Theo Term Sheet"}, {"Kịch bản": "Tăng trưởng", "Doanh thu thay đổi": 0.20, "Giá trị tài sản cơ sở": 0.15, "Giá token": 0.15, "Thanh khoản": "Cải thiện", "Khả năng phân phối": 1.0, "Khả năng mua lại": "Cải thiện nếu dòng tiền cho phép"}, {"Kịch bản": "Suy giảm", "Doanh thu thay đổi": -0.25, "Giá trị tài sản cơ sở": 0.0, "Giá token": -0.30, "Thanh khoản": "Thấp", "Khả năng phân phối": 0.75, "Khả năng mua lại": "Có thể trì hoãn"}])
    df["Thu nhập năm dự kiến"] = m["AnnualIncome"] * df["Khả năng phân phối"]; df["Giá trị token giả định"] = m["IssuePrice"] * (1 + df["Giá token"]); df["Giá trị tài sản cơ sở giả định"] = m["TargetVND"] * (1 + df["Giá trị tài sản cơ sở"])
    return df


def smart_contract_pseudocode(case03: dict) -> str:
    return """IF Investor_KYC_Status != \"Valid\"\n THEN Reject_Subscription\nIF Investor_Exceeds_Ownership_Limit\n THEN Reject_Transfer\nIF Funds_Received == TRUE\n THEN Issue_Token\nIF Minimum_Funding_Target_Not_Reached\n THEN Refund_Investors\nIF Project_Milestone_Verified == TRUE\n THEN Release_Next_Tranche\nIF Payment_Date_Reached AND Issuer_Has_Sufficient_Funds\n THEN Distribute_Income\nIF Security_Incident == TRUE\n THEN Pause_Transfer"""


def risk_dataframe(data):
    df = pd.DataFrame(data)
    if not df.empty:
        df["Điểm"] = pd.to_numeric(df.get("P"), errors="coerce").fillna(0) * pd.to_numeric(df.get("I"), errors="coerce").fillna(0)
    return df
