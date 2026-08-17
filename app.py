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
st.caption("Phiên bản 1.0 · Case 01 + Case 02 + Case 03 + Consistency Checker")

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
case03 = st.session_state.case03
financials = calculate_financials(profile)

st.sidebar.success("Hồ sơ đã được cá nhân hóa")

def save_all():
    save_project(project_id, student_id, profile, st.session_state.case01, {}, st.session_state.case03)

if st.sidebar.button("Lưu toàn bộ", use_container_width=True):
    save_all()
    st.sidebar.success("Đã lưu Case 01 và Case 03 vào SQLite")

st.subheader("Hồ sơ case cá nhân")
cols = st.columns(4)
for col, key in zip(cols, ["D1", "D2", "D3", "D4"]):
    col.metric(key, profile[key])

profile_df = pd.DataFrame({
    "Thông số": ["Ngành hoạt động", "Loại hình doanh nghiệp", "Vấn đề ngân hàng trọng tâm", "Công cụ huy động vốn Case 03"],
    "Giá trị": [profile["industry"], profile["business_type"], profile["banking_problem"], profile["funding_instrument"]],
})
st.dataframe(profile_df, use_container_width=True, hide_index=True)
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
    as_is_df = pd.DataFrame(case01["as_is"])
    as_is_edited = st.data_editor(as_is_df, num_rows="dynamic", use_container_width=True, key="as_is_editor")
    case01["as_is"] = as_is_edited.to_dict("records")
    step_count = len(case01["as_is"])
    if step_count >= 8:
        st.success(f"Đạt yêu cầu số bước: {step_count} bước")
    else:
        st.warning(f"Chưa đạt tối thiểu 8 bước. Hiện có {step_count} bước.")
    flow = [str(row.get("Hành động", "")) for row in case01["as_is"] if str(row.get("Hành động", "")).strip()]
    st.write(" → ".join(flow))

    st.subheader("2. Đánh giá CSDL tập trung so với Blockchain/DLT")
    assessment_edited = st.data_editor(pd.DataFrame(case01["assessment"]), column_config={"CSDL tập trung": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "Blockchain/DLT": st.column_config.NumberColumn(min_value=1, max_value=5, step=1)}, use_container_width=True, key="assessment_editor")
    case01["assessment"] = assessment_edited.to_dict("records")
    score_db = pd.to_numeric(assessment_edited["CSDL tập trung"], errors="coerce").fillna(0).sum()
    score_chain = pd.to_numeric(assessment_edited["Blockchain/DLT"], errors="coerce").fillna(0).sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng điểm CSDL", f"{score_db:.0f}")
    c2.metric("Tổng điểm Blockchain/DLT", f"{score_chain:.0f}")
    c3.info("Blockchain có điểm cao hơn" if score_chain > score_db else "CSDL có điểm cao hơn" if score_chain < score_db else "Hai phương án bằng điểm")

    st.subheader("3. Kiến trúc mạng Blockchain")
    arch = case01["architecture"]
    decision_options = ["Go", "No-Go", "Hybrid"]
    model_options = ["Blockchain công khai", "Blockchain riêng tư", "Blockchain liên minh", "Blockchain lai", "Không sử dụng blockchain"]
    consensus_options = ["PBFT hoặc biến thể", "Proof of Authority", "Raft", "Xác nhận nhiều bên", "Biểu quyết theo tỷ lệ thành viên"]
    ac1, ac2 = st.columns(2)
    arch["decision"] = ac1.selectbox("Quyết định", decision_options, index=decision_options.index(arch.get("decision", "Hybrid")))
    arch["blockchain_type"] = ac2.selectbox("Mô hình", model_options, index=model_options.index(arch.get("blockchain_type", "Blockchain liên minh")))
    arch["nodes"] = st.multiselect("Các thành viên/nút tham gia", MEMBERS, default=[x for x in arch.get("nodes", []) if x in MEMBERS])
    ac3, ac4 = st.columns(2)
    arch["consensus"] = ac3.selectbox("Cơ chế đồng thuận", consensus_options, index=consensus_options.index(arch.get("consensus", "PBFT hoặc biến thể")))
    arch["validator_count"] = ac4.number_input("Số nút xác thực", min_value=1, max_value=max(1, len(arch["nodes"])), value=min(int(arch.get("validator_count", 4)), max(1, len(arch["nodes"]))), step=1)
    arch["completion"] = st.text_input("Thời điểm giao dịch được xem là hoàn tất", value=arch.get("completion", ""))

    st.subheader("4. Ma trận quyền truy cập")
    perm_edited = st.data_editor(pd.DataFrame(case01["permissions"]), use_container_width=True, key="permissions_editor")
    case01["permissions"] = perm_edited.to_dict("records")

    st.subheader("5. Phân loại dữ liệu On-chain và Off-chain")
    data_edited = st.data_editor(pd.DataFrame(case01["data"]), use_container_width=True, key="data_editor")
    case01["data"] = data_edited.to_dict("records")
    invalid_storage = [row.get("Loại dữ liệu", "") for row in case01["data"] if bool(row.get("On-chain")) == bool(row.get("Off-chain"))]
    if invalid_storage:
        st.warning("Các dòng cần chọn đúng một vị trí lưu trữ: " + ", ".join(invalid_storage))

    st.subheader("6. Đồng thuận và quản trị mạng")
    gov = case01["governance"]
    for key, label in [("Chủ sở hữu nền tảng", "Ai sở hữu nền tảng?"), ("Tiếp nhận thành viên", "Ai được tiếp nhận thành viên mới?"), ("Thay đổi quy tắc", "Ai hoặc quy trình nào thay đổi quy tắc mạng?"), ("Nâng cấp hợp đồng", "Ai được nâng cấp hợp đồng thông minh?"), ("Tạm dừng hệ thống", "Ai có quyền tạm dừng hệ thống?"), ("Trách nhiệm giao dịch sai", "Ai chịu trách nhiệm khi giao dịch hoặc dữ liệu sai?"), ("Bồi thường", "Cơ chế bồi thường thiệt hại?"), ("Tranh chấp", "Cơ chế giải quyết tranh chấp?"), ("Lưu trữ dữ liệu", "Dữ liệu được lưu trữ tại đâu?"), ("Thành viên rời mạng", "Xử lý thành viên rời mạng như thế nào?")]:
        gov[key] = st.text_area(label, value=gov.get(key, ""), key=f"gov_{key}")

    st.subheader("7. Risk Register")
    risk_edited = st.data_editor(risk_dataframe(case01["risks"]), num_rows="dynamic", column_config={"P": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "I": st.column_config.NumberColumn(min_value=1, max_value=5, step=1), "Điểm": st.column_config.NumberColumn(disabled=True)}, use_container_width=True, key="risk_editor")
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
    st.dataframe(result_df, use_container_width=True, hide_index=True)
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
