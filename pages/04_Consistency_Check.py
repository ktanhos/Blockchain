import streamlit as st
import pandas as pd

from database import load_project, save_project
from services.personalization import build_case_profile
from services.financial import calculate_financials
from services.case03 import default_case03
from services.consistency import check_consistency

st.set_page_config(page_title="Consistency Checker", page_icon="✓", layout="wide")
st.title("Consistency Checker · Ba Case")
st.caption("Kiểm tra đầy đủ 22 câu hỏi liên kết giữa Case 01, Case 02 và Case 03 theo đề bài.")

student_id = st.sidebar.text_input("Mã số sinh viên", value="")
if not student_id:
    st.info("Nhập mã số sinh viên để kiểm tra.")
    st.stop()
try:
    profile = build_case_profile(student_id)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

project_id = f"student_{''.join(ch for ch in student_id if ch.isdigit())}"
project = load_project(project_id)
if not project:
    st.warning("Chưa tìm thấy dự án. Hãy hoàn thành và lưu Case 01 trước.")
    st.stop()

financials = calculate_financials(profile)
case01 = project.get("case01") or {}
case02 = project.get("case02") or {}
case03 = project.get("case03") or default_case03(profile, financials)
arch = case01.get("architecture", {})

st.subheader("Khai báo liên kết còn thiếu")
st.info("Bộ kiểm tra không tự suy diễn các nội dung mang tính thiết kế. Các mục dưới đây phải được xác nhận rõ để hệ thống có thể kiểm tra 22 câu hỏi.")

with st.form("consistency_linkage"):
    st.markdown("**Case 02**")
    c21, c22 = st.columns(2)
    case02["blockchain_type"] = c21.selectbox("Loại blockchain sử dụng", [arch.get("blockchain_type", "")], index=0 if arch.get("blockchain_type") else None)
    case02["kyc_reuse"] = c22.checkbox("Tái sử dụng KYC từ Case 01", value=bool(case02.get("kyc_reuse", False)))
    case02["members"] = st.multiselect("Thành viên Case 02", list(arch.get("nodes", [])), default=[x for x in case02.get("members", []) if x in arch.get("nodes", [])])
    case02["oracle"] = st.text_area("Oracle Case 02 được sử dụng", value=str(case02.get("oracle", "")))
    case02["emergency_pause"] = st.checkbox("Có tái sử dụng cơ chế tạm dừng khẩn cấp", value=bool(case02.get("emergency_pause", False)))
    case02["upgrade_authority"] = st.text_input("Chủ thể nâng cấp hợp đồng Case 02", value=case02.get("upgrade_authority", ""))
    case02["conclusion"] = st.text_area("Kết luận Case 02", value=case02.get("conclusion", ""))
    case02["risks"] = case02.get("risks", case01.get("risks", []))

    st.markdown("**Case 03**")
    case03["blockchain_type"] = st.selectbox("Loại blockchain Case 03", [arch.get("blockchain_type", "")], index=0 if arch.get("blockchain_type") else None)
    case03["kyc_reuse"] = st.checkbox("Tái sử dụng KYC", value=bool(case03.get("kyc_reuse", False)))
    case03["oracle"] = st.text_area("Oracle Case 03 tái sử dụng từ Case 02", value=str(case03.get("oracle", "")))
    case03["pause"] = st.text_area("Cơ chế tạm dừng khẩn cấp", value=case03.get("pause", ""))
    case03["upgrade_authority"] = st.text_input("Chủ thể nâng cấp hợp đồng Case 03", value=case03.get("upgrade_authority", ""))
    case03["payment_priority"] = st.text_area("Thứ tự ưu tiên thanh toán", value=case03.get("payment_priority", ""))
    case03["legal_structure"] = st.text_area("Cấu trúc pháp lý và tổ chức phát hành", value=case03.get("legal_structure", ""))
    case03["legal_technical_gap"] = st.text_area("Khoảng cách giữa khả năng kỹ thuật và hiệu lực pháp lý", value=case03.get("legal_technical_gap", ""))
    case03["collateral_shared"] = st.checkbox("Dùng chung tài sản bảo đảm với khoản vay", value=bool(case03.get("collateral_shared", False)))
    case03["priority_rights"] = st.text_area("Quyền ưu tiên nếu dùng chung tài sản", value=case03.get("priority_rights", ""))
    case03["_annual_income"] = float(case03.get("_annual_income", 0))
    case03["members"] = st.multiselect("Thành viên Case 03", list(arch.get("nodes", [])), default=[x for x in case03.get("members", []) if x in arch.get("nodes", [])])
    case03["risks"] = case03.get("risks", [])

    save_linkage = st.form_submit_button("Lưu khai báo và chạy kiểm tra", type="primary")

if save_linkage:
    save_project(project_id, student_id, profile, case01, case02, case03)
    st.success("Đã lưu dữ liệu liên kết của ba Case.")
    project = load_project(project_id)
    case02 = project.get("case02") or {}
    case03 = project.get("case03") or case03

st.subheader("Tổng quan")
cols = st.columns(4)
cols[0].metric("Tổng nhu cầu vốn", f"{financials['V']:.2f} tỷ")
cols[1].metric("Khoản vay", f"{financials['LoanAmount']:.2f} tỷ")
cols[2].metric("External Capital", f"{financials['ExternalCapital']:.2f} tỷ")
cols[3].metric("DSCR", f"{financials['DSCR']:.2f}x")

checks = check_consistency(profile, financials, case01, case02, case03)
df = pd.DataFrame(checks)
passed = int((df["Trạng thái"] == "Đạt").sum())
failed = int((df["Trạng thái"] == "Lỗi").sum())

c1, c2, c3 = st.columns(3)
c1.metric("Tổng kiểm tra", len(df))
c2.metric("Đạt", passed)
c3.metric("Lỗi / chưa đủ dữ liệu", failed)
if failed == 0:
    st.success("Đã vượt qua toàn bộ 22 kiểm tra.")
else:
    st.warning(f"Còn {failed} kiểm tra chưa đạt. Không nên coi dự án là hoàn tất cho đến khi xử lý các mục này.")

st.subheader("Bộ kiểm tra 22 câu hỏi")
st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Chỉ xem các lỗi")
failed_df = df[df["Trạng thái"] == "Lỗi"]
if failed_df.empty:
    st.success("Không có lỗi.")
else:
    for _, row in failed_df.iterrows():
        st.error(f"{int(row['STT'])}. {row['Hạng mục']} — {row['Chi tiết']}")

st.subheader("Nguyên tắc")
st.markdown("Bộ kiểm tra bám đúng 22 câu hỏi liên kết của đề. Nó không tự thay đổi kết luận của Case trước. Nếu thiết kế được sửa để xử lý lỗi liên kết, thay đổi phải được ghi trong Nhật ký thay đổi thiết kế.")
