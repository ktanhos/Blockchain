"""Bộ dựng sơ đồ dùng chung cho Report Builder.

Mục tiêu là giữ nguyên dữ liệu đầu vào nhưng cải thiện cấu trúc thị giác:
phân cấp tiêu đề rõ, khoảng trắng hợp lý, nhãn không chồng lấn và bố cục
phù hợp với báo cáo học thuật. Các nguyên tắc tham khảo từ bài viết về
trực quan hóa Python của Phạm Đình Khánh: chọn loại biểu đồ theo mục đích,
đặt tiêu đề và nhãn rõ ràng, dùng điểm đánh dấu khi cần và dùng ma trận màu
cho dữ liệu rủi ro. Không thay đổi dữ liệu Case.
"""
from __future__ import annotations

from collections import defaultdict
from io import BytesIO
import math
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

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


def _new_figure(width=11, height=6):
    fig = plt.figure(figsize=(width, height), facecolor=WHITE)
    fig.patch.set_facecolor(WHITE)
    return fig


def _header(fig, title, subtitle=None):
    fig.text(0.055, 0.955, str(title).upper(), ha="left", va="top",
             fontsize=16.5, fontweight="bold", color=NAVY)
    if subtitle:
        fig.text(0.055, 0.915, str(subtitle), ha="left", va="top",
                 fontsize=9.5, color=SLATE)


def _save(fig):
    out = BytesIO()
    fig.savefig(out, format="png", dpi=190, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    out.seek(0)
    return out


def _wrapped(text, width=25):
    return "\n".join(textwrap.wrap(str(text), width=width, break_long_words=False))


def flow_figure(title, steps):
    """Sơ đồ quy trình dạng thẻ bước, tránh mũi tên chồng lên nội dung."""
    steps = [str(x).strip() for x in (steps or []) if str(x).strip()]
    if not steps:
        steps = ["Chưa có dữ liệu"]

    n = len(steps)
    if n <= 5:
        cols = n
        rows = 1
    else:
        cols = 4
        rows = math.ceil(n / cols)

    fig = _new_figure(12, 4.6 if rows == 1 else 6.4)
    _header(fig, title, "Trình tự xử lý theo dữ liệu Case")
    ax = fig.add_axes([0.055, 0.10, 0.89, 0.72])
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.axis("off")

    positions = {}
    for row in range(rows):
        indices = list(range(row * cols, min((row + 1) * cols, n)))
        # Hàng kế tiếp chạy ngược chiều để tạo luồng ziczac dễ đọc.
        if row % 2 == 1:
            indices = list(reversed(indices))
        for col, idx in enumerate(indices):
            positions[idx] = (col + 0.5, rows - row - 0.5)

    for idx in range(n):
        x, y = positions[idx]
        card_w, card_h = 0.76, 0.42
        ax.add_patch(FancyBboxPatch(
            (x - card_w / 2, y - card_h / 2), card_w, card_h,
            boxstyle="round,pad=0.025,rounding_size=0.06",
            facecolor=LIGHT, edgecolor=GRID, linewidth=1.0,
        ))
        ax.text(
            x - card_w / 2 + 0.07, y, str(idx + 1),
            ha="center", va="center", fontsize=9, fontweight="bold", color=WHITE,
            bbox=dict(boxstyle="circle,pad=0.28", facecolor=BLUE,
                      edgecolor=WHITE, linewidth=1.2),
        )
        ax.text(
            x - card_w / 2 + 0.17, y, _wrapped(steps[idx], 22),
            ha="left", va="center", fontsize=8.6, color=DARK,
        )

    # Nối từng bước bằng mũi tên ngắn nằm ngoài thẻ.
    for idx in range(n - 1):
        x1, y1 = positions[idx]
        x2, y2 = positions[idx + 1]
        if abs(y1 - y2) < 0.1:
            direction = 1 if x2 > x1 else -1
            start = (x1 + 0.39 * direction, y1)
            end = (x2 - 0.39 * direction, y2)
        else:
            direction = 1 if x2 > x1 else -1
            start = (x1 + 0.28 * direction, y1 - 0.21)
            end = (x2 + 0.28 * direction, y2 + 0.21)
        ax.annotate(
            "", xy=end, xytext=start,
            arrowprops=dict(arrowstyle="-|>", color=SLATE, linewidth=1.1,
                            shrinkA=0, shrinkB=0),
        )

    if rows > 1:
        fig.text(0.055, 0.055,
                 "Luồng đọc: từ trái sang phải, sau đó chuyển xuống hàng kế tiếp.",
                 fontsize=8.5, color=SLATE)
    return _save(fig)


def architecture_figure(case01):
    """Kiến trúc dạng hub và spoke, có phân tầng dữ liệu."""
    nodes = case01.get("architecture", {}).get("nodes", []) or ["FutureBank"]
    nodes = [str(x).strip() for x in nodes if str(x).strip()][:8]

    fig = _new_figure(12, 7.0)
    _header(fig, "Kiến trúc Blockchain liên minh",
            "Các bên tham gia, sổ cái dùng chung và phân lớp dữ liệu")
    ax = fig.add_axes([0.04, 0.07, 0.92, 0.80])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    ledger = (0.50, 0.70)
    ax.add_patch(FancyBboxPatch(
        (0.34, 0.63), 0.32, 0.14,
        boxstyle="round,pad=0.02,rounding_size=0.025",
        facecolor=LIGHT_BLUE, edgecolor=BLUE, linewidth=1.6,
    ))
    ax.text(0.50, 0.70, "SỔ CÁI LIÊN MINH\nBlockchain liên minh",
            ha="center", va="center", fontsize=12.5, fontweight="bold", color=NAVY)

    positions = [
        (0.13, 0.48), (0.38, 0.48), (0.62, 0.48), (0.87, 0.48),
        (0.13, 0.28), (0.38, 0.28), (0.62, 0.28), (0.87, 0.28),
    ]
    for idx, node in enumerate(nodes):
        x, y = positions[idx]
        ax.plot([ledger[0], x], [0.63, y + 0.055], color=GRID, linewidth=1.0, zorder=1)
        ax.add_patch(FancyBboxPatch(
            (x - 0.105, y - 0.045), 0.21, 0.09,
            boxstyle="round,pad=0.015,rounding_size=0.018",
            facecolor=WHITE, edgecolor="#AAB7C4", linewidth=1.0, zorder=2,
        ))
        ax.text(x, y, _wrapped(node, 18), ha="center", va="center",
                fontsize=8.6, color=DARK, zorder=3)

    ax.add_patch(Rectangle((0.06, 0.045), 0.40, 0.105,
                           facecolor=LIGHT, edgecolor=GRID, linewidth=1.0))
    ax.add_patch(Rectangle((0.54, 0.045), 0.40, 0.105,
                           facecolor=LIGHT_TEAL, edgecolor="#C7DDD8", linewidth=1.0))
    ax.text(0.26, 0.108, "NGOÀI CHUỖI", ha="center", va="center",
            fontsize=9.2, fontweight="bold", color=SLATE)
    ax.text(0.26, 0.075, "KYC • hồ sơ • chứng từ • báo cáo",
            ha="center", va="center", fontsize=8.6, color=DARK)
    ax.text(0.74, 0.108, "TRÊN CHUỖI", ha="center", va="center",
            fontsize=9.2, fontweight="bold", color=TEAL)
    ax.text(0.74, 0.075, "trạng thái • bằng chứng • mã băm • giao dịch",
            ha="center", va="center", fontsize=8.6, color=DARK)
    return _save(fig)


def heatmap_figure(case01, case02, case03):
    """Ma trận rủi ro 5x5, đánh số điểm để loại bỏ hiện tượng nhãn chồng nhau."""
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
                points.append((probability, impact, str(row.get("Rủi ro", "Rủi ro")), source))

    fig = _new_figure(11.5, 7.6)
    _header(fig, "Ma trận rủi ro tích hợp",
            "Mỗi điểm được đánh số; danh mục rủi ro đặt dưới biểu đồ để tránh chồng nhãn")
    ax = fig.add_axes([0.09, 0.20, 0.84, 0.68])
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6)); ax.set_yticks(range(1, 6))
    ax.set_xlabel("Mức độ tác động", labelpad=9, fontsize=10, color=DARK)
    ax.set_ylabel("Xác suất xảy ra", labelpad=9, fontsize=10, color=DARK)
    ax.tick_params(length=0, labelsize=9, colors=SLATE)
    for spine in ax.spines.values(): spine.set_visible(False)

    for probability in range(1, 6):
        for impact in range(1, 6):
            score = probability * impact
            if score <= 4:
                fill = RISK_LOW
            elif score <= 9:
                fill = RISK_MEDIUM
            elif score <= 15:
                fill = RISK_HIGH
            else:
                fill = RISK_CRITICAL
            ax.add_patch(Rectangle(
                (impact - 0.5, probability - 0.5), 1, 1,
                facecolor=fill, edgecolor=WHITE, linewidth=2,
            ))

    by_cell = defaultdict(list)
    for idx, (probability, impact, name, source) in enumerate(points, 1):
        by_cell[(probability, impact)].append((idx, name, source))

    for (probability, impact), cell_points in by_cell.items():
        count = len(cell_points)
        if count == 1:
            offsets = [(0, 0)]
        else:
            offsets = [
                (0.17 * math.cos(2 * math.pi * j / count),
                 0.17 * math.sin(2 * math.pi * j / count))
                for j in range(count)
            ]
        for item, (dx, dy) in zip(cell_points, offsets):
            idx, _, _ = item
            ax.scatter(impact + dx, probability + dy, s=310,
                       facecolor=NAVY, edgecolor=WHITE, linewidth=1.8, zorder=5)
            ax.text(impact + dx, probability + dy, str(idx),
                    ha="center", va="center", fontsize=8.2, fontweight="bold",
                    color=WHITE, zorder=6)

    fig.text(0.09, 0.135, "Danh mục rủi ro", fontsize=9.5,
             fontweight="bold", color=NAVY)
    if points:
        chunks = [f"{idx}. {name} · {source}"
                  for idx, (_, _, name, source) in enumerate(points, 1)]
        midpoint = math.ceil(len(chunks) / 2)
        lines = ["    ".join(chunks[:midpoint]), "    ".join(chunks[midpoint:])]
        for i, line in enumerate(lines):
            if line.strip():
                fig.text(0.09, 0.105 - i * 0.026, line,
                         fontsize=7.7, color=DARK)
    else:
        fig.text(0.09, 0.105, "Chưa có dữ liệu rủi ro hợp lệ.",
                 fontsize=8, color=SLATE)

    fig.text(0.09, 0.045,
             "Điểm rủi ro trực quan = Xác suất × Tác động",
             fontsize=8, color=SLATE)
    return _save(fig)


def roadmap_figure():
    """Lộ trình triển khai ba giai đoạn."""
    fig = _new_figure(11.5, 4.8)
    _header(fig, "Lộ trình triển khai", "Từ kiểm chứng kỹ thuật đến triển khai chính thức")
    ax = fig.add_axes([0.07, 0.18, 0.86, 0.60])
    ax.set_xlim(0, 3); ax.set_ylim(0, 1); ax.axis("off")
    stages = [
        (0.50, "01", "Kiểm chứng kỹ thuật", "Xác định kiến trúc và kiểm thử quy trình"),
        (1.50, "02", "Thử nghiệm giới hạn", "Triển khai phạm vi nhỏ và đánh giá rủi ro"),
        (2.50, "03", "Triển khai chính thức", "Mở rộng khi pháp lý, vận hành và kiểm soát đạt yêu cầu"),
    ]
    for i, (x, number, title, desc) in enumerate(stages):
        ax.add_patch(FancyBboxPatch(
            (x - 0.38, 0.25), 0.76, 0.50,
            boxstyle="round,pad=0.025,rounding_size=0.035",
            facecolor=LIGHT if i != 1 else LIGHT_BLUE,
            edgecolor=BLUE if i != 1 else NAVY,
            linewidth=1.3,
        ))
        ax.text(x, 0.66, number, ha="center", va="center",
                fontsize=11, fontweight="bold", color=BLUE)
        ax.text(x, 0.51, title, ha="center", va="center",
                fontsize=9.5, fontweight="bold", color=NAVY)
        ax.text(x, 0.35, _wrapped(desc, 27), ha="center", va="center",
                fontsize=7.7, color=DARK)
        if i < len(stages) - 1:
            ax.annotate("", xy=(x + 0.61, 0.50), xytext=(x + 0.40, 0.50),
                        arrowprops=dict(arrowstyle="-|>", color=SLATE, linewidth=1.2))
    return _save(fig)
