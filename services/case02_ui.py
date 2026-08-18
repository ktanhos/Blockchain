import pandas as pd
from services.case02 import oracle_defaults, scenario_defaults, evaluate_credit, smart_contract_events, default_case02
from services.case01 import risk_dataframe


def render_case02(st, financials, case01=None):
    if "case02" not in st.session_state or not st.session_state.case02:
        st.session_state.case02 = default_case02(financials, case01 or {})
    case02 = st.session_state.case02
    case01 = case01 or {}

    st.header("Case 02 · Tín dụng Blockchain")
    st.caption("Case 02 nhận dữ liệu từ Case 01. Các trường kế thừa được hiển thị rõ để sinh viên kiểm tra trước khi sử dụng.")

    st.subheader("1. Hồ sơ tín dụng chuyển tiếp")
    credit_items = [("Tổng nhu cầu vốn", f"{financials['V']:.2f} tỷ"), ("Khoản vay", f"{financials['LoanAmount']:.2f} tỷ"), ("Vốn còn thiếu", f"{financials['ExternalCapital']:.2f} tỷ"), ("Thời hạn", f"{financials['T']} năm"), ("Lãi suất", f"{financials['r']*100:.2f}%"), ("Tài sản bảo đảm", f"{financials['CollateralValue']:.2f} tỷ")]
    for row_start in range(0, len(credit_items), 3):
        cols = st.columns(3)
        for col, (label, display) in zip(cols, credit_items[row_start:row_start + 3]):
            col.metric(label, display)

    st.subheader("2. Dữ liệu kế thừa từ Case 01")
    c1, c2 = st.columns(2)
    c1.info(f"Blockchain: {case02.get('blockchain_type', '')}")
    c2.info(f"Đồng thuận: {case02.get('consensus', '')}")
    st.dataframe(pd.DataFrame({"Thành viên mạng": case02.get("members", [])}), width="stretch", hide_index=True)

    st.subheader("3. KYC và quản trị liên kết")
    case02["kyc_reuse"] = st.checkbox("Sử dụng lại hệ thống KYC từ Case 01", value=bool(case02.get("kyc_reuse", False)), key="case02_kyc_reuse")
    case02["kyc_reference"] = st.text_area("Mô tả cách KYC Case 01 được sử dụng lại", value=case02.get("kyc_reference", ""), key="case02_kyc_reference", height=90)
    case02["emergency_pause"] = st.checkbox("Có cơ chế tạm dừng khẩn cấp", value=bool(case02.get("emergency_pause", False)), key="case02_emergency_pause")
    case02["pause_authority"] = st.text_area("Chủ thể và điều kiện tạm dừng khẩn cấp", value=case02.get("pause_authority", ""), key="case02_pause_authority", height=90)
    case02["upgrade_authority"] = st.text_area("Chủ thể có quyền nâng cấp hợp đồng", value=case02.get("upgrade_authority", ""), key="case02_upgrade_authority", height=90)

    st.subheader("4. Phân tích tín dụng")
    metrics = evaluate_credit(financials, "Cơ sở")
    case02["DSCR"] = metrics["DSCR"]
    case02["LTV"] = metrics["LTV"]
    c1, c2, c3 = st.columns(3)
    c1.metric("DSCR", f"{metrics['DSCR']:.2f}x")
    c2.metric("LTV", f"{metrics['LTV']*100:.2f}%")
    c3.metric("Trạng thái", metrics["Trạng thái"])

    st.subheader("5. To Be Process")
    to_be_defaults = case02.get("to_be") or [{"Thứ tự": i + 1, "Bước": i + 1, "Chủ thể": "", "Hành động": action, "Dữ liệu": "", "Hệ thống": "Blockchain/CBS", "Điều kiện": "", "Kết quả": ""} for i, action in enumerate(["Tiếp nhận hồ sơ và tham chiếu KYC", "Xác minh KYC và AML", "Xác minh hóa đơn", "Xác nhận giao hàng", "Xác minh tài sản bảo đảm", "Đánh giá tín dụng", "Oracle cập nhật dữ liệu", "Hợp đồng thông minh kiểm tra điều kiện", "Phê duyệt tín dụng", "Giải ngân và ghi nhận trạng thái"])]
    to_be_edited = st.data_editor(pd.DataFrame(to_be_defaults), num_rows="dynamic", width="stretch", hide_index=True, key="case02_to_be_editor")
    case02["to_be"] = to_be_edited.to_dict("records")

    st.subheader("6. Oracle")
    oracle_edited = st.data_editor(pd.DataFrame(case02.get("oracle") or oracle_defaults()), num_rows="dynamic", width="stretch", key="case02_oracle_editor")
    case02["oracle"] = oracle_edited.to_dict("records")
    case02["oracle_reuse"] = st.checkbox("Case 03 được phép tái sử dụng Oracle của Case 02", value=bool(case02.get("oracle_reuse", False)), key="case02_oracle_reuse")
    if not case02["oracle_reuse"]:
        st.warning("Case 03 sẽ không được coi là kế thừa Oracle nếu chưa bật cơ chế tái sử dụng.")

    st.subheader("7. Ba kịch bản tín dụng")
    scenarios = scenario_defaults(financials)
    scenario_rows = [{"Kịch bản": name, "Doanh thu": data["Revenue1"], "Biên EBITDA": data["EbitdaMargin"], "EBITDA": data["EBITDA1"], "DSCR": data["DSCR"], "Tài sản bảo đảm": data["CollateralValue"], "LTV": data["LTV"]} for name, data in scenarios.items()]
    st.dataframe(pd.DataFrame(scenario_rows), width="stretch", hide_index=True)
    selected = st.selectbox("Kịch bản mô phỏng", list(scenarios.keys()), key="case02_selected_scenario")
    selected_eval = evaluate_credit(financials, selected)
    a, b, c = st.columns(3)
    a.metric("DSCR", f"{selected_eval['DSCR']:.2f}x")
    b.metric("LTV", f"{selected_eval['LTV']*100:.2f}%")
    c.metric("Trạng thái", selected_eval["Trạng thái"])

    st.subheader("8. Mô phỏng hợp đồng thông minh")
    x1, x2 = st.columns(2)
    kyc = x1.checkbox("KYC hợp lệ", value=True, key="case02_sim_kyc")
    aml = x1.checkbox("Không có cảnh báo AML", value=True, key="case02_sim_aml")
    invoice = x2.checkbox("Hóa đơn hợp lệ và chưa được tài trợ", value=True, key="case02_sim_invoice")
    delivery = x2.checkbox("Đã xác nhận giao hàng", value=True, key="case02_sim_delivery")
    events = smart_contract_events(kyc_valid=kyc, aml_clear=aml, invoice_valid=invoice, delivery_confirmed=delivery, ltv=selected_eval["LTV"])
    st.dataframe(pd.DataFrame(events), width="stretch", hide_index=True)

    st.subheader("9. Tình huống sự kiện")
    event = st.selectbox("Chọn sự kiện", ["KYC không hợp lệ", "Hóa đơn đã được tài trợ", "Chưa xác nhận giao hàng", "LTV vượt ngưỡng cảnh báo", "LTV vượt ngưỡng xử lý tài sản", "Điều kiện đầy đủ"], key="case02_event")
    mapping = {"KYC không hợp lệ": (False, True, True, True, selected_eval["LTV"]), "Hóa đơn đã được tài trợ": (True, True, False, True, selected_eval["LTV"]), "Chưa xác nhận giao hàng": (True, True, True, False, selected_eval["LTV"]), "LTV vượt ngưỡng cảnh báo": (True, True, True, True, 0.70), "LTV vượt ngưỡng xử lý tài sản": (True, True, True, True, 0.80), "Điều kiện đầy đủ": (True, True, True, True, min(selected_eval["LTV"], 0.69))}
    args = mapping[event]
    st.dataframe(pd.DataFrame(smart_contract_events(kyc_valid=args[0], invoice_valid=args[2], delivery_confirmed=args[3], aml_clear=args[1], ltv=args[4])), width="stretch", hide_index=True)
    case02["smart_contract"] = "KYC hợp lệ, AML không có cảnh báo, hóa đơn hợp lệ, giao hàng đã xác nhận; LTV vượt ngưỡng kích hoạt cảnh báo hoặc xử lý tài sản."

    st.subheader("10. Risk Register chuyển tiếp")
    st.caption("Các rủi ro này được khởi tạo từ Risk Register Case 01. Có thể sửa, thêm hoặc xóa. Nếu xóa toàn bộ, Consistency Checker sẽ phản ánh đúng việc mất liên kết rủi ro.")
    risk_edited = st.data_editor(risk_dataframe(case02.get("risks", [])), num_rows="dynamic", column_config={"P": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "I": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "Điểm": st.column_config.NumberColumn(disabled=True)}, width="stretch", hide_index=True, key="case02_risk_editor")
    case02["risks"] = risk_edited.to_dict("records")

    st.subheader("11. Kết luận Case 02")
    case02["conclusion"] = st.text_area("Kết luận của sinh viên", value=case02.get("conclusion", ""), key="case02_conclusion", height=140)
    st.session_state.case02 = case02
    return case02
