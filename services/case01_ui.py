import pandas as pd
from services.case01 import risk_dataframe


def render_case01(st, case01):
    st.header("Case 01 · Thiết kế kiến trúc Blockchain")

    st.subheader("1. As-is Process")
    st.caption("Có thể sửa, thêm, xóa và thay đổi thứ tự. Dữ liệu được giữ trong phiên làm việc và tự động lưu vào dự án.")
    as_is_df = pd.DataFrame(case01.get("as_is", []))
    if "Thứ tự" not in as_is_df.columns:
        as_is_df.insert(0, "Thứ tự", range(1, len(as_is_df) + 1))
    as_is_df["Thứ tự"] = pd.to_numeric(as_is_df["Thứ tự"], errors="coerce")
    missing = as_is_df["Thứ tự"].isna()
    if missing.any():
        as_is_df.loc[missing, "Thứ tự"] = list(range(1, int(missing.sum()) + 1))
    as_is_df["Thứ tự"] = as_is_df["Thứ tự"].astype(int)
    edited = st.data_editor(as_is_df, num_rows="dynamic", width="stretch", hide_index=True, column_config={"Thứ tự": st.column_config.NumberColumn("Thứ tự", min_value=1, step=1), "Bước": st.column_config.NumberColumn("Bước", disabled=True)}, key="as_is_editor")
    edited["Thứ tự"] = pd.to_numeric(edited["Thứ tự"], errors="coerce")
    missing = edited["Thứ tự"].isna()
    if missing.any():
        edited.loc[missing, "Thứ tự"] = list(range(1, int(missing.sum()) + 1))
    edited["Thứ tự"] = edited["Thứ tự"].astype(int)
    edited = edited.sort_values("Thứ tự", kind="stable").reset_index(drop=True)
    edited["Bước"] = range(1, len(edited) + 1)
    case01["as_is"] = edited.to_dict("records")
    if len(case01["as_is"]) >= 8:
        st.success(f"Đạt yêu cầu số bước: {len(case01['as_is'])} bước")
    else:
        st.warning(f"Chưa đạt tối thiểu 8 bước. Hiện có {len(case01['as_is'])} bước.")

    st.subheader("2. Đánh giá CSDL tập trung so với Blockchain/DLT")
    assessment = st.data_editor(pd.DataFrame(case01.get("assessment", [])), num_rows="dynamic", column_config={"CSDL tập trung": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "Blockchain/DLT": st.column_config.NumberColumn(min_value=1, max_value=5, step=1)}, width="stretch", hide_index=True, key="assessment_editor")
    case01["assessment"] = assessment.to_dict("records")
    db_score = pd.to_numeric(assessment.get("CSDL tập trung", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()
    chain_score = pd.to_numeric(assessment.get("Blockchain/DLT", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng điểm CSDL", f"{db_score:.0f}")
    c2.metric("Tổng điểm Blockchain/DLT", f"{chain_score:.0f}")
    c3.info("Blockchain có điểm cao hơn" if chain_score > db_score else "CSDL có điểm cao hơn" if chain_score < db_score else "Hai phương án bằng điểm")

    st.subheader("3. Kiến trúc mạng Blockchain")
    arch = case01.setdefault("architecture", {})
    decisions = ["Go", "No-Go", "Hybrid"]
    models = ["Blockchain công khai", "Blockchain riêng tư", "Blockchain liên minh", "Blockchain lai", "Không sử dụng blockchain"]
    consensuses = ["PBFT hoặc biến thể", "Proof of Authority", "Raft", "Xác nhận nhiều bên", "Biểu quyết theo tỷ lệ thành viên"]
    a1, a2 = st.columns(2)
    arch["decision"] = a1.selectbox("Quyết định", decisions, index=decisions.index(arch.get("decision", "Hybrid")) if arch.get("decision") in decisions else 2, key="case01_decision")
    arch["blockchain_type"] = a2.selectbox("Mô hình", models, index=models.index(arch.get("blockchain_type", "Blockchain liên minh")) if arch.get("blockchain_type") in models else 2, key="case01_blockchain_type")
    custom = arch.setdefault("custom_members", [])
    members = list(dict.fromkeys(["FutureBank", "Ngân hàng đối tác", "Doanh nghiệp", "Nhà cung cấp", "Khách hàng/người mua", "Logistics", "Kiểm toán viên", "Cơ quan quản lý"] + custom))
    arch["nodes"] = st.multiselect("Các thành viên/nút tham gia", members, default=[x for x in arch.get("nodes", []) if x in members], key="case01_nodes")
    new_member = st.text_input("Thêm thành viên/nút tùy chỉnh", key="new_member_name", placeholder="Ví dụ: Công ty bảo hiểm A")
    if st.button("Thêm thành viên", key="add_member"):
        new_member = new_member.strip()
        if new_member and new_member not in members:
            custom.append(new_member)
            arch["nodes"] = list(dict.fromkeys(arch.get("nodes", []) + [new_member]))
            case01.setdefault("permissions", []).append({"Chủ thể": new_member, "Đọc": True, "Ghi": False, "Xác thực": False, "Quản trị": False, "Tạm dừng": False})
            st.rerun()
    a3, a4 = st.columns(2)
    arch["consensus"] = a3.selectbox("Cơ chế đồng thuận", consensuses, index=consensuses.index(arch.get("consensus", "PBFT hoặc biến thể")) if arch.get("consensus") in consensuses else 0, key="case01_consensus")
    arch["validator_count"] = a4.number_input("Số nút xác thực", min_value=1, max_value=max(1, len(arch.get("nodes", []))), value=min(int(arch.get("validator_count", 4)), max(1, len(arch.get("nodes", [])))), step=1, key="case01_validator_count")
    arch["completion"] = st.text_input("Thời điểm giao dịch được xem là hoàn tất", value=arch.get("completion", ""), key="case01_completion")

    st.subheader("4. Ma trận quyền truy cập")
    permissions = case01.setdefault("permissions", [])
    existing = {row.get("Chủ thể") for row in permissions}
    for member in arch.get("nodes", []):
        if member not in existing:
            permissions.append({"Chủ thể": member, "Đọc": True, "Ghi": False, "Xác thực": False, "Quản trị": False, "Tạm dừng": False})
    perm = st.data_editor(pd.DataFrame(permissions), num_rows="dynamic", width="stretch", hide_index=True, key="permissions_editor")
    case01["permissions"] = perm.to_dict("records")

    st.subheader("5. Phân loại dữ liệu On-chain và Off-chain")
    st.caption("Có thể chọn cả hai khi một dữ liệu có trạng thái hoặc mã băm trên chuỗi nhưng hồ sơ chi tiết vẫn lưu ngoài chuỗi.")
    data = st.data_editor(pd.DataFrame(case01.get("data", [])), num_rows="dynamic", width="stretch", hide_index=True, key="data_editor")
    case01["data"] = data.to_dict("records")
    invalid = [row.get("Loại dữ liệu", "") for row in case01["data"] if not bool(row.get("On-chain")) and not bool(row.get("Off-chain"))]
    if invalid:
        st.warning("Các dòng chưa chọn vị trí lưu trữ: " + ", ".join(invalid))

    st.subheader("6. Đồng thuận và quản trị mạng")
    gov = case01.setdefault("governance", {})
    fields = [("Chủ sở hữu nền tảng", "Ai sở hữu nền tảng?"), ("Tiếp nhận thành viên", "Ai được tiếp nhận thành viên mới?"), ("Thay đổi quy tắc", "Ai hoặc quy trình nào thay đổi quy tắc mạng?"), ("Nâng cấp hợp đồng", "Ai được nâng cấp hợp đồng thông minh?"), ("Tạm dừng hệ thống", "Ai có quyền tạm dừng hệ thống?"), ("Quản lý khóa", "Ai quản lý khóa, cấp lại khóa và xử lý mất khóa của nút?"), ("Trách nhiệm giao dịch sai", "Ai chịu trách nhiệm khi giao dịch hoặc dữ liệu sai?"), ("Bồi thường", "Cơ chế bồi thường thiệt hại?"), ("Tranh chấp", "Cơ chế giải quyết tranh chấp?"), ("Lưu trữ dữ liệu", "Dữ liệu được lưu trữ tại đâu?"), ("Thành viên rời mạng", "Xử lý thành viên rời mạng như thế nào?")]
    for key, label in fields:
        gov[key] = st.text_area(label, value=gov.get(key, ""), key=f"gov_{key}")

    st.subheader("7. Risk Register")
    risk = st.data_editor(risk_dataframe(case01.get("risks", [])), num_rows="dynamic", column_config={"P": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "I": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "Điểm": st.column_config.NumberColumn(disabled=True)}, width="stretch", hide_index=True, key="risk_editor")
    case01["risks"] = risk.to_dict("records")

    st.subheader("8. Kết luận Case 01")
    case01["conclusion"] = st.text_area("Kết luận của sinh viên", value=case01.get("conclusion", ""), height=120, key="case01_conclusion")
    return case01
