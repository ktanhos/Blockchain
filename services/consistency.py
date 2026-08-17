def check_consistency(profile, financials, case01, case03):
    checks = []

    def add(name, ok, detail):
        checks.append({"Hạng mục": name, "Trạng thái": "Đạt" if ok else "Lỗi", "Chi tiết": detail})

    add("Hồ sơ cá nhân hóa", all(k in profile for k in ["D1", "D2", "D3", "D4"]), "D1 đến D4 tồn tại")
    add("Case 01 có tối thiểu 8 bước", len(case01.get("as_is", [])) >= 8, f"Hiện có {len(case01.get('as_is', []))} bước")
    add("Case 01 có 12 tiêu chí đánh giá", len(case01.get("assessment", [])) >= 12, f"Hiện có {len(case01.get('assessment', []))} tiêu chí")
    add("Case 01 có thành viên mạng", len(case01.get("architecture", {}).get("nodes", [])) >= 1, "Kiểm tra danh sách thành viên")
    add("Case 01 có ít nhất 10 dữ liệu", len(case01.get("data", [])) >= 10, f"Hiện có {len(case01.get('data', []))} dòng")
    add("Case 01 có ít nhất 10 rủi ro", len(case01.get("risks", [])) >= 10, f"Hiện có {len(case01.get('risks', []))} rủi ro")

    invalid_storage = [r.get("Loại dữ liệu", "") for r in case01.get("data", []) if bool(r.get("On-chain")) == bool(r.get("Off-chain"))]
    add("Phân loại On-chain và Off-chain hợp lệ", not invalid_storage, "Không có dữ liệu chọn đồng thời hoặc không chọn vị trí lưu trữ" if not invalid_storage else ", ".join(invalid_storage))

    add("Công cụ Case 03 đúng cá nhân hóa", case03.get("instrument") == profile.get("funding_instrument"), f"Case 03: {case03.get('instrument')} | Hồ sơ: {profile.get('funding_instrument')}")
    external = float(financials.get("ExternalCapital", 0))
    issue = float(case03.get("issue_price", 0))
    token_count = int(case03.get("_token_count", 0))
    if token_count <= 0 and issue > 0:
        import math
        token_count = math.ceil(external * 1e9 / issue)
    actual_raise = token_count * issue
    tolerance = issue if issue > 0 else 0
    add("Case 03 huy động từ External Capital", abs(actual_raise - external * 1e9) <= tolerance, f"External Capital = {external:.2f} tỷ; giá trị phát hành = {actual_raise/1e9:.2f} tỷ")
    add("Mã token tối đa 6 ký tự", 1 <= len(str(case03.get("token_code", ""))) <= 6, f"Mã token: {case03.get('token_code', '')}")
    add("Vòng đời token đủ 12 bước", len(case03.get("lifecycle", [])) >= 12, f"Hiện có {len(case03.get('lifecycle', []))} bước")
    add("Case 03 có ít nhất 14 rủi ro", len(case03.get("risks", [])) >= 14, f"Hiện có {len(case03.get('risks', []))} rủi ro")
    add("Thời hạn Case 03 phù hợp khoản vay", int(case03.get("term_years", 0)) == int(financials.get("T", -1)), f"Case 03 = {case03.get('term_years')} năm; Case 02 = {financials.get('T')} năm")
    add("Lợi suất Case 03 có giá trị", float(case03.get("annual_return_rate", 0)) >= 0, "Kiểm tra tỷ lệ phân phối")

    architecture = case01.get("architecture", {})
    add("Case 01 có quyết định Blockchain", architecture.get("decision") in ["Go", "No-Go", "Hybrid"], f"Quyết định: {architecture.get('decision')}")
    add("Case 01 có cơ chế đồng thuận", bool(str(architecture.get("consensus", "")).strip()), "Kiểm tra consensus")

    return checks
