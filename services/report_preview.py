"""Preview images used by Report Builder.

Kept separate from the Word exporter so Streamlit can always import the
preview layer independently and show the same diagram sources before export.
"""
from services.report_docx_enhanced import (
    architecture_figure,
    flow_figure,
    heatmap_figure,
    roadmap_figure,
)


def preview_figures(case01, case02, case03):
    return {
        "As-is Process": flow_figure(
            "As-is Process",
            [x.get("Hành động", "") for x in case01.get("as_is", [])],
        ),
        "Kiến trúc Blockchain liên minh": architecture_figure(case01),
        "To-be Process": flow_figure(
            "To-be Process",
            [x.get("Hành động", "") for x in case02.get("to_be", [])],
        ),
        "Vòng đời token": flow_figure(
            "Vòng đời token",
            [x.get("Giai đoạn", "") for x in case03.get("lifecycle", [])],
        ),
        "Integrated Risk Heat Map": heatmap_figure(case01, case02, case03),
        "Lộ trình triển khai": roadmap_figure(),
    }
