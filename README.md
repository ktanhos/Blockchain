# Blockchain Finance Case Study

Ứng dụng Streamlit hỗ trợ sinh viên thực hiện chuỗi Case Study Blockchain trong Tài chính và Ngân hàng.

## Phiên bản 1.0

Đã có:

- Cá nhân hóa D1, D2, D3, D4 và các thông số tài chính.
- Case 01: As-is Process, đánh giá Blockchain, kiến trúc mạng, quyền, dữ liệu On-chain và Off-chain, đồng thuận, quản trị và Risk Register.
- Case 02: hồ sơ tín dụng, DSCR, LTV, Oracle, ba kịch bản, sự kiện và mô phỏng hợp đồng thông minh.
- Case 03 nâng cao: dữ liệu chuyển tiếp từ Case 02, công cụ huy động vốn theo D1, Term Sheet, Token Economics, quy mô phát hành, vòng đời token, pseudocode hợp đồng thông minh, lợi ích nhà đầu tư, NPV, IRR, ba kịch bản, bảo vệ nhà đầu tư, Risk Register và khuyến nghị.
- Kiểm tra tính nhất quán giữa Case 01, Case 02 và Case 03.
- SQLite lưu hồ sơ dự án và dữ liệu Case 01, Case 02, Case 03.

## Chạy ứng dụng

```bash
pip install -r requirements.txt
streamlit run app.py
```

Trên Streamlit Community Cloud, chọn repository `ktanhos/Blockchain`, nhánh `main` và file `app.py`.

## Cấu trúc

```text
app.py
database.py
pages/
  03_Case_03.py
services/
  personalization.py
  financial.py
  case01.py
  case02.py
  case02_ui.py
  case03.py
  case03_ui.py
  consistency.py
requirements.txt
```

## Luồng dữ liệu

```text
Mã sinh viên
    ↓
Hồ sơ cá nhân hóa
    ↓
Case 01
    ↓
Case 02
    ↓
External Capital
    ↓
Case 03
    ↓
Consistency Checker
```

Case 03 không cho nhập lại phần vốn cần huy động. Quy mô phát hành được tính từ External Capital và giá phát hành. Các tham số thiết kế như giá token, lợi suất, thời hạn và mức đầu tư tối thiểu phải được giải thích trong Term Sheet.

Consistency Checker kiểm tra các liên kết cốt lõi như tổng nhu cầu vốn, khoản vay, External Capital, DSCR, LTV, công cụ huy động vốn, quy mô phát hành, mã token, vòng đời token, rủi ro và thời hạn.

SQLite hiện phục vụ mục tiêu học tập và thử nghiệm. Đây chưa phải kiến trúc lưu trữ phù hợp cho triển khai chính thức với dữ liệu của cả lớp.

## Lưu ý

Ứng dụng hiện là mô phỏng học thuật. Hợp đồng thông minh, Oracle, token và giao dịch đều là mô hình mô phỏng, chưa triển khai tài sản thật hoặc mạng Blockchain thật.
