"""Bộ dựng sơ đồ dùng chung cho Report Builder.

Nguyên tắc thiết kế:
1. Sơ đồ chỉ minh họa cấu trúc hoặc quan hệ chính.
2. Không nhồi toàn bộ dữ liệu chi tiết vào hình.
3. Chi tiết dài phải nằm trong bảng hoặc phần nhận xét của báo cáo.
4. Hình phải đọc được khi đặt trên trang A4.
5. Preview trên Streamlit và hình chèn vào Word dùng cùng một bộ dựng.

Không thay đổi dữ liệu đầu vào của Case.
"""
from __future__ import annotations

from collections import defaultdict
from io import BytesIO
import math
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

FONT_NAME = "DejaVu Sans"
NAVY = "#17324D"
BLUE = "#2F6B9A"
TEAL = "#2A8C82"
SLATE = "#667085"
DARK = "#263442"
GRID = "#D9E1E8"
LIGHT = "#F4F7FA"
LIGHT_BLUE = "#EAF2F8"
LIGHT_TEAL = "#EEF6F4"
WHITE = "#FFFFFF"
RISK_LOW = "#E4F1EE"
RISK_MEDIUM = "#F8EDC5"
RISK_HIGH = "#F5D1CE"
RISK_CRITICAL = "#D99595"


def _new_figure(width=11.2, height=6.2):
    fig = plt.figure(figsize=(width, height), facecolor=WHITE)
    fig.patch.set_facecolor(WHITE)
    return fig


def _header(fig, title, subtitle=None):
    fig.text(0.055, 0.955, str(title), ha="left", va="top", fontsize=16,
             fontweight="bold", color=NAVY)
    if subtitle:
        fig.text(0.055, 0.915, str(subtitle), ha="left", va="top",
                 fontsize=9.2, color=SLATE)


def _save(fig):
    out = BytesIO()
    fig.savefig(out, format="png", dpi=220, bbox_inches="tight",
                facecolor=WHITE, pad_inches=0.12)
    plt.close(fig)
    out.seek(0)
    return out


def _wrapped(text, width=22):
    value = str(text or "").strip()
    if not value:
        return ""
    return "\n".join(textwrap.wrap(value, width=width, break_long_words=False))


def _card(ax, x, y, width, height, text, number=None, fill=LIGHT,
          edge=GRID, fontsize=8.5, wrap_width=20):
    ax.add_patch(FancyBboxPatch(
        (x - width / 2, y - height / 2), width, height,
        boxstyle="round,pad=0.012,rounding_size=0.025",
        facecolor=fill, edgecolor=edge, linewidth=1.15, zorder=3,
    ))
    if number is not None:
        ax.add_patch(Circle(
            (x - width / 2 + 0.035, y), 0.025,
            facecolor=BLUE, edgecolor=WHITE, linewidth=1.0, zorder=5,
        ))
        ax.text(x - width / 2 + 0.035, y, str(number), ha="center",
                va="center", fontsize=7.2, fontweight="bold", color=WHITE,
                zorder=6)
        text_x = x - width / 2 + 0.075
        alignment = "left"
    else:
        text_x = x
        alignment = "center"
    ax.text(text_x, y, _wrapped(text, wrap_width), ha=alignment, va="center",
            fontsize=fontsize, color=DARK, zorder=5)


def _arrow(ax, start, end, color=SLATE, lw=1.15, style="-|>"):
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle=style, color=color, linewidth=lw,
                                shrinkA=0, shrinkB=0,
                                connectionstyle="arc3,rad=0"), zorder=2)


def flow_figure(title, steps):
    """Sơ đồ quy trình tối giản, ưu tiên trình tự đọc thay vì chi tiết."""
    steps = [str(x).strip() for x in (steps or []) if str(x).strip()]
    if not steps:
        steps = ["Chưa có dữ liệu"]

    n = len(steps)
    cols = n if n <= 5 else 4
    rows = math.ceil(n / cols)
    height = 4.6 if rows == 1 else 6.2 if rows == 2 else 7.4

    fig = _new_figure(11.4, height)
    _header(fig, title,
            "Sơ đồ minh họa trình tự xử lý; chi tiết nghiệp vụ nằm trong bảng quy trình.")
    ax = fig.add_axes([0.055, 0.12, 0.89, 0.72])
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.axis("off")

    positions = {}
    for row in range(rows):
        indices = list(range(row * cols, min((row + 1) * cols, n)))
        if row % 2 == 1:
            indices.reverse()
        count = len(indices)
        offset = (cols - count) / 2
        for col, idx in enumerate(indices):
            positions[idx] = (col + 0.5 + offset, rows - row - 0.5)

    card_w = 0.82 if cols >= 4 else 0.78
    card_h = 0.44
    for idx in range(n):
        x, y = positions[idx]
        _card(ax, x, y, card_w, card_h, steps[idx], idx + 1,
              fontsize=8.2 if n > 8 else 8.5,
              wrap_width=18 if n > 8 else 20)

    for idx in range(n - 1):
        x1, y1 = positions[idx]
        x2, y2 = positions[idx + 1]
        if abs(y1 - y2) < 0.05:
            direction = 1 if x2 > x1 else -1
            _arrow(ax,
                   (x1 + card_w / 2 * direction, y1),
                   (x2 - card_w / 2 * direction, y2))
        else:
            # Các hàng được xếp ziczac. Hai bước chuyển hàng nằm cùng cột,
            # vì vậy chỉ cần một mũi tên dọc, không dùng đường chéo.
            _arrow(ax,
                   (x1, y1 - card_h / 2),
                   (x2, y2 + card_h / 2))

    fig.text(0.055, 0.055,
             "Hình dùng để minh họa luồng. Các chủ thể, dữ liệu, hệ thống và thời gian được trình bày trong bảng tương ứng.",
             fontsize=8.3, color=SLATE)
    return _save(fig)


def architecture_figure(case01):
    """Sơ đồ kiến trúc liên minh: minh họa quan hệ, không nhồi quyền và dữ liệu."""
    architecture = case01.get("architecture", {}) or {}
    nodes = architecture.get("nodes", []) or ["FutureBank"]
    nodes = [str(x).strip() for x in nodes if str(x).strip()][:8]

    fig = _new_figure(11.4, 7.0)
    _header(fig, "Kiến trúc Blockchain liên minh",
            "Quan hệ giữa sổ cái dùng chung và các thành viên mạng.")
    ax = fig.add_axes([0.045, 0.12, 0.91, 0.73])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    ax.add_patch(FancyBboxPatch(
        (0.32, 0.69), 0.36, 0.13,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        facecolor=LIGHT_BLUE, edgecolor=BLUE, linewidth=1.7))
    ax.text(0.50, 0.755, "SỔ CÁI LIÊN MINH", ha="center", va="center",
            fontsize=14, fontweight="bold", color=NAVY)
    ax.text(0.50, 0.715,
            architecture.get("blockchain_type", "Blockchain liên minh"),
            ha="center", va="center", fontsize=9.2, color=SLATE)

    positions = [
        (0.13, 0.50), (0.37, 0.50), (0.63, 0.50), (0.87, 0.50),
        (0.13, 0.28), (0.37, 0.28), (0.63, 0.28), (0.87, 0.28),
    ]
    for idx, node in enumerate(nodes):
        x, y = positions[idx]
        ax.plot([0.50, x], [0.69, y + 0.045], color="#AAB7C4",
                linewidth=1.0, zorder=1)
        _card(ax, x, y, 0.19, 0.09, node, fontsize=8.4, wrap_width=16)

    ax.add_patch(FancyBboxPatch(
        (0.07, 0.055), 0.39, 0.10,
        boxstyle="round,pad=0.015,rounding_size=0.018",
        facecolor=LIGHT, edgecolor=GRID, linewidth=1.0))
    ax.add_patch(FancyBboxPatch(
        (0.54, 0.055), 0.39, 0.10,
        boxstyle="round,pad=0.015,rounding_size=0.018",
        facecolor=LIGHT_TEAL, edgecolor="#C7DDD8", linewidth=1.0))
    ax.text(0.265, 0.125, "NGOÀI CHUỖI", ha="center", va="center",
            fontsize=9.3, fontweight="bold", color=SLATE)
    ax.text(0.265, 0.083, "KYC • hồ sơ • chứng từ • báo cáo",
            ha="center", va="center", fontsize=8.2, color=DARK)
    ax.text(0.735, 0.125, "TRÊN CHUỖI", ha="center", va="center",
            fontsize=9.3, fontweight="bold", color=TEAL)
    ax.text(0.735, 0.083, "trạng thái • bằng chứng • mã băm • giao dịch",
            ha="center", va="center", fontsize=8.2, color=DARK)

    fig.text(0.055, 0.025,
             "Chi tiết quyền truy cập và phân loại dữ liệu được trình bày trong các bảng Case 01.",
             fontsize=8.2, color=SLATE)
    return _save(fig)


def _risk_fill(score):
    if score <= 4:
        return RISK_LOW
    if score <= 9:
        return RISK_MEDIUM
    if score <= 15:
        return RISK_HIGH
    return RISK_CRITICAL


def heatmap_figure(case01, case02, case03):
    """Ma trận rủi ro 5x5 chỉ minh họa vị trí rủi ro.

    Tên rủi ro không đặt trong hình. Mỗi điểm có mã số và được giải thích
    bằng Risk Register ngay sau hình trong báo cáo.
    """
    points = []
    for source, rows in (
        ("Case 01", case01.get("risks", [])),
        ("Case 02", case02.get("risks", [])),
        ("Case 03", case03.get("risks", [])),
    ):
        for row in rows:
            try:
                probability = int(row.get("P", 0))
                impact = int(row.get("I", 0))
            except (TypeError, ValueError):
                continue
            if 1 <= probability <= 5 and 1 <= impact <= 5:
                points.append((probability, impact, source))

    fig = _new_figure(9.6, 7.0)
    _header(fig, "Ma trận rủi ro tích hợp",
            "Hình chỉ minh họa phân bố rủi ro; mã số được đối chiếu với Risk Register.")
    ax = fig.add_axes([0.13, 0.24, 0.76, 0.62])
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6)); ax.set_yticks(range(1, 6))
    ax.set_xlabel("Mức độ tác động", labelpad=8, fontsize=10, color=DARK)
    ax.set_ylabel("Xác suất xảy ra", labelpad=8, fontsize=10, color=DARK)
    ax.tick_params(length=0, labelsize=9, colors=SLATE)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for probability in range(1, 6):
        for impact in range(1, 6):
            ax.add_patch(Rectangle(
                (impact - 0.5, probability - 0.5), 1, 1,
                facecolor=_risk_fill(probability * impact),
                edgecolor=WHITE, linewidth=1.7))

    by_cell = defaultdict(list)
    for idx, (probability, impact, source) in enumerate(points, 1):
        by_cell[(probability, impact)].append((idx, source))

    for (probability, impact), cell_points in by_cell.items():
        count = len(cell_points)
        if count == 1:
            offsets = [(0, 0)]
        else:
            radius = 0.18 if count <= 6 else 0.21
            offsets = [(
                radius * math.cos(2 * math.pi * j / count),
                radius * math.sin(2 * math.pi * j / count),
            ) for j in range(count)]
        for (idx, _source), (dx, dy) in zip(cell_points, offsets):
            ax.scatter(impact + dx, probability + dy, s=210,
                       facecolor=NAVY, edgecolor=WHITE, linewidth=1.5, zorder=5)
            ax.text(impact + dx, probability + dy, str(idx), ha="center",
                    va="center", fontsize=7.4, fontweight="bold",
                    color=WHITE, zorder=6)

    labels = [(RISK_LOW, "Thấp"), (RISK_MEDIUM, "Trung bình"),
              (RISK_HIGH, "Cao"), (RISK_CRITICAL, "Rất cao")]
    start_x = 0.18
    for i, (fill, label) in enumerate(labels):
        x = start_x + i * 0.17
        fig.patches.append(Rectangle(
            (x, 0.145), 0.018, 0.018, transform=fig.transFigure,
            facecolor=fill, edgecolor=GRID, linewidth=0.6))
        fig.text(x + 0.024, 0.146, label, fontsize=8.2,
                 color=DARK, va="bottom")

    fig.text(0.18, 0.085,
             "Số trong vòng tròn = mã rủi ro. Chi tiết tên, nguồn, kiểm soát và kế hoạch xử lý nằm trong Risk Register.",
             fontsize=8.4, color=SLATE)
    return _save(fig)


def roadmap_figure():
    """Lộ trình triển khai ba giai đoạn, chỉ giữ thông điệp chính."""
    fig = _new_figure(11.2, 4.5)
    _header(fig, "Lộ trình triển khai", "Ba giai đoạn từ kiểm chứng đến vận hành.")
    ax = fig.add_axes([0.07, 0.19, 0.86, 0.58])
    ax.set_xlim(0, 3); ax.set_ylim(0, 1); ax.axis("off")

    stages = [
        (0.50, "01", "Kiểm chứng kỹ thuật", "Kiến trúc • dữ liệu • kiểm thử"),
        (1.50, "02", "Thử nghiệm giới hạn", "Quy trình • kiểm soát • đánh giá"),
        (2.50, "03", "Triển khai chính thức", "Vận hành • giám sát • mở rộng"),
    ]
    for i, (x, num, name, desc) in enumerate(stages):
        ax.add_patch(FancyBboxPatch(
            (x - 0.35, 0.38), 0.70, 0.32,
            boxstyle="round,pad=0.015,rounding_size=0.025",
            facecolor=LIGHT, edgecolor=GRID, linewidth=1.2))
        ax.text(x, 0.64, num, ha="center", va="center", fontsize=8.5,
                fontweight="bold", color=BLUE)
        ax.text(x, 0.52, name, ha="center", va="center", fontsize=10.3,
                fontweight="bold", color=NAVY)
        ax.text(x, 0.29, desc, ha="center", va="center", fontsize=8.2,
                color=SLATE)
        if i < 2:
            _arrow(ax, (x + 0.37, 0.54), (x + 0.63, 0.54))

    fig.text(0.07, 0.08,
             "Các điều kiện chuyển giai đoạn và tiêu chí nghiệm thu được trình bày trong phần lộ trình của báo cáo.",
             fontsize=8.2, color=SLATE)
    return _save(fig)
