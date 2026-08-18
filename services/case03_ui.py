import copy
import pandas as pd
from services.case03 import default_case03, token_metrics, investor_benefits, investment_scenarios, smart_contract_pseudocode, risk_dataframe, investor_cashflows, npv, irr


def render_case03(st, profile, financials, case02=None, save_callback=None):
    if "case03" not in st.session_state:
        st.session_state.case03 = default_case03(profile, financials)
    case03 = st.session_state.case03
    case02 = case02 or st.session_state.get("case02", {})

    # Tạo liên kết rủi ro thực tế từ Case 02. Không ép đạt: sinh viên vẫn có thể xóa hoặc chỉnh sửa.
    if not case03.get("risk_inheritance_initialized"):
        existing_names = {str(r.get("Rủi ro", "")).strip() for r in case03.get("risks", [])}
        for risk in case02.get("risks", [])[:3]:
            name = str(risk.get("Rủi ro", "")).strip()
            if name and name not in existing_names:
                case03["risks"].append(copy.deepcopy(risk))
                existing_names.add(name)
        case03["risk_inheritance_initialized"] = True

    st.header("Case 03 · Huy động vốn và đầu tư bằng token")
    st.caption("Case 03 sử dụng External Capital, DSCR, LTV, Oracle, KYC và Risk Register đã được liên kết từ các Case trước.")

    st.subheader("1. Dữ liệu chuyển tiếp")
    values = [("Tổng nhu cầu vốn", financials["V"], " tỷ"), ("Khoản vay", financials["LoanAmount"], " tỷ"), ("Vốn còn thiếu", financials["ExternalCapital"], " tỷ"), ("DSCR", financials["DSCR"], "x"), ("LTV", financials["LTV"] * 100, "%"), ("Công cụ", profile["funding_instrument"], "")]
    for row_start in range(0, len(values), 3):
        cols = st.columns(3)
        for col, (label, value, suffix) in zip(cols, values[row_start:row_start + 3]):
            col.metric(label, f"{value:.2f}{suffix}" if isinstance(value, (int, float)) else str(value))

    st.subheader("2. Liên kết Case 01 và Case 02")
    c1, c2 = st.columns(2)
    case03["kyc_reuse"] = c1.checkbox("Sử dụng lại KYC từ Case 01 và Case 02", value=bool(case03.get("kyc_reuse", False)), key="case03_kyc_reuse")
    case03["oracle_reuse"] = c2.checkbox("Tái sử dụng Oracle từ Case 02", value=bool(case03.get("oracle_reuse", False) and case02.get("oracle_reuse", False)), key="case03_oracle_reuse")
    case03["kyc_reference"] = st.text_area("Mô tả liên kết KYC", value=case03.get("kyc_reference", ""), key="case03_kyc_reference", height=80)
    case03["oracle_reference"] = st.text_area("Mô tả Oracle được tái sử dụng", value=case03.get("oracle_reference", ""), key="case03_oracle_reference", height=80)
    case03["upgrade_authority"] = st.text_area("Chủ thể có quyền nâng cấp hợp đồng", value=case03.get("upgrade_authority", ""), key="case03_upgrade_authority", height=80)

    st.subheader("3. Hồ sơ phát hành")
    left, right = st.columns(2)
    case03["business_name"] = left.text_input("Tên doanh nghiệp", value=case03["business_name"], key="case03_business_name")
    case03["project_name"] = right.text_input("Tên dự án", value=case03["project_name"], key="case03_project_name")
    case03["platform_name"] = left.text_input("Tên nền tảng blockchain", value=case03["platform_name"], key="case03_platform_name")
    case03["instrument"] = right.text_input("Công cụ huy động vốn được phân bổ", value=profile["funding_instrument"], disabled=True, key="case03_instrument")
    case03["token_name"] = left.text_input("Tên token", value=case03["token_name"], key="case03_token_name")
    case03["token_code"] = right.text_input("Mã token, tối đa 6 ký tự", value=case03["token_code"][:6], key="case03_token_code")
    case03["asset_base"] = st.text_area("Tài sản cơ sở", value=case03["asset_base"], key="case03_asset_base")

    st.subheader("4. Term Sheet và Token Economics")
    t1, t2, t3 = st.columns(3)
    case03["issue_price"] = t1.number_input("Giá phát hành mỗi token, đồng", min_value=1.0, value=float(case03["issue_price"]), step=100000.0, key="case03_issue_price")
    case03["minimum_investment"] = t2.number_input("Mức đầu tư tối thiểu, đồng", min_value=1.0, value=float(case03["minimum_investment"]), step=1000000.0, key="case03_minimum_investment")
    case03["term_years"] = t3.number_input("Thời hạn, năm", min_value=1, max_value=30, value=int(case03["term_years"]), step=1, key="case03_term_years")
    t4, t5 = st.columns(2)
    case03["annual_return_rate"] = t4.number_input("Coupon hoặc lợi suất phân phối giả định, %/năm", min_value=0.0, max_value=100.0, value=float(case03["annual_return_rate"] * 100), step=0.5, key="case03_annual_return") / 100
    case03["target_investor"] = t5.text_input("Nhà đầu tư mục tiêu", value=case03["target_investor"], key="case03_target_investor")
    case03["voting"] = st.selectbox("Quyền biểu quyết", ["Có", "Không"], index=0 if case03["voting"] == "Có" else 1, key="case03_voting")
    case03["transfer_restrictions"] = st.text_area("Hạn chế chuyển nhượng", value=case03["transfer_restrictions"], key="case03_transfer")
    case03["custody"] = st.text_area("Cơ chế lưu ký", value=case03["custody"], key="case03_custody")
    case03["buyback"] = st.text_area("Cơ chế mua lại", value=case03["buyback"], key="case03_buyback")
    case03["lost_key"] = st.text_area("Cơ chế xử lý mất khóa", value=case03["lost_key"], key="case03_lost_key")
    case03["pause"] = st.text_area("Cơ chế tạm dừng", value=case03["pause"], key="case03_pause")
    case03["payment_priority"] = st.text_area("Thứ tự ưu tiên thanh toán", value=case03["payment_priority"], key="case03_payment_priority")
    case03["legal_structure"] = st.text_area("Cấu trúc pháp lý và quyền pháp lý của token", value=case03["legal_structure"], key="case03_legal_structure")
    case03["legal_technical_gap"] = st.text_area("Khoảng cách giữa khả năng kỹ thuật và hiệu lực pháp lý", value=case03["legal_technical_gap"], key="case03_legal_gap")

    metrics = token_metrics(case03, financials)
    st.write("Quy mô phát hành")
    m1, m2, m3 = st.columns(3)
    m1.metric("Vốn cần huy động", f"{metrics['ExternalCapital']:.2f} tỷ")
    m2.metric("Tổng số token", f"{metrics['TokenCount']:,}")
    m3.metric("Giá phát hành", f"{metrics['IssuePrice']:,.0f} đồng")
    m4, m5 = st.columns(2)
    m4.metric("Giá trị phát hành", f"{metrics['ActualRaise'] / 1e9:.2f} tỷ")
    m5.metric("Tỷ lệ phát hành thực tế", f"{metrics['ActualRaise'] / metrics['TargetVND'] * 100:.4f}%" if metrics['TargetVND'] else "0%")

    st.subheader("5. Vòng đời token")
    lifecycle = st.data_editor(pd.DataFrame(case03["lifecycle"]), num_rows="dynamic", width="stretch", key="case03_lifecycle")
    case03["lifecycle"] = lifecycle.to_dict("records")

    st.subheader("6. Hợp đồng thông minh")
    st.code(smart_contract_pseudocode(case03), language="text")

    st.subheader("7. Lợi ích nhà đầu tư")
    discount = st.number_input("Tỷ lệ chiết khấu để tính NPV, %/năm", min_value=0.0, max_value=100.0, value=10.0, step=0.5, key="case03_discount") / 100
    benefits = investor_benefits(case03, financials, discount)
    b1, b2, b3 = st.columns(3)
    b1.metric("Thu nhập năm", f"{benefits['Coupon hoặc lợi nhuận năm'] / 1e9:.2f} tỷ")
    b2.metric("Tổng thu nhập", f"{benefits['Tổng thu nhập trong kỳ'] / 1e9:.2f} tỷ")
    b3.metric("ROI tích lũy", f"{benefits['ROI tích lũy'] * 100:.2f}%")
    b4, b5 = st.columns(2)
    b4.metric("NPV", f"{benefits['NPV'] / 1e9:.2f} tỷ")
    b5.metric("IRR", "Không xác định" if benefits["IRR"] is None else f"{benefits['IRR'] * 100:.2f}%")
    case03["investor_return"] = True

    st.subheader("8. Phân tích ba kịch bản đầu tư")
    scenario_df = investment_scenarios(case03, financials)
    st.dataframe(scenario_df, width="stretch", hide_index=True)
    scenario = st.selectbox("Kịch bản phân tích dòng tiền nhà đầu tư", ["Cơ sở", "Tăng trưởng", "Suy giảm"], key="case03_scenario")
    base_flows = investor_cashflows(case03, financials)
    scenario_row = scenario_df[scenario_df["Kịch bản"] == scenario].iloc[0]
    payout_factor = float(scenario_row["Khả năng phân phối"]); price_factor = float(scenario_row["Giá token"]); scenario_flows = list(base_flows)
    if len(scenario_flows) > 1:
        for i in range(1, len(scenario_flows)): scenario_flows[i] *= payout_factor
        scenario_flows[-1] += metrics["TargetVND"] * price_factor
    scenario_irr = irr(scenario_flows)
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("NPV kịch bản", f"{npv(discount, scenario_flows) / 1e9:.2f} tỷ")
    sc2.metric("IRR kịch bản", "Không xác định" if scenario_irr is None else f"{scenario_irr * 100:.2f}%")
    scenario_token_price_vnd = metrics["IssuePrice"] * (1 + price_factor)
    sc3.metric("Giá token giả định", f"{scenario_token_price_vnd:,.0f} đồng")

    st.subheader("9. Bảo vệ nhà đầu tư")
    protections = case03.get("protections") or [{"Biện pháp": x, "Áp dụng": True, "Thiết kế chi tiết": ""} for x in ["Xác minh tổ chức phát hành", "Thẩm định dự án", "Công bố rủi ro", "Giới hạn đầu tư", "Tách biệt tiền nhà đầu tư", "Kiểm toán hợp đồng thông minh", "Giải ngân theo tiến độ", "Cơ chế hoàn tiền", "Báo cáo sử dụng vốn", "Cơ chế xử lý khiếu nại", "Giám sát giao dịch bất thường", "Kế hoạch ứng phó sự cố"]]
    protection_edited = st.data_editor(pd.DataFrame(protections), width="stretch", key="case03_protection")
    case03["protections"] = protection_edited.to_dict("records")

    st.subheader("10. Risk Register cho token")
    risk_edited = st.data_editor(risk_dataframe(case03["risks"]), num_rows="dynamic", column_config={"P": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "I": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "Điểm": st.column_config.NumberColumn(disabled=True)}, width="stretch", hide_index=True, key="case03_risk")
    case03["risks"] = risk_edited.to_dict("records")

    st.subheader("11. Khuyến nghị và kết luận Case 03")
    case03["recommendation"] = st.text_area("Khuyến nghị của sinh viên", value=case03.get("recommendation", ""), height=160, key="case03_recommendation")
    case03["conclusion"] = st.text_area("Kết luận Case 03", value=case03.get("conclusion", case03.get("recommendation", "")), height=120, key="case03_conclusion")
    checks = {"Công cụ đúng theo mã sinh viên": case03["instrument"] == profile["funding_instrument"], "Vốn huy động khớp External Capital": abs(metrics["ActualRaise"] - metrics["TargetVND"]) <= metrics["IssuePrice"], "Mã token tối đa 6 ký tự": 1 <= len(case03["token_code"]) <= 6, "Có Term Sheet": bool(case03["token_name"].strip() and case03["token_code"].strip() and case03["asset_base"].strip()), "Đủ 12 bước vòng đời": len(case03["lifecycle"]) >= 12, "Đủ 14 nhóm rủi ro": len(case03["risks"]) >= 14, "Có khuyến nghị": bool(case03["recommendation"].strip())}
    st.dataframe(pd.DataFrame({"Hạng mục": list(checks.keys()), "Trạng thái": ["Đạt" if v else "Chưa đạt" for v in checks.values()]}), width="stretch", hide_index=True)
    st.session_state.case03 = case03
    if save_callback and st.button("Lưu Case 03", type="primary", key="save_case03"):
        save_callback(case03)
        st.success("Đã lưu Case 03.")
    return case03
