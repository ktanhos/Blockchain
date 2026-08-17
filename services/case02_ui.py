import pandas as pd
from services.case02 import oracle_defaults, scenario_defaults, evaluate_credit, smart_contract_events


def render_case02(st, financials):
    st.header("Case 02 · Tín dụng Blockchain")
    st.caption("Case 02 sử dụng trực tiếp các thông số tài chính từ Case 01, không nhập lại.")

    st.subheader("1. Hồ sơ tín dụng chuyển tiếp")
    cols = st.columns(6)
    for col, key, label in zip(cols, ["V", "LoanAmount", "ExternalCapital", "T", "r", "CollateralValue"], ["Tổng nhu cầu vốn", "Khoản vay", "Vốn còn thiếu", "Thời hạn", "Lãi suất", "Tài sản bảo đảm"]):
        value = financials[key]
        suffix = " tỷ" if key not in ["T", "r"] else (" năm" if key == "T" else "%")
        display = f"{value:.2f}{suffix}" if key != "r" else f"{value*100:.2f}%"
        col.metric(label, display)

    st.subheader("2. Phân tích tín dụng")
    metrics = evaluate_credit(financials, "Cơ sở")
    c1, c2, c3 = st.columns(3)
    c1.metric("DSCR", f"{metrics['DSCR']:.2f}x")
    c2.metric("LTV", f"{metrics['LTV']*100:.2f}%")
    c3.metric("Trạng thái", metrics["Trạng thái"])
    st.info("Ngưỡng cảnh báo trong mô phỏng được dùng để vận hành bộ luật Case 02; cần đối chiếu lại với ngưỡng chính thức của đề nếu tài liệu quy định khác.")

    st.subheader("3. Oracle")
    oracle_df = pd.DataFrame(oracle_defaults())
    oracle_edited = st.data_editor(oracle_df, num_rows="dynamic", use_container_width=True, key="oracle_editor")
    st.session_state.case02_oracle = oracle_edited.to_dict("records")

    st.subheader("4. Ba kịch bản")
    scenarios = scenario_defaults(financials)
    scenario_rows = []
    for name, data in scenarios.items():
        scenario_rows.append({"Kịch bản": name, "Doanh thu": data["Revenue1"], "Biên EBITDA": data["EbitdaMargin"], "EBITDA": data["EBITDA1"], "DSCR": data["DSCR"], "Tài sản bảo đảm": data["CollateralValue"], "LTV": data["LTV"]})
    st.dataframe(pd.DataFrame(scenario_rows), use_container_width=True, hide_index=True)
    selected = st.selectbox("Kịch bản mô phỏng", list(scenarios.keys()))
    selected_eval = evaluate_credit(financials, selected)
    a, b, c = st.columns(3)
    a.metric("DSCR", f"{selected_eval['DSCR']:.2f}x")
    b.metric("LTV", f"{selected_eval['LTV']*100:.2f}%")
    c.metric("Trạng thái", selected_eval["Trạng thái"])

    st.subheader("5. Mô phỏng hợp đồng thông minh")
    x1, x2 = st.columns(2)
    kyc = x1.checkbox("KYC hợp lệ", value=True)
    aml = x1.checkbox("Không có cảnh báo AML", value=True)
    invoice = x2.checkbox("Hóa đơn hợp lệ và chưa được tài trợ", value=True)
    delivery = x2.checkbox("Đã xác nhận giao hàng", value=True)
    events = smart_contract_events(kyc_valid=kyc, aml_clear=aml, invoice_valid=invoice, delivery_confirmed=delivery, ltv=selected_eval["LTV"])
    st.dataframe(pd.DataFrame(events), use_container_width=True, hide_index=True)

    st.subheader("6. Tình huống sự kiện")
    event = st.selectbox("Chọn sự kiện", ["KYC không hợp lệ", "Hóa đơn đã được tài trợ", "Chưa xác nhận giao hàng", "LTV vượt ngưỡng cảnh báo", "LTV vượt ngưỡng xử lý tài sản", "Điều kiện đầy đủ"])
    mapping = {
        "KYC không hợp lệ": (False, True, True, True, selected_eval["LTV"]),
        "Hóa đơn đã được tài trợ": (True, True, False, True, selected_eval["LTV"]),
        "Chưa xác nhận giao hàng": (True, True, True, False, selected_eval["LTV"]),
        "LTV vượt ngưỡng cảnh báo": (True, True, True, True, 0.70),
        "LTV vượt ngưỡng xử lý tài sản": (True, True, True, True, 0.80),
        "Điều kiện đầy đủ": (True, True, True, True, min(selected_eval["LTV"], 0.69)),
    }
    args = mapping[event]
    st.dataframe(pd.DataFrame(smart_contract_events(kyc_valid=args[0], invoice_valid=args[2], delivery_confirmed=args[3], aml_clear=args[1], ltv=args[4])), use_container_width=True, hide_index=True)

    st.success("Case 02 đã có lớp tín dụng, Oracle, kịch bản và mô phỏng hợp đồng thông minh. Dữ liệu đầu vào lấy trực tiếp từ Case 01.")
