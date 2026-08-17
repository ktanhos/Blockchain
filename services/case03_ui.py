import pandas as pd
from services.case03 import default_case03, token_metrics, investor_benefits, investment_scenarios, smart_contract_pseudocode, risk_dataframe


def render_case03(st, profile, financials):
    if "case03" not in st.session_state:
        st.session_state.case03 = default_case03(profile, financials)
    case03 = st.session_state.case03

    st.header("Case 03 · Huy động vốn và đầu tư bằng token")
    st.caption("Case 03 sử dụng trực tiếp External Capital, DSCR, LTV và công cụ huy động vốn đã xác định từ các case trước.")

    st.subheader("1. Dữ liệu chuyển tiếp")
    c = st.columns(6)
    values = [("Tổng nhu cầu vốn", financials["V"], " tỷ"), ("Khoản vay", financials["LoanAmount"], " tỷ"), ("Vốn còn thiếu", financials["ExternalCapital"], " tỷ"), ("DSCR", financials["DSCR"], "x"), ("LTV", financials["LTV"] * 100, "%"), ("Công cụ", profile["funding_instrument"], "")]
    for col, (label, value, suffix) in zip(c, values):
        col.metric(label, f"{value:.2f}{suffix}" if isinstance(value, (int, float)) else value)
    st.info("Theo đề, số vốn huy động Case 03 phải bằng phần vốn còn thiếu từ Case 02. Kết quả tín dụng và rủi ro của Case 02 phải được sử dụng khi đánh giá phương án token.")

    st.subheader("2. Hồ sơ phát hành")
    left, right = st.columns(2)
    case03["business_name"] = left.text_input("Tên doanh nghiệp", value=case03["business_name"])
    case03["project_name"] = right.text_input("Tên dự án", value=case03["project_name"])
    case03["platform_name"] = left.text_input("Tên nền tảng blockchain", value=case03["platform_name"])
    case03["instrument"] = right.text_input("Công cụ huy động vốn được phân bổ", value=profile["funding_instrument"], disabled=True)
    case03["token_name"] = left.text_input("Tên token", value=case03["token_name"])
    case03["token_code"] = right.text_input("Mã token, tối đa 6 ký tự", value=case03["token_code"][:6])
    case03["asset_base"] = st.text_area("Tài sản cơ sở", value=case03["asset_base"])

    st.subheader("3. Term Sheet")
    t1, t2, t3 = st.columns(3)
    case03["issue_price"] = t1.number_input("Giá phát hành mỗi token, đồng", min_value=1.0, value=float(case03["issue_price"]), step=100000.0)
    case03["minimum_investment"] = t2.number_input("Mức đầu tư tối thiểu, đồng", min_value=1.0, value=float(case03["minimum_investment"]), step=1000000.0)
    case03["term_years"] = t3.number_input("Thời hạn, năm", min_value=1, max_value=30, value=int(case03["term_years"]), step=1)
    t4, t5 = st.columns(2)
    case03["annual_return_rate"] = t4.number_input("Coupon hoặc lợi suất phân phối giả định, %/năm", min_value=0.0, max_value=100.0, value=float(case03["annual_return_rate"] * 100), step=0.5) / 100
    case03["target_investor"] = t5.text_input("Nhà đầu tư mục tiêu", value=case03["target_investor"])
    case03["voting"] = st.selectbox("Quyền biểu quyết", ["Có", "Không"], index=0 if case03["voting"] == "Có" else 1)
    case03["transfer_restrictions"] = st.text_area("Hạn chế chuyển nhượng", value=case03["transfer_restrictions"])
    case03["custody"] = st.text_area("Cơ chế lưu ký", value=case03["custody"])
    case03["buyback"] = st.text_area("Cơ chế mua lại", value=case03["buyback"])
    case03["lost_key"] = st.text_area("Cơ chế xử lý mất khóa", value=case03["lost_key"])
    case03["pause"] = st.text_area("Cơ chế tạm dừng", value=case03["pause"])

    metrics = token_metrics(case03, financials)
    st.write("**Tính toán quy mô phát hành**")
    m = st.columns(4)
    m[0].metric("Vốn cần huy động", f"{metrics['ExternalCapital']:.2f} tỷ")
    m[1].metric("Tổng số token", f"{metrics['TokenCount']:,}")
    m[2].metric("Giá phát hành", f"{metrics['IssuePrice']:,.0f} đồng")
    m[3].metric("Tổng giá trị phát hành", f"{metrics['ActualRaise'] / 1e9:.2f} tỷ")
    if abs(metrics["ActualRaise"] - metrics["ExternalCapital"]) > metrics["IssuePrice"]:
        st.warning("Giá phát hành và số token làm tổng giá trị phát hành vượt đáng kể vốn cần huy động. Hãy điều chỉnh giá token để bám sát External Capital.")

    st.subheader("4. Vòng đời token")
    lifecycle = st.data_editor(pd.DataFrame(case03["lifecycle"]), num_rows="dynamic", use_container_width=True, key="case03_lifecycle")
    case03["lifecycle"] = lifecycle.to_dict("records")

    st.subheader("5. Hợp đồng thông minh")
    st.code(smart_contract_pseudocode(case03), language="text")
    st.caption("Đây là pseudocode mô phỏng theo yêu cầu Case 03, không phải hợp đồng thông minh triển khai trên mạng thật.")

    st.subheader("6. Lợi ích nhà đầu tư")
    discount = st.number_input("Tỷ lệ chiết khấu để tính NPV, %/năm", min_value=0.0, max_value=100.0, value=10.0, step=0.5) / 100
    benefits = investor_benefits(case03, financials, discount)
    b = st.columns(5)
    b[0].metric("Thu nhập năm", f"{benefits['Coupon hoặc lợi nhuận năm'] / 1e9:.2f} tỷ")
    b[1].metric("Tổng thu nhập", f"{benefits['Tổng thu nhập trong kỳ'] / 1e9:.2f} tỷ")
    b[2].metric("ROI tích lũy", f"{benefits['ROI tích lũy'] * 100:.2f}%")
    b[3].metric("NPV", f"{benefits['NPV'] / 1e9:.2f} tỷ")
    b[4].metric("IRR", "Không xác định" if benefits["IRR"] is None else f"{benefits['IRR'] * 100:.2f}%")
    st.caption("Các chỉ tiêu lợi ích phụ thuộc giả định về giá phát hành, tỷ lệ phân phối và thời hạn do sinh viên thiết kế.")

    st.subheader("7. Ba kịch bản đầu tư")
    scenario_df = investment_scenarios(case03, financials)
    st.dataframe(scenario_df, use_container_width=True, hide_index=True)
    st.write("Tăng trưởng giả định doanh thu tăng 20%, giá trị doanh nghiệp hoặc tài sản cơ sở tăng 15% và nhu cầu mua token tăng. Suy giảm giả định doanh thu giảm 25%, doanh nghiệp chậm thanh toán, thanh khoản thứ cấp thấp và giá token giảm 30%.")

    st.subheader("8. Bảo vệ nhà đầu tư")
    protections = [
        "Xác minh tổ chức phát hành", "Thẩm định dự án", "Công bố rủi ro", "Giới hạn đầu tư", "Tách biệt tiền nhà đầu tư", "Kiểm toán hợp đồng thông minh", "Giải ngân theo tiến độ", "Cơ chế hoàn tiền", "Báo cáo sử dụng vốn", "Cơ chế xử lý khiếu nại", "Giám sát giao dịch bất thường", "Kế hoạch ứng phó sự cố",
    ]
    protection_df = pd.DataFrame({"Biện pháp": protections, "Áp dụng": [True] * len(protections), "Thiết kế chi tiết": [""] * len(protections)})
    protection_edited = st.data_editor(protection_df, use_container_width=True, key="case03_protection")
    case03["protections"] = protection_edited.to_dict("records")

    st.subheader("9. Risk Register cho token")
    risk_df = risk_dataframe(case03["risks"])
    risk_edited = st.data_editor(risk_df, num_rows="dynamic", column_config={"P": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "I": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "Điểm": st.column_config.NumberColumn(disabled=True)}, use_container_width=True, key="case03_risk")
    case03["risks"] = risk_edited.to_dict("records")
    st.write(f"Số rủi ro: {len(case03['risks'])}")

    st.subheader("10. Khuyến nghị đầu tư")
    case03["recommendation"] = st.text_area("Khuyến nghị của sinh viên", value=case03.get("recommendation", ""), height=160)
    checks = {
        "Công cụ đúng theo mã sinh viên": case03["instrument"] == profile["funding_instrument"],
        "Vốn huy động bám External Capital": abs(metrics["ActualRaise"] - metrics["ExternalCapital"]) <= metrics["IssuePrice"],
        "Mã token tối đa 6 ký tự": 1 <= len(case03["token_code"]) <= 6,
        "Có Term Sheet": bool(case03["token_name"].strip() and case03["token_code"].strip()),
        "Đủ 12 bước vòng đời": len(case03["lifecycle"]) >= 12,
        "Có Risk Register tối thiểu 14 nhóm rủi ro": len(case03["risks"]) >= 14,
        "Có khuyến nghị": bool(case03["recommendation"].strip()),
    }
    st.dataframe(pd.DataFrame({"Hạng mục": list(checks.keys()), "Trạng thái": ["Đạt" if v else "Chưa đạt" for v in checks.values()]}), use_container_width=True, hide_index=True)
    if all(checks.values()):
        st.success("Case 03 đã đạt bộ kiểm tra cơ bản.")
    else:
        st.warning("Case 03 chưa đạt đầy đủ bộ kiểm tra. Hoàn thiện các mục còn thiếu trước khi nộp.")

    st.session_state.case03 = case03
    return case03
