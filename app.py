import streamlit as st
import pandas as pd

from database import load_project, save_project
from services.personalization import build_case_profile
from services.financial import calculate_financials
from services.case01 import default_case01, MEMBERS, risk_dataframe
from services.case02_ui import render_case02
from services.case03 import default_case03
from services.case03_ui import render_case03
from services.consistency import check_consistency

st.set_page_config(page_title="Blockchain Finance Case Study", page_icon="⛓️", layout="wide")
st.title("Blockchain trong Tài chính và Ngân hàng")
st.caption("Phiên bản 1.1 · Case 01 + Case 02 + Case 03 + Consistency Checker")

st.sidebar.header("Hồ sơ sinh viên")
student_id = st.sidebar.text_input("Mã số sinh viên", value="")

if not student_id:
    st.info("Nhập mã số sinh viên ở thanh bên để bắt đầu.")
    st.stop()

try:
    profile = build_case_profile(student_id)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

project_id = f"student_{''.join(ch for ch in student_id if ch.isdigit())}"
existing = load_project(project_id)
if "project_id" not in st.session_state or st.session_state.get("project_id") != project_id:
    st.session_state.project_id = project_id
    st.session_state.case01 = existing["case01"] if existing and existing.get("case01") else default_case01()
    st.session_state.case03 = existing["case03"] if existing and existing.get("case03") else default_case03(profile, calculate_financials(profile))

case01 = st.session_state.case01
financials = calculate_financials(profile)

st.sidebar.success("Hồ sơ đã được cá nhân hóa")

def save_all():
    save_project(project_id, student_id, profile, st.session_state.case01, {}, st.session_state.case03)

if st.sidebar.button("Lưu toàn bộ"):
    save_all()
    st.sidebar.success("Đã lưu toàn bộ dữ liệu dự án")

st.subheader("Hồ sơ case cá nhân")
cols = st.columns(4)
for col, key in zip(cols, ["D1", "D2", "D3", "D4"]):
    col.metric(key, profile[key])

profile_df = pd.DataFrame({
    "Thông số": ["Ngành hoạt động", "Loại hình doanh nghiệp", "Vấn đề ngân hàng trọng tâm", "Công cụ huy động vốn Case 03"],
    "Giá trị": [profile["industry"], profile["business_type"], profile["banking_problem"], profile["funding_instrument"]],
})
st.dataframe(profile_df, width="stretch", hide_index=True)
st.divider()

case01_tab, case02_tab, case03_tab, check_tab = st.tabs([
    "Case 01 · Kiến trúc Blockchain",
    "Case 02 · Tín dụng Blockchain",
    "Case 03 · Huy động vốn bằng token",
    "Kiểm tra tính nhất quán",
])

with case01_tab:
    st.header("Case 01 · Thiết kế kiến trúc Blockchain")

    st.subheader("1. As-is Process")
    st.caption("Có thể sửa trực tiếp từng ô, thêm dòng, xóa dòng và thay đổi thứ tự. Nhập số thứ tự mong muốn vào cột Thứ tự rồi hệ thống sẽ sắp xếp lại quy trình.")
    as_is_df = pd.DataFrame(case01.get("as_is", []))
    if "Thứ tự" not in as_is_df.columns:
        as_is_df.insert(0, "Thứ tự", range(1, len(as_is_df) + 1))
    else:
        as_is_df["Thứ tự"] = pd.to_numeric(as_is_df["Thứ tự"], errors="coerce")
        missing = as_is_df["Thứ tự"].isna()
        if missing.any():
            as_is_df.loc[missing, "Thứ tự"] = range(1, int(missing.sum()) + 1)
    as_is_df["Thứ tự"] = as_is_df["Thứ tự"].astype(int)

    as_is_edited = st.data_editor(
        as_is_df,
        num_rows="dynamic",
        width="stretch",
        hide_index=True,
        column_config={
            "Thứ tự": st.column_config.NumberColumn("Thứ tự", min_value=1, step=1, help="Số càng nhỏ thì bước càng đứng trước."),
            "Bước": st.column_config.NumberColumn("Bước", disabled=True),
        },
        key="as_is_editor",
    )
    as_is_edited["Thứ tự"] = pd.to_numeric(as_is_edited["Thứ tự"], errors="coerce")
    missing = as_is_edited["Thứ tự"].isna()
    if missing.any():
        as_is_edited.loc[missing, "Thứ tự"] = range(1, int(missing.sum()) + 1)
    as_is_edited["Thứ tự"] = as_is_edited["Thứ tự"].astype(int)
    as_is_edited = as_is_edited.sort_values("Thứ tự", kind="stable").reset_index(drop=True)
    as_is_edited["Bước"] = range(1, len(as_is_edited) + 1)
    case01["as_is"] = as_is_edited.to_dict("records")

    step_count = len(case01["as_is"])
    if step_count >= 8:
        st.success(f"Đạt yêu cầu số bước: {step_count} bước")
    else:
        st.warning(f"Chưa đạt tối thiểu 8 bước. Hiện có {step_count} bước.")
    flow = [str(row.get("Hành động", "")) for row in case01["as_is"] if str(row.get("Hành động", "")).strip()]
    st.write(" → ".join(flow))

    st.subheader("2. Đánh giá CSDL tập trung so với Blockchain/DLT")
    st.caption("Có thể sửa điểm từ 1 đến 5, sửa tiêu chí, sửa giải thích, thêm tiêu chí hoặc xóa tiêu chí.")
    assessment_df = pd.DataFrame(case01.get("assessment", []))
    assessment_edited = st.data_editor(
        assessment_df,
        num_rows="dynamic",
        column_config={
            "CSDL tập trung": st.column_config.NumberColumn(min_value=1, max_value=5, step=1),
            "Blockchain/DLT": st.column_config.NumberColumn(min_value=1, max_value=5, step=1),
        },
        width="stretch",
        hide_index=True,
        key="assessment_editor",
    )
    case01["assessment"] = assessment_edited.to_dict("records")
    score_db = pd.to_numeric(assessment_edited.get("CSDL tập trung", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()
    score_chain = pd.to_numeric(assessment_edited.get("Blockchain/DLT", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng điểm CSDL", f"{score_db:.0f}")
    c2.metric("Tổng điểm Blockchain/DLT", f"{score_chain:.0f}")
    if score_chain > score_db:
        c3.info("Blockchain có điểm cao hơn")
    elif score_chain < score_db:
        c3.info("CSDL có điểm cao hơn")
    else:
        c3.info("Hai phương án bằng điểm")

    st.subheader("3. Kiến trúc mạng Blockchain")
    arch = case01["architecture"]
    decision_options = ["Go", "No-Go", "Hybrid"]
    model_options = ["Blockchain công khai", "Blockchain riêng tư", "Blockchain liên minh", "Blockchain lai", "Không sử dụng blockchain"]
    consensus_options = ["PBFT hoặc biến thể", "Proof of Authority", "Raft", "Xác nhận nhiều bên", "Biểu quyết theo tỷ lệ thành viên"]
    ac1, ac2 = st.columns(2)
    arch["decision"] = ac1.selectbox("Quyết định", decision_options, index=decision_options.index(arch.get("decision", "Hybrid")))
    arch["blockchain_type"] = ac2.selectbox("Mô hình", model_options, index=model_options.index(arch.get("blockchain_type", "Blockchain liên minh")))

    custom_members = arch.setdefault("custom_members", [])
    member_options = list(dict.fromkeys(MEMBERS + custom_members))
    arch["nodes"] = st.multiselect("Các thành viên/nút tham gia", member_options, default=[x for x in arch.get("nodes", []) if x in member_options])
    new_member = st.text_input("Thêm thành viên/nút tùy chỉnh", key="new_member_name", placeholder="Ví dụ: Công ty bảo hiểm A")
    if st.button("Thêm thành viên", key="add_member"):
        new_member = new_member.strip()
        if not new_member:
            st.warning("Chưa nhập tên thành viên.")
        elif new_member in member_options:
            st.warning("Thành viên này đã tồn tại.")
        else:
            custom_members.append(new_member)
            if new_member not in arch["nodes"]:
                arch["nodes"].append(new_member)
            case01["permissions"].append({"Chủ thể": new_member, "Đọc": True, "Ghi": False, "Xác thực": False, "Quản trị": False, "Tạm dừng": False})
            st.rerun()

    ac3, ac4 = st.columns(2)
    arch["consensus"] = ac3.selectbox("Cơ chế đồng thuận", consensus_options, index=consensus_options.index(arch.get("consensus", "PBFT hoặc biến thể")))
    max_validators = max(1, len(arch["nodes"]))
    arch["validator_count"] = ac4.number_input("Số nút xác thực", min_value=1, max_value=max_validators, value=min(int(arch.get("validator_count", 4)), max_validators), step=1)
    arch["completion"] = st.text_input("Thời điểm giao dịch được xem là hoàn tất", value=arch.get("completion", ""))

    st.subheader("4. Ma trận quyền truy cập")
    st.caption("Có thể sửa quyền trực tiếp. Các thành viên tùy chỉnh được thêm ở phần Kiến trúc mạng sẽ xuất hiện tại đây.")
    permission_members = set(arch.get("nodes", []))
    permissions = case01.get("permissions", [])
    existing_permission_members = {row.get("Chủ thể") for row in permissions}
    for member in permission_members - existing_permission_members:
        permissions.append({"Chủ thể": member, "Đọc": True, "Ghi": False, "Xác thực": False, "Quản trị": False, "Tạm dừng": False})
    case01["permissions"] = permissions
    perm_edited = st.data_editor(case01["permissions"], num_rows="dynamic", width="stretch", hide_index=True, key="permissions_editor")
    case01["permissions"] = perm_edited.to_dict("records")

    st.subheader("5. Phân loại dữ liệu On-chain và Off-chain")
    st.caption("Có thể sửa tên dữ liệu, thêm loại dữ liệu, xóa loại dữ liệu và thay đổi cách lưu trữ.")
    data_edited = st.data_editor(pd.DataFrame(case01["data"]), num_rows="dynamic", width="stretch", hide_index=True, key="data_editor")
    case01["data"] = data_edited.to_dict("records")
    invalid_storage = [row.get("Loại dữ liệu", "") for row in case01["data"] if bool(row.get("On-chain")) == bool(row.get("Off-chain"))]
    if invalid_storage:
        st.warning("Các dòng cần chọn đúng một vị trí lưu trữ: " + ", ".join(invalid_storage))

    st.subheader("6. Đồng thuận và quản trị mạng")
    gov = case01["governance"]
    for key, label in [("Chủ sở hữu nền tảng", "Ai sở hữu nền tảng?"), ("Tiếp nhận thành viên", "Ai được tiếp nhận thành viên mới?"), ("Thay đổi quy tắc", "Ai hoặc quy trình nào thay đổi quy tắc mạng?"), ("Nâng cấp hợp đồng", "Ai được nâng cấp hợp đồng thông minh?"), ("Tạm dừng hệ thống", "Ai có quyền tạm dừng hệ thống?"), ("Trách nhiệm giao dịch sai", "Ai chịu trách nhiệm khi giao dịch hoặc dữ liệu sai?"), ("Bồi thường", "Cơ chế bồi thường thiệt hại?"), ("Tranh chấp", "Cơ chế giải quyết tranh chấp?"), ("Lưu trữ dữ liệu", "Dữ liệu được lưu trữ tại đâu?"), ("Thành viên rời mạng", "Xử lý thành viên rời mạng như thế nào?")]:
        gov[key] = st.text_area(label, value=gov.get(key, ""), key=f"gov_{key}")

    st.subheader("7. Risk Register")
    st.caption("Có thể sửa tên rủi ro, nguyên nhân, xác suất, tác động, biện pháp và chủ sở hữu; có thể thêm hoặc xóa dòng. Điểm rủi ro tự tính bằng xác suất nhân tác động.")
    risk_edited = st.data_editor(risk_dataframe(case01["risks"]), num_rows="dynamic", column_config={"P": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "I": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "Điểm": st.column_config.NumberColumn(disabled=True)}, width="stretch", hide_index=True, key="risk_editor")
    case01["risks"] = risk_edited.to_dict("records")

    st.subheader("8. Kết luận Case 01")
    case01["conclusion"] = st.text_area("Kết luận của sinh viên", value=case01.get("conclusion", ""), height=120)
    if st.button("Lưu Case 01", type="primary", key="save_case01"):
        st.session_state.case01 = case01
        save_project(project_id, student_id, profile, case01, case03=st.session_state.case03)
        st.success("Đã lưu Case 01.")

with case02_tab:
    render_case02(st, financials)

with case03_tab:
    render_case03(st, profile, financials, save_callback=lambda data: save_project(project_id, student_id, profile, st.session_state.case01, {}, data))

with check_tab:
    st.header("Consistency Checker · Kiểm tra liên kết ba Case")
    st.caption("Kiểm tra tự động 22 câu hỏi liên kết giữa Case 01, Case 02 và Case 03.")
    existing_project = load_project(project_id) or {}
    case02_saved = existing_project.get("case02") or {}
    case03_saved = existing_project.get("case03") or st.session_state.case03
    results = check_consistency(profile, financials, st.session_state.case01, case02_saved, case03_saved)
    result_df = pd.DataFrame(results)
    st.dataframe(result_df, width="stretch", hide_index=True)
    errors = sum(x["Trạng thái"] == "Lỗi" for x in results)
    c1, c2 = st.columns(2)
    c1.metric("Tổng kiểm tra", len(results))
    c2.metric("Số lỗi", errors)
    if errors == 0:
        st.success("Không phát hiện lỗi trong 22 kiểm tra.")
    else:
        st.error(f"Phát hiện {errors} điểm cần xử lý trước khi nộp.")
    if st.button("Lưu kết quả kiểm tra", key="save_consistency"):
        st.session_state.consistency = results
        save_all()
        st.success("Đã lưu trạng thái dự án.")
