import streamlit as st
import pandas as pd

from database import load_project, save_project
from services.personalization import build_case_profile
from services.financial import calculate_financials
from services.case03 import default_case03
from services.case03_ui import render_case03

st.set_page_config(page_title="Case 03 · Token", page_icon="🪙", layout="wide")

st.title("Case 03 · Huy động vốn và đầu tư bằng token")
st.caption("Dữ liệu được kế thừa từ hồ sơ cá nhân và Case 02")

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
if not existing:
    st.warning("Chưa có hồ sơ dự án. Hãy hoàn thành và lưu Case 01 trước khi thực hiện Case 03.")
    st.stop()

financials = calculate_financials(profile)
if "case03" not in st.session_state or st.session_state.get("case03_project_id") != project_id:
    saved = existing.get("case03") or {}
    st.session_state.case03 = saved if saved else default_case03(profile, financials)
    st.session_state.case03_project_id = project_id

case03 = render_case03(st, profile, financials)

st.divider()
st.subheader("Kiểm tra dữ liệu chuyển tiếp")
checks = {
    "Tổng nhu cầu vốn giữ nguyên": abs(financials["V"] - calculate_financials(profile)["V"]) < 1e-9,
    "Khoản vay lấy từ hồ sơ tín dụng": financials["LoanAmount"] > 0,
    "Vốn còn thiếu bằng External Capital": financials["ExternalCapital"] > 0,
    "Công cụ huy động đúng theo D1": case03["instrument"] == profile["funding_instrument"],
    "Case 03 không nhập lại vốn cần huy động": True,
}
st.dataframe(pd.DataFrame({"Kiểm tra": list(checks.keys()), "Trạng thái": ["Đạt" if x else "Chưa đạt" for x in checks.values()]}), use_container_width=True, hide_index=True)

if st.button("Lưu Case 03", type="primary", use_container_width=True):
    save_project(project_id, student_id, profile, existing.get("case01", {}), existing.get("case02", {}), case03)
    st.success("Đã lưu Case 03 vào SQLite.")
