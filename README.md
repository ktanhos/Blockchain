# Blockchain Finance Case Study

Ứng dụng Streamlit hỗ trợ sinh viên và chuyên viên tư vấn mô phỏng chuỗi Case Study Blockchain trong Tài chính và Ngân hàng theo cấu trúc của Instruction File.

## Phiên bản 2.1

Đã có:

- Cá nhân hóa D1, D2, D3, D4 và các thông số tài chính.
- Case 01: As-is Process, đánh giá Blockchain, kiến trúc mạng, quyền, dữ liệu On-chain và Off-chain, đồng thuận, quản trị và Risk Register.
- Case 02: hồ sơ tín dụng, DSCR, LTV, Oracle, ba kịch bản, sự kiện và mô phỏng hợp đồng thông minh.
- Case 03 nâng cao: dữ liệu chuyển tiếp từ Case 02, công cụ huy động vốn theo D1, Term Sheet, Token Economics, quy mô phát hành, vòng đời token, pseudocode hợp đồng thông minh, lợi ích nhà đầu tư, NPV, IRR, ba kịch bản, bảo vệ nhà đầu tư, Risk Register và khuyến nghị.
- Consistency Checker kiểm tra chuỗi liên kết Case 01 → Case 02 → Case 03 và không nới lỏng lỗi chỉ để đạt trạng thái Đạt.
- Report Builder theo cấu trúc báo cáo tổng hợp của Instruction File.
- Bộ xuất Word nâng cao xây dựng bảng Word thật thay vì chuyển Markdown sang Word.
- Bảng có nhiều cột được chuyển sang trang ngang để tránh chữ bị ép vào các cột quá hẹp.
- Nội dung trong ô bảng không thụt đầu dòng; căn lề, khoảng cách dòng và lề ô được kiểm soát riêng với nội dung thân bài.
- Định dạng báo cáo A4, Times New Roman, Heading thật, đánh số trang và khoảng cách đoạn chuẩn.
- Mục lục, danh mục bảng và danh mục hình bằng trường Word có thể cập nhật tự động.
- Caption tự động cho bảng và hình.
- Sơ đồ As-is và To-be được trình bày dạng luồng nhiều hàng thay vì ép toàn bộ bước trên một dòng.
- Sơ đồ kiến trúc Blockchain được thiết kế lại theo mô hình sổ cái liên minh, các thành viên và lớp dữ liệu.
- Sơ đồ vòng đời token, Integrated Risk Heat Map và lộ trình triển khai được tạo tự động từ dữ liệu Case.
- Report Builder hiển thị toàn bộ sơ đồ trước khi xuất Word.
- Người dùng có thể tải từng sơ đồ PNG trực tiếp từ Report Builder để sử dụng thủ công nếu Word gặp lỗi hiển thị.
- Quality Gate trước khi xuất báo cáo: kiểm tra dữ liệu, nội dung, liên kết Case, số liệu tài chính, lợi ích nhà đầu tư, KPI, Risk Register và quy mô báo cáo.
- Cho phép tạo bản nháp Word khi còn lỗi và chỉ bật báo cáo sẵn sàng nộp khi không còn lỗi cứng.
- SQLite lưu hồ sơ dự án và dữ liệu Case 01, Case 02, Case 03.

## Chạy ứng dụng

```bash
pip install -r requirements.txt
streamlit run app.py
```

Trên Streamlit Community Cloud, chọn repository `ktanhos/Blockchain`, nhánh `main` và file `app.py`.

## Cấu trúc chính

```text
app.py
database.py
requirements.txt
services/
  personalization.py
  financial.py
  case01.py
  case01_ui.py
  case02.py
  case02_ui.py
  case03.py
  case03_ui.py
  consistency.py
  instruction_engine.py
  report_builder.py
  report_quality.py
  report_ui.py
  report_docx.py
  report_docx_enhanced.py
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
    ↓
Report Quality Gate
    ↓
Report Builder
    ↓
Xem trước sơ đồ
    ↓
Word báo cáo
```

Case 03 không cho nhập lại phần vốn cần huy động. Quy mô phát hành được tính từ External Capital và giá phát hành. Các tham số thiết kế như giá token, lợi suất, thời hạn và mức đầu tư tối thiểu phải được giải thích trong Term Sheet.

Report Builder không thay đổi kết luận của Case để làm báo cáo đạt. Nếu dữ liệu chưa nhất quán, Quality Gate sẽ hiển thị lỗi và bản nháp vẫn có thể được xuất để kiểm tra bố cục.

Báo cáo mục tiêu khoảng 30 đến 40 trang nội dung chính, không tính phụ lục. Con số trang là ước tính vì phụ thuộc lượng phân tích sinh viên, độ dài bảng và cách Word phân trang.

SQLite hiện phục vụ mục tiêu học tập và thử nghiệm. Đây chưa phải kiến trúc lưu trữ phù hợp cho triển khai chính thức với dữ liệu của cả lớp.

## Lưu ý

Ứng dụng hiện là mô phỏng học thuật. Hợp đồng thông minh, Oracle, token và giao dịch đều là mô hình mô phỏng, chưa triển khai tài sản thật hoặc mạng Blockchain thật.
