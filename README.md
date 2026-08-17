# Blockchain Finance Case Study

Ứng dụng Streamlit hỗ trợ sinh viên thực hiện chuỗi Case Study Blockchain trong Tài chính và Ngân hàng.

## Phiên bản 0.4

Đã có:

- Cá nhân hóa D1, D2, D3, D4 và các thông số tài chính.
- Case 01: As-is Process, đánh giá Blockchain, kiến trúc mạng, quyền, dữ liệu On-chain/Off-chain, đồng thuận, quản trị và Risk Register.
- Case 02: hồ sơ tín dụng, DSCR, LTV, Oracle, ba kịch bản, sự kiện và mô phỏng hợp đồng thông minh.
- Case 03: dữ liệu chuyển tiếp từ Case 02, công cụ huy động vốn theo D1, hồ sơ phát hành, Term Sheet, quy mô token, vòng đời token, pseudocode hợp đồng thông minh, lợi ích nhà đầu tư, ba kịch bản, bảo vệ nhà đầu tư, Risk Register và khuyến nghị đầu tư.
- SQLite lưu hồ sơ dự án và hỗ trợ lưu Case 01, Case 02, Case 03.

## Chạy ứng dụng

```bash
pip install -r requirements.txt
streamlit run app.py
```

Trên Streamlit Community Cloud, file `app.py` là ứng dụng chính. Case 03 được triển khai dưới dạng trang `pages/03_Case_03.py`.

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
requirements.txt
```

## Nguyên tắc dữ liệu

Case 03 lấy External Capital, DSCR, LTV và công cụ huy động vốn từ hồ sơ đã cá nhân hóa và Case 02. Sinh viên không nhập lại phần vốn cần huy động.

Các giả định về giá phát hành, số token, lợi suất phân phối, thời hạn, mức đầu tư tối thiểu và cơ chế mua lại là các tham số thiết kế của sinh viên, phải được giải thích trong Term Sheet.

SQLite hiện phục vụ mục tiêu học tập và thử nghiệm. Đây chưa phải kiến trúc lưu trữ phù hợp cho triển khai chính thức với dữ liệu của cả lớp.

## Nguồn yêu cầu Case 03

Ứng dụng bám các đầu ra của tài liệu: báo cáo Case 03, bảng so sánh phương án huy động vốn, Term Sheet, vòng đời token, pseudocode hợp đồng thông minh, bảng tính lợi ích nhà đầu tư, ba kịch bản, Risk Register và khuyến nghị đầu tư.

## Lộ trình

- Phiên bản 0.4: hoàn thiện Case 03.
- Phiên bản 0.5: kiểm tra tính nhất quán giữa ba Case.
- Phiên bản 0.6: sơ đồ tự động và Change Log.
- Phiên bản 1.0: xuất báo cáo và giao diện giảng viên.
