"""Preview images used by Report Builder.

The preview layer uses the same diagram functions that are injected into the
Word exporter, so the user sees the same visual output before export.
"""
from services.diagram_styles import architecture_figure, flow_figure, roadmap_figure
from services.risk_matrix import heatmap_figure


def _patch_word_risk_matrix():
    """Đồng bộ ma trận rủi ro xem trước với hình đưa vào Word."""
    try:
        import services.report_docx_enhanced as renderer
        renderer.heatmap_figure = heatmap_figure
    except Exception:
        # Không làm Report Builder sập chỉ vì bộ xuất Word chưa tải được.
        pass


def preview_figures(case01, case02, case03):
    _patch_word_risk_matrix()
    return {
        "As-is Process": flow_figure(
            "Quy trình As-is",
            [x.get("Hành động", "") for x in case01.get("as_is", [])],
        ),
        "Kiến trúc Blockchain liên minh": architecture_figure(case01),
        "To-be Process": flow_figure(
            "Quy trình To-be",
            [x.get("Hành động", "") for x in case02.get("to_be", [])],
        ),
        "Vòng đời token": flow_figure(
            "Vòng đời token",
            [x.get("Giai đoạn", "") for x in case03.get("lifecycle", [])],
        ),
        "Integrated Risk Heat Map": heatmap_figure(case01, case02, case03),
        "Lộ trình triển khai": roadmap_figure(),
    }
