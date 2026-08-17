# Blockchain Finance Case Study

Ứng dụng Streamlit hỗ trợ sinh viên thực hiện chuỗi Case Study Blockchain trong Tài chính và Ngân hàng.

## Phiên bản 0.1

Đã có:

- Nhập mã số sinh viên và tự xác định D1, D2, D3, D4.
- Tự xác định ngành, loại hình doanh nghiệp, vấn đề ngân hàng và công cụ huy động vốn.
- Tự tính các thông số tài chính cá nhân hóa.
- Dashboard tài chính cho Case 02.

## Chạy ứng dụng

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cấu trúc

```text
app.py
services/
  personalization.py
  financial.py
requirements.txt
```

Các bước tiếp theo sẽ bổ sung Case 01, mô phỏng hợp đồng thông minh, Oracle, Case 03, Risk Register, kiểm tra tính nhất quán và xuất báo cáo.
