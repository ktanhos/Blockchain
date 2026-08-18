"""Ma trận rủi ro dành cho báo cáo.

Thiết kế theo nguyên tắc: biểu đồ trả lời câu hỏi rủi ro nằm ở đâu;
bảng phía sau trả lời rủi ro số đó là gì. Không đưa tên dài vào trong hình.
"""
from __future__ import annotations

from collections import defaultdict
from io import BytesIO
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

NAVY = "#17324D"
SLATE = "#667085"
DARK = "#263442"
WHITE = "#FFFFFF"
LOW = "#E6F1EE"
MEDIUM = "#F8EDC5"
HIGH = "#F3D2D0"
CRITICAL = "#D99393"
GRID = "#FFFFFF"


def _collect(case01, case02, case03):
    points = []
    for source, rows in (("Case 01", case01.get("risks", [])), ("Case 02", case02.get("risks", [])), ("Case 03", case03.get("risks", []))):
        for row in rows:
            try:
                p = int(row.get("P", 0)); impact = int(row.get("I", 0))
            except (TypeError, ValueError):
                continue
            if 1 <= p <= 5 and 1 <= impact <= 5:
                points.append({"id": len(points) + 1, "p": p, "i": impact, "score": p * impact, "risk": str(row.get("Rủi ro", "Rủi ro")), "source": source})
    return points


def heatmap_figure(case01, case02, case03):
    points = _collect(case01, case02, case03)
    fig = plt.figure(figsize=(8.6, 8.2), facecolor=WHITE)
    fig.text(0.08, 0.955, "MA TRẬN RỦI RO TÍCH HỢP", fontsize=16, fontweight="bold", color=NAVY, va="top")
    fig.text(0.08, 0.918, "Số trên điểm dùng để đối chiếu với Bảng Risk Register ngay sau hình", fontsize=9, color=SLATE, va="top")

    ax = fig.add_axes([0.16, 0.22, 0.72, 0.64])
    ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6)); ax.set_yticks(range(1, 6))
    ax.set_xlabel("Mức độ tác động", fontsize=10, labelpad=9, color=DARK)
    ax.set_ylabel("Xác suất xảy ra", fontsize=10, labelpad=9, color=DARK)
    ax.tick_params(length=0, labelsize=9, colors=SLATE)
    for spine in ax.spines.values(): spine.set_visible(False)

    for p in range(1, 6):
        for i in range(1, 6):
            score = p * i
            fill = LOW if score <= 4 else MEDIUM if score <= 9 else HIGH if score <= 15 else CRITICAL
            ax.add_patch(Rectangle((i - .5, p - .5), 1, 1, facecolor=fill, edgecolor=GRID, linewidth=2))
            ax.text(i, p, str(score), ha="center", va="center", fontsize=8, color=SLATE, alpha=.65)

    by_cell = defaultdict(list)
    for item in points:
        by_cell[(item["p"], item["i"])].append(item)

    for (p, i), cell in by_cell.items():
        n = len(cell)
        if n == 1:
            offsets = [(0, 0)]
        else:
            radius = min(.22, .30 / max(1, math.sqrt(n)))
            offsets = [(radius * math.cos(2 * math.pi * j / n), radius * math.sin(2 * math.pi * j / n)) for j in range(n)]
        for item, (dx, dy) in zip(cell, offsets):
            ax.scatter(i + dx, p + dy, s=300 if n <= 6 else 230, facecolor=NAVY, edgecolor=WHITE, linewidth=1.5, zorder=5)
            ax.text(i + dx, p + dy, str(item["id"]), ha="center", va="center", fontsize=8, fontweight="bold", color=WHITE, zorder=6)

    fig.text(0.08, 0.13, "Mức độ rủi ro", fontsize=9, fontweight="bold", color=NAVY)
    legend = [("Thấp", LOW, "1–4"), ("Trung bình", MEDIUM, "5–9"), ("Cao", HIGH, "10–15"), ("Rất cao", CRITICAL, "16–25")]
    x = .08
    for label, fill, score in legend:
        fig.patches.append(Rectangle((x, .082), .022, .022, transform=fig.transFigure, facecolor=fill, edgecolor="#B7C0C8", linewidth=.5))
        fig.text(x + .029, .082, f"{label} ({score})", fontsize=7.8, color=DARK, va="bottom")
        x += .20
    fig.text(.08, .045, "Cách đọc: xác suất × tác động. Ví dụ điểm 12 thuộc vùng rủi ro cao.", fontsize=7.8, color=SLATE)

    out = BytesIO(); fig.savefig(out, format="png", dpi=220, bbox_inches="tight", facecolor=WHITE); plt.close(fig); out.seek(0)
    return out


def risk_register_rows(case01, case02, case03):
    return [{"STT": x["id"], "Rủi ro": x["risk"], "Nguồn": x["source"], "Xác suất": x["p"], "Tác động": x["i"], "Điểm": x["score"]} for x in _collect(case01, case02, case03)]
