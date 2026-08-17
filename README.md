# Blockchain Finance Case Study

Ứng dụng Streamlit hỗ trợ sinh viên thực hiện chuỗi Case Study Blockchain trong Tài chính và Ngân hàng.

## Phiên bản 0.2

Đã có:

- Nhập mã số sinh viên và tự xác định D1, D2, D3, D4.
- Tự xác định ngành, loại hình doanh nghiệp, vấn đề ngân hàng và công cụ huy động vốn.
- Tự tính các thông số tài chính cá nhân hóa.
- Case 01: As-is Process tối thiểu 8 bước.
- Case 01: đánh giá cơ sở dữ liệu tập trung so với Blockchain/DLT theo các tiêu chí của tài liệu.
- Case 01: lựa chọn mô hình Blockchain, thành viên mạng, nút xác thực và cơ chế đồng thuận.
- Case 01: ma trận quyền đọc, ghi, xác thực, quản trị và tạm dừng.
- Case 01: phân loại dữ liệu On-chain và Off-chain.
- Case 01: thiết kế các nội dung quản trị mạng.
- Case 01: Risk Register với Risk Score = Probability × Impact.
- Checklist kiểm tra điều kiện hoàn thành Case 01.
- SQLite lưu hồ sơ sinh viên và toàn bộ dữ liệu Case 01 để Case 02 có thể sử dụng lại.

## Chạy ứng dụng

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cấu trúc

```text
app.py
database.py
services/
  personalization.py
  financial.py
  case01.py
requirements.txt
```

## Nguyên tắc dữ liệu

Dữ liệu cá nhân hóa được tính từ mã số sinh viên theo quy tắc của tài liệu case study. Case 02 và Case 03 sẽ sử dụng dữ liệu đã lưu từ Case trước thay vì yêu cầu sinh viên nhập lại.

SQLite chỉ là lớp lưu trữ của ứng dụng học tập. Phiên bản hiện tại chưa triển khai mạng Blockchain thật, ví thật hoặc giao dịch tài sản thật.

## Lộ trình

- Phiên bản 0.3: Case 02, sản phẩm tín dụng, To-be Process, máy tính DSCR/LTV, mô phỏng hợp đồng thông minh, Oracle và ba kịch bản.
- Phiên bản 0.4: Case 03, Term Sheet, token, lợi ích nhà đầu tư và ba kịch bản đầu tư.
- Phiên bản 1.0: kiểm tra tính nhất quán giữa ba Case, sơ đồ tự động, xuất báo cáo và hỗ trợ giảng viên.
