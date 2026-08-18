"""Lớp xuất Word dùng bộ dựng sơ đồ thẩm mỹ mới.

Giữ nguyên bộ xuất Word hiện tại để giảm rủi ro thay đổi logic nội dung.
Sau khi Word được tạo, chỉ thay thế sáu ảnh sơ đồ bằng ảnh từ
services.diagram_styles. Vì vậy dữ liệu, bảng, mục lục và cấu trúc báo cáo
không bị thay đổi.
"""
from __future__ import annotations

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from services.report_docx_enhanced import build_docx as _legacy_build_docx
from services.diagram_styles import (
    architecture_figure,
    flow_figure,
    heatmap_figure,
    roadmap_figure,
)


def _diagram_images(case01, case02, case03):
    return [
        flow_figure(
            "Quy trình As-is",
            [x.get("Hành động", "") for x in case01.get("as_is", [])],
        ).getvalue(),
        architecture_figure(case01).getvalue(),
        flow_figure(
            "Quy trình To-be",
            [x.get("Hành động", "") for x in case02.get("to_be", [])],
        ).getvalue(),
        flow_figure(
            "Vòng đời token",
            [x.get("Giai đoạn", "") for x in case03.get("lifecycle", [])],
        ).getvalue(),
        heatmap_figure(case01, case02, case03).getvalue(),
        roadmap_figure().getvalue(),
    ]


def _replace_diagram_images(docx_bytes, images):
    """Thay các ảnh PNG được chèn tuần tự bởi bộ xuất Word hiện tại.

    build_docx hiện tại chèn đúng sáu sơ đồ theo thứ tự:
    As-is, kiến trúc, To-be, vòng đời token, ma trận rủi ro, lộ trình.
    Các ảnh được thay trực tiếp trong gói DOCX nên không ảnh hưởng tới văn
    bản, bảng hoặc trường mục lục.
    """
    source = BytesIO(docx_bytes)
    output = BytesIO()
    with ZipFile(source, "r") as zin, ZipFile(output, "w") as zout:
        media_names = sorted(
            name for name in zin.namelist()
            if name.startswith("word/media/") and name.lower().endswith(".png")
        )
        replacements = min(len(media_names), len(images))
        replacement_map = {
            media_names[i]: images[i] for i in range(replacements)
        }
        for item in zin.infolist():
            data = replacement_map.get(item.filename)
            if data is None:
                data = zin.read(item.filename)
            info = item
            if info.filename in replacement_map:
                info.compress_type = ZIP_DEFLATED
            zout.writestr(info, data)
    return output.getvalue()


def build_docx(profile, financials, case01, case02, case03, report, consistency_results, quality_checks=None):
    legacy = _legacy_build_docx(
        profile, financials, case01, case02, case03,
        report, consistency_results, quality_checks,
    )
    return _replace_diagram_images(legacy, _diagram_images(case01, case02, case03))


__all__ = ["build_docx"]
