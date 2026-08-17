import streamlit as st
import pandas as pd

from database import load_project
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
    st.warning("Chưa tìm thấy dự án. Hãy lưu Case 01 trước khi kiểm tra.")
    st.stop()

financials = calculate_financials(profile)
case01 = project.get("case01") or {}
case02 = project.get("case02") or {}
case03 = project.get("case03") or default_case03(profile, financials)

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
st.dataframe(df, use_container_width=True, hide_index=True, column_config={
    "STT": st.column_config.NumberColumn(width="small"),
    "Trạng thái": st.column_config.TextColumn(width="small"),
})

st.subheader("Chỉ xem các lỗi")
failed_df = df[df["Trạng thái"] == "Lỗi"]
if failed_df.empty:
    st.success("Không có lỗi.")
else:
    for _, row in failed_df.iterrows():
        st.error(f"{int(row['STT'])}. {row['Hạng mục']} — {row['Chi tiết']}")

st.subheader("Nguyên tắc xử lý")
st.markdown("""
Các mục kiểm tra được chia thành ba loại. Mục Đạt nghĩa là dữ liệu hiện có thỏa điều kiện tự động. Mục Lỗi nghĩa là dữ liệu thiếu hoặc đang có dấu hiệu không nhất quán. Các nội dung mang tính lập luận như cấu trúc pháp lý, quyền ưu tiên, khoảng cách giữa khả năng kỹ thuật và hiệu lực pháp lý vẫn phải được sinh viên khai báo và chịu trách nhiệm giải thích.

Bộ kiểm tra này không tự thay đổi kết luận của Case trước. Nếu sinh viên thay đổi thiết kế để giải quyết một lỗi liên kết, thay đổi phải được ghi trong Nhật ký thay đổi thiết kế theo nguyên tắc bắt buộc của đề.
""")
