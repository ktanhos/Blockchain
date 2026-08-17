import streamlit as st
import pandas as pd

from database import load_project, save_project
from services.personalization import build_case_profile
from services.financial import calculate_financials
from services.case01 import default_case01, MEMBERS, risk_dataframe

st.set_page_config(page_title="Blockchain Finance Case Study", page_icon="⛓️", layout="wide")
st.title("Blockchain trong Tài chính và Ngân hàng")
st.caption("Phiên bản 0.2 · Case 01: FutureBank Blockchain Blueprint")

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
if "case01" not in st.session_state or st.session_state.get("project_id") != project_id:
    st.session_state.project_id = project_id
    st.session_state.case01 = existing["case01"] if existing and existing.get("case01") else default_case01()
case01 = st.session_state.case01

st.sidebar.success("Hồ sơ đã được cá nhân hóa")

st.subheader("Hồ sơ case cá nhân")
cols = st.columns(4)
for col, key in zip(cols, ["D1", "D2", "D3", "D4"]):
    col.metric(key, profile[key])
st.dataframe(pd.DataFrame({
    "Thông số": ["Ngành hoạt động", "Loại hình doanh nghiệp", "Vấn đề ngân hàng trọng tâm", "Công cụ huy động vốn Case 03"],
    "Giá trị": [profile["industry"], profile["business_type"], profile["banking_problem"], profile["funding_instrument"]],
}), use_container_width=True, hide_index=True)

financials = calculate_financials(profile)
with st.expander("Thông số tài chính chuyển tiếp sang Case 02", expanded=False):
    fcols = st.columns(4)
    fcols[0].metric("Tổng nhu cầu vốn", f"{financials['V']:.2f} tỷ")
    fcols[1].metric("Khoản vay", f"{financials['LoanAmount']:.2f} tỷ")
    fcols[2].metric("Vốn còn thiếu", f"{financials['ExternalCapital']:.2f} tỷ")
    fcols[3].metric("DSCR", f"{financials['DSCR']:.2f}x")

st.divider()
st.header("Case 01 · Thiết kế kiến trúc Blockchain")

st.subheader("1. As-is Process")
st.caption("Tối thiểu 8 bước; thể hiện chủ thể, dữ liệu, hệ thống, nhập lại, đối chiếu, rủi ro và trách nhiệm.")
as_is_edited = st.data_editor(pd.DataFrame(case01["as_is"]), num_rows="dynamic", use_container_width=True, key="as_is_editor")
case01["as_is"] = as_is_edited.to_dict("records")
if len(case01["as_is"]) >= 8:
    st.success(f"Đạt yêu cầu số bước: {len(case01['as_is'])} bước")
else:
    st.warning(f"Chưa đạt tối thiểu 8 bước. Hiện có {len(case01['as_is'])} bước.")
st.markdown("**Chuỗi quy trình hiện tại**")
flow = [str(row.get("Hành động", "")) for row in case01["as_is"] if str(row.get("Hành động", "")).strip()]
st.write(" → ".join(flow))

st.subheader("2. Đánh giá CSDL tập trung so với Blockchain/DLT")
st.caption("Chấm điểm từ 1 đến 5 theo mức độ phù hợp với tình huống của case và ghi rõ lý do.")
assessment_edited = st.data_editor(
    pd.DataFrame(case01["assessment"]),
    column_config={
        "CSDL tập trung": st.column_config.NumberColumn(min_value=1, max_value=5, step=1),
        "Blockchain/DLT": st.column_config.NumberColumn(min_value=1, max_value=5, step=1),
    },
    use_container_width=True,
    key="assessment_editor",
)
case01["assessment"] = assessment_edited.to_dict("records")
score_db = pd.to_numeric(assessment_edited["CSDL tập trung"], errors="coerce").fillna(0).sum()
score_chain = pd.to_numeric(assessment_edited["Blockchain/DLT"], errors="coerce").fillna(0).sum()
sc1, sc2, sc3 = st.columns(3)
sc1.metric("Tổng điểm CSDL", f"{score_db:.0f}")
sc2.metric("Tổng điểm Blockchain/DLT", f"{score_chain:.0f}")
sc3.info("Blockchain/DLT đang cao hơn" if score_chain > score_db else "CSDL tập trung đang cao hơn" if score_chain < score_db else "Hai phương án bằng điểm")
st.info("Tổng điểm chỉ là chỉ báo hỗ trợ. Kết luận Go, No-Go hoặc Hybrid vẫn phải dựa trên giải thích, pháp lý, chi phí, tích hợp và giá trị kinh tế.")

st.subheader("3. Kiến trúc mạng Blockchain")
arch = case01["architecture"]
arch["decision"] = st.selectbox("Quyết định", ["Go", "No-Go", "Hybrid"], index=["Go", "No-Go", "Hybrid"].index(arch.get("decision", "Hybrid")))
arch["blockchain_type"] = st.selectbox("Mô hình", ["Blockchain công khai", "Blockchain riêng tư", "Blockchain liên minh", "Blockchain lai", "Không sử dụng blockchain"], index=["Blockchain công khai", "Blockchain riêng tư", "Blockchain liên minh", "Blockchain lai", "Không sử dụng blockchain"].index(arch.get("blockchain_type", "Blockchain liên minh")))
arch["nodes"] = st.multiselect("Các thành viên/nút tham gia", MEMBERS, default=[x for x in arch.get("nodes", []) if x in MEMBERS])
ac1, ac2 = st.columns(2)
arch["consensus"] = ac1.selectbox("Cơ chế đồng thuận", ["PBFT hoặc biến thể", "Proof of Authority", "Raft", "Xác nhận nhiều bên", "Biểu quyết theo tỷ lệ thành viên"], index=["PBFT hoặc biến thể", "Proof of Authority", "Raft", "Xác nhận nhiều bên", "Biểu quyết theo tỷ lệ thành viên"].index(arch.get("consensus", "PBFT hoặc biến thể")))
arch["validator_count"] = ac2.number_input("Số nút xác thực", min_value=1, max_value=max(1, len(arch["nodes"])), value=min(int(arch.get("validator_count", 4)), max(1, len(arch["nodes"]))), step=1)
arch["completion"] = st.text_input("Thời điểm giao dịch được xem là hoàn tất", value=arch.get("completion", ""))

st.subheader("4. Ma trận quyền truy cập")
perm_edited = st.data_editor(pd.DataFrame(case01["permissions"]), use_container_width=True, key="permissions_editor")
case01["permissions"] = perm_edited.to_dict("records")

st.subheader("5. Phân loại dữ liệu On-chain và Off-chain")
st.caption("Tối thiểu 10 loại dữ liệu; xác định vị trí lưu trữ, chủ thể được truy cập và lý do.")
data_edited = st.data_editor(pd.DataFrame(case01["data"]), use_container_width=True, key="data_editor")
case01["data"] = data_edited.to_dict("records")
invalid_storage = [row.get("Loại dữ liệu", "Không xác định") for row in case01["data"] if bool(row.get("On-chain")) == bool(row.get("Off-chain"))]
if invalid_storage:
    st.warning("Các dòng cần chọn đúng một vị trí lưu trữ: " + ", ".join(invalid_storage))
else:
    st.success("Phân loại On-chain/Off-chain hợp lệ.")

st.subheader("6. Đồng thuận và quản trị mạng")
gov = case01["governance"]
for key, label in [
    ("Chủ sở hữu nền tảng", "Ai sở hữu nền tảng?"),
    ("Tiếp nhận thành viên", "Ai được tiếp nhận thành viên mới?"),
    ("Thay đổi quy tắc", "Ai/quy trình nào thay đổi quy tắc mạng?"),
    ("Nâng cấp hợp đồng", "Ai được nâng cấp hợp đồng thông minh?"),
    ("Tạm dừng hệ thống", "Ai có quyền tạm dừng hệ thống?"),
    ("Trách nhiệm giao dịch sai", "Ai chịu trách nhiệm khi giao dịch hoặc dữ liệu sai?"),
    ("Bồi thường", "Cơ chế bồi thường thiệt hại?"),
    ("Tranh chấp", "Cơ chế giải quyết tranh chấp?"),
    ("Lưu trữ dữ liệu", "Dữ liệu được lưu trữ tại đâu?"),
    ("Thành viên rời mạng", "Xử lý thành viên rời mạng như thế nào?"),
]:
    gov[key] = st.text_area(label, value=gov.get(key, ""), key=f"gov_{key}")

st.subheader("7. Risk Register")
st.caption("Risk Score = Probability × Impact. Xác suất và tác động từ 1 đến 5; tối thiểu 10 rủi ro.")
risk_edited = st.data_editor(
    risk_dataframe(case01["risks"]),
    num_rows="dynamic",
    column_config={
        "P": st.column_config.NumberColumn(min_value=1, max_value=5, step=1),
        "I": st.column_config.NumberColumn(min_value=1, max_value=5, step=1),
        "Điểm": st.column_config.NumberColumn(disabled=True),
    },
    use_container_width=True,
    key="risk_editor",
)
case01["risks"] = risk_edited.to_dict("records")
if len(case01["risks"]) >= 10:
    st.success(f"Đạt tối thiểu Risk Register: {len(case01['risks'])} rủi ro")
else:
    st.warning(f"Chưa đạt tối thiểu 10 rủi ro: hiện có {len(case01['risks'])}")
if not risk_edited.empty and "Điểm" in risk_edited.columns:
    st.write(f"Rủi ro điểm từ 15 trở lên: {len(risk_edited[risk_edited['Điểm'] >= 15])}")

st.subheader("8. Kết luận Case 01")
case01["conclusion"] = st.text_area("Kết luận của sinh viên", value=case01.get("conclusion", ""), height=120)

checks = {
    "As-is có tối thiểu 8 bước": len(case01["as_is"]) >= 8,
    "Có đánh giá CSDL và Blockchain": len(case01["assessment"]) >= 12,
    "Có thành viên mạng": len(arch.get("nodes", [])) >= 1,
    "Có ma trận quyền": len(case01["permissions"]) >= len(MEMBERS),
    "Có tối thiểu 10 loại dữ liệu": len(case01["data"]) >= 10,
    "Có Risk Register tối thiểu 10 rủi ro": len(case01["risks"]) >= 10,
    "Có kết luận": bool(case01.get("conclusion", "").strip()),
}
st.dataframe(pd.DataFrame({"Hạng mục": list(checks.keys()), "Trạng thái": ["Đạt" if v else "Chưa đạt" for v in checks.values()]}), use_container_width=True, hide_index=True)

ready = all(checks.values())
if ready:
    st.success("Case 01 đã đủ các điều kiện kiểm tra cơ bản. Có thể dùng làm đầu vào cho Case 02.")
else:
    st.warning("Case 01 chưa đủ điều kiện kiểm tra cơ bản. Hãy hoàn thiện các mục còn thiếu trước khi chuyển sang Case 02.")

if st.button("Lưu Case 01", type="primary", use_container_width=True):
    st.session_state.case01 = case01
    save_project(project_id, student_id, profile, case01)
    st.success("Đã lưu Case 01 vào SQLite. Case 02 sau này sẽ đọc trực tiếp dữ liệu này, không cần nhập lại.")
