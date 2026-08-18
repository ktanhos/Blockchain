import json
import copy
import streamlit as st
import pandas as pd

from database import load_project, save_project
from services.personalization import build_case_profile
from services.financial import calculate_financials
from services.case01 import default_case01
from services.case01_ui import render_case01
from services.case02 import default_case02
from services.case02_ui import render_case02
from services.case03 import default_case03
from services.case03_ui import render_case03
from services.consistency import check_consistency
from services.instruction_engine import validate_case01, validate_case02, validate_case03
from services.report_pdf import build_integrated_report

st.set_page_config(page_title="Blockchain Finance Case Study", page_icon="⛓️", layout="wide")
st.title("Blockchain trong Tài chính và Ngân hàng")
st.caption("Case 01 → Case 02 → Case 03 → Consistency Checker → Báo cáo")

st.sidebar.header("Hồ sơ sinh viên")
student_id = st.sidebar.text_input("Mã số sinh viên", key="global_student_id")
if not student_id:
    st.info("Nhập mã số sinh viên ở thanh bên để bắt đầu.")
    st.stop()

digits = "".join(ch for ch in student_id if ch.isdigit())
if len(digits) < 4:
    st.error("Mã số sinh viên phải có ít nhất 4 chữ số.")
    st.stop()
project_id = f"student_{digits}"
existing = load_project(project_id) or {}

if existing.get("profile", {}).get("business_description") and "business_description" not in st.session_state:
    st.session_state.business_description = existing["profile"]["business_description"]
try:
    profile = build_case_profile(student_id)
except ValueError as exc:
    st.error(str(exc))
    st.stop()
profile["student_id"] = student_id
if existing.get("profile", {}).get("business_description") and not profile.get("business_description"):
    profile["business_description"] = existing["profile"]["business_description"]
    st.session_state.business_description = profile["business_description"]

financials = calculate_financials(profile)

def merge_defaults(template, saved):
    result = copy.deepcopy(template)
    if saved:
        result.update(copy.deepcopy(saved))
    return result

if st.session_state.get("project_id") != project_id:
    st.session_state.project_id = project_id
    st.session_state.case01 = copy.deepcopy(existing.get("case01") or default_case01())
    st.session_state.case02 = merge_defaults(default_case02(financials, st.session_state.case01), existing.get("case02"))
    st.session_state.case03 = merge_defaults(default_case03(profile, financials), existing.get("case03"))
else:
    st.session_state.setdefault("case01", copy.deepcopy(existing.get("case01") or default_case01()))
    st.session_state.setdefault("case02", merge_defaults(default_case02(financials, st.session_state.case01), existing.get("case02")))
    st.session_state.setdefault("case03", merge_defaults(default_case03(profile, financials), existing.get("case03")))

case01 = st.session_state.case01
case02 = st.session_state.case02
case03 = st.session_state.case03
case01.setdefault("permissions", []); case01.setdefault("data", []); case01.setdefault("assessment", []); case01.setdefault("risks", []); case01.setdefault("architecture", {}); case01.setdefault("governance", {})
case02.setdefault("oracle", []); case02.setdefault("risks", [])
case03.setdefault("risks", [])


def save_all():
    save_project(project_id, student_id, profile, st.session_state.case01, st.session_state.case02, st.session_state.case03)

st.sidebar.success("Hồ sơ đã được cá nhân hóa")
if st.sidebar.button("Lưu toàn bộ", type="primary", key="save_all_button"):
    save_all()
    st.sidebar.success("Đã lưu toàn bộ dữ liệu dự án")

st.subheader("Hồ sơ case cá nhân")
cols = st.columns(4)
for col, key in zip(cols, ["D1", "D2", "D3", "D4"]):
    col.metric(key, profile[key])
profile_df = pd.DataFrame({"Thông số": ["Ngành hoạt động", "Loại hình doanh nghiệp", "Vấn đề ngân hàng trọng tâm", "Công cụ huy động vốn Case 03"], "Giá trị": [profile["industry"], profile["business_type"], profile["banking_problem"], profile["funding_instrument"]]})
st.dataframe(profile_df, width="stretch", hide_index=True)
if profile.get("business_description"):
    with st.expander("Mô tả hoạt động doanh nghiệp", expanded=True):
        st.write(profile["business_description"])
st.divider()

case01_tab, case02_tab, case03_tab, check_tab, report_tab = st.tabs(["Case 01 · Kiến trúc Blockchain", "Case 02 · Tín dụng Blockchain", "Case 03 · Huy động vốn bằng token", "Kiểm tra tính nhất quán", "Báo cáo"])

with case01_tab:
    st.session_state.case01 = render_case01(st, st.session_state.case01)

with case02_tab:
    st.session_state.case02 = render_case02(st, financials, st.session_state.case01)

with case03_tab:
    st.session_state.case03 = render_case03(st, profile, financials, st.session_state.case02, save_callback=lambda data: save_project(project_id, student_id, profile, st.session_state.case01, st.session_state.case02, data))

with check_tab:
    st.header("Consistency Checker · Kiểm tra liên kết ba Case")
    st.caption("Kiểm tra 22 yêu cầu liên kết. Lỗi chỉ được chuyển thành Đạt khi dữ liệu thực sự tồn tại và nhất quán.")
    results = check_consistency(profile, financials, st.session_state.case01, st.session_state.case02, st.session_state.case03)
    result_df = pd.DataFrame(results)
    st.dataframe(result_df, width="stretch", hide_index=True)
    errors = sum(x["Trạng thái"] == "Lỗi" for x in results)
    c1, c2 = st.columns(2)
    c1.metric("Tổng kiểm tra", len(results)); c2.metric("Số lỗi", errors)
    if errors == 0: st.success("Không phát hiện lỗi trong 22 kiểm tra.")
    else: st.error(f"Phát hiện {errors} điểm cần xử lý.")
    if st.button("Lưu kết quả kiểm tra", key="save_consistency"):
        st.session_state.consistency = results; save_all(); st.success("Đã lưu trạng thái dự án.")

with report_tab:
    st.header("Báo cáo tổng hợp")
    results = check_consistency(profile, financials, st.session_state.case01, st.session_state.case02, st.session_state.case03)
    case01_status = validate_case01(st.session_state.case01); case02_status = validate_case02(st.session_state.case02); case03_status = validate_case03(st.session_state.case03)
    completed = sum(case01_status.values()) + sum(case02_status.values()) + sum(case03_status.values()); total = len(case01_status) + len(case02_status) + len(case03_status); errors = sum(x["Trạng thái"] == "Lỗi" for x in results)
    m1, m2, m3 = st.columns(3); m1.metric("Mức độ hoàn thiện theo Instruction", f"{completed / total * 100:.0f}%" if total else "0%"); m2.metric("Kiểm tra liên kết", f"{len(results) - errors}/{len(results)}"); m3.metric("Điểm cần xử lý", errors)
    status_df = pd.DataFrame([{ "Case": "Case 01", "Đạt yêu cầu": sum(case01_status.values()), "Tổng yêu cầu": len(case01_status), "Tỷ lệ": f"{sum(case01_status.values()) / len(case01_status) * 100:.0f}%"}, {"Case": "Case 02", "Đạt yêu cầu": sum(case02_status.values()), "Tổng yêu cầu": len(case02_status), "Tỷ lệ": f"{sum(case02_status.values()) / len(case02_status) * 100:.0f}%"}, {"Case": "Case 03", "Đạt yêu cầu": sum(case03_status.values()), "Tổng yêu cầu": len(case03_status), "Tỷ lệ": f"{sum(case03_status.values()) / len(case03_status) * 100:.0f}%"}])
    st.dataframe(status_df, width="stretch", hide_index=True)
    if errors: st.dataframe(pd.DataFrame(results).query("Trạng thái == 'Lỗi'"), width="stretch", hide_index=True)
    else: st.success("Không còn điểm lỗi trong bộ kiểm tra liên kết.")
    st.subheader("Xem nhanh")
    p1, p2, p3 = st.columns(3); p1.write(f"Doanh nghiệp: {profile.get('business_type', '')}"); p1.write(f"Ngành: {profile.get('industry', '')}"); p2.write(f"Tổng nhu cầu vốn: {financials.get('V', 0):,.2f} tỷ đồng"); p2.write(f"Khoản vay: {financials.get('LoanAmount', 0):,.2f} tỷ đồng"); p3.write(f"Vốn còn thiếu: {financials.get('ExternalCapital', 0):,.2f} tỷ đồng"); p3.write(f"Blockchain: {st.session_state.case01.get('architecture', {}).get('blockchain_type', '')}")
    st.info("Bản báo cáo được tổng hợp từ dữ liệu Case 01, Case 02 và Case 03. Sinh viên vẫn phải hoàn thiện phần phân tích, trích dẫn và trình bày theo Instruction File.")
    report_bytes = build_integrated_report(profile, financials, st.session_state.case01, st.session_state.case02, st.session_state.case03, results)
    st.download_button("Xuất báo cáo", data=report_bytes, file_name=f"Bao_cao_Blockchain_{digits}.pdf", mime="application/pdf", width="stretch")
    project_json = {"student_id": student_id, "profile": profile, "financials": financials, "case01": st.session_state.case01, "case02": st.session_state.case02, "case03": st.session_state.case03, "consistency": results}
    st.download_button("Xuất toàn bộ dữ liệu dự án JSON", data=json.dumps(project_json, ensure_ascii=False, indent=2, default=str), file_name=f"Blockchain_Project_{digits}.json", mime="application/json", width="stretch")

# Tự động lưu sau mỗi lần rerun. Nhờ đó thao tác nhập liệu được giữ ngay cả khi chuyển tab hoặc làm mới nhẹ trong cùng dự án.
save_all()
st.caption("Đã đồng bộ dữ liệu dự án.")
