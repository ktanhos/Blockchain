import streamlit as st

from services.personalization import build_case_profile
from services.financial import calculate_financials

st.set_page_config(page_title="Blockchain Finance Case Study", page_icon="⛓️", layout="wide")

st.title("Blockchain trong Tài chính và Ngân hàng")
st.caption("Phiên bản 0.1 · Hồ sơ cá nhân hóa và máy tính tài chính")

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

st.subheader("Hồ sơ case cá nhân")
col1, col2, col3, col4 = st.columns(4)
col1.metric("D1", profile["D1"])
col2.metric("D2", profile["D2"])
col3.metric("D3", profile["D3"])
col4.metric("D4", profile["D4"])

st.dataframe(
    {
        "Thông số": [
            "Ngành hoạt động",
            "Loại hình doanh nghiệp",
            "Vấn đề ngân hàng trọng tâm",
            "Công cụ huy động vốn Case 03",
        ],
        "Giá trị": [
            profile["industry"],
            profile["business_type"],
            profile["banking_problem"],
            profile["funding_instrument"],
        ],
    },
    use_container_width=True,
    hide_index=True,
)

st.subheader("Thông số tài chính cá nhân hóa")
financials = calculate_financials(profile)

f1, f2, f3, f4 = st.columns(4)
f1.metric("Tổng nhu cầu vốn", f"{financials['V']:.2f} tỷ đồng")
f2.metric("Tỷ lệ vốn vay", f"{financials['LoanRatio'] * 100:.2f}%")
f3.metric("Khoản vay", f"{financials['LoanAmount']:.2f} tỷ đồng")
f4.metric("Vốn còn thiếu", f"{financials['ExternalCapital']:.2f} tỷ đồng")

f5, f6, f7, f8 = st.columns(4)
f5.metric("Thời hạn", f"{financials['T']} năm")
f6.metric("Lãi suất", f"{financials['r'] * 100:.2f}%")
f7.metric("Tài sản bảo đảm", f"{financials['CollateralValue']:.2f} tỷ đồng")
f8.metric("DSCR", f"{financials['DSCR']:.2f}x")

st.subheader("Chi tiết tính toán Case 02")
rows = [
    ("Tổng nhu cầu vốn", financials["V"]),
    ("Tỷ lệ vốn vay", financials["LoanRatio"] * 100),
    ("Khoản vay ngân hàng", financials["LoanAmount"]),
    ("Vốn còn thiếu", financials["ExternalCapital"]),
    ("Tiền lãi năm đầu", financials["Interest"]),
    ("Doanh thu năm đầu", financials["Revenue1"]),
    ("Biên EBITDA", financials["EbitdaMargin"] * 100),
    ("EBITDA năm đầu", financials["EBITDA1"]),
    ("Gốc phải trả năm đầu", financials["PrincipalPayment"]),
    ("Nghĩa vụ trả nợ năm đầu", financials["DebtService1"]),
    ("DSCR", financials["DSCR"]),
    ("Giá trị tài sản bảo đảm", financials["CollateralValue"]),
    ("LTV", financials["LTV"] * 100),
    ("Dòng tiền còn lại sau trả nợ", financials["ResidualCash"]),
]

st.dataframe(
    {"Chỉ tiêu": [x[0] for x in rows], "Giá trị": [round(x[1], 4) for x in rows]},
    use_container_width=True,
    hide_index=True,
)

st.success("Phiên bản 0.1 đã hoàn thành phần cá nhân hóa và tính toán tài chính cốt lõi.")
