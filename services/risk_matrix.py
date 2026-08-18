"""Ma trận rủi ro dành cho báo cáo.

Nguyên tắc thiết kế:
1. Biểu đồ chỉ minh họa phân bố và mức độ rủi ro.
2. Không đặt tên hoặc mã từng rủi ro lên biểu đồ.
3. Mỗi ô thể hiện mức điểm và số lượng rủi ro trong ô.
4. Risk Register phía sau mới là nơi đọc chi tiết từng rủi ro.
5. Thiết kế ưu tiên khả năng đọc trên trang A4 và màn hình Streamlit.
"""
from __future__ import annotations

from collections import Counter
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

NAVY = "#17324D"
SLATE = "#667085"
DARK = "#263442"
MUTED = "#98A2B3"
WHITE = "#FFFFFF"
GRID = "#FFFFFF"
LOW = "#E5F1EE"
MEDIUM = "#F8EDC5"
HIGH = "#F3D2D0"
CRITICAL = "#D99393"


def _collect(case01, case02, case03):
    points = []
    for source, rows in (
        ("Case 01", case01.get("risks", [])),
        ("Case 02", case02.get("risks", [])),
        ("Case 03", case03.get("risks", [])),
    ):
        for row in rows:
            try:
                p = int(row.get("P", 0))
                impact = int(row.get("I", 0))
            except (TypeError, ValueError):
                continue
            if 1 <= p <= 5 and 1 <= impact <= 5:
                points.append({
                    "id": len(points) + 1,
                    "p": p,
                    "i": impact,
                    "score": p * impact,
                    "risk": str(row.get("Rủi ro", "Rủi ro")),
                    "source": source,
                })
    return points


def _fill(score):
    if score <= 4:
        return LOW
    if score <= 9:
        return MEDIUM
    if score <= 15:
        return HIGH
    return CRITICAL


def _band(score):
    if score <= 4:
        return "Thấp"
    if score <= 9:
        return "Trung bình"
    if score <= 15:
        return "Cao"
    return "Rất cao"


def heatmap_figure(case01, case02, case03):
    """Heatmap 5x5 dạng tổng hợp theo ô, không chồng nhãn.

    Mỗi ô luôn hiển thị điểm của ô. Nếu có rủi ro tại ô đó, biểu đồ chỉ
    hiển thị số lượng rủi ro. Chi tiết từng rủi ro nằm trong Risk Register.
    """
    points = _collect(case01, case02, case03)
    counts = Counter((x["p"], x["i"]) for x in points)
    total = len(points)
    high_count = sum(x["score"] >= 10 for x in points)
    critical_count = sum(x["score"] >= 16 for x in points)

    fig = plt.figure(figsize=(10.8, 7.2), facecolor=WHITE)
    fig.text(
        0.075, 0.955, "MA TRẬN RỦI RO TÍCH HỢP",
        fontsize=16, fontweight="bold", color=NAVY, va="top",
    )
    fig.text(
        0.075, 0.918,
        "Phân bố rủi ro theo xác suất và tác động. Chi tiết được trình bày trong Risk Register.",
        fontsize=9.2, color=SLATE, va="top",
    )

    summary = [
        ("Tổng rủi ro", total),
        ("Rủi ro cao trở lên", high_count),
        ("Rủi ro rất cao", critical_count),
    ]
    for idx, (label, value) in enumerate(summary):
        x = 0.075 + idx * 0.205
        fig.patches.append(FancyBboxPatch(
            (x, 0.835), 0.175, 0.055,
            transform=fig.transFigure,
            boxstyle="round,pad=0.008,rounding_size=0.012",
            facecolor="#F6F8FA", edgecolor="#E2E8F0", linewidth=0.8,
        ))
        fig.text(x + 0.012, 0.862, label, fontsize=7.6, color=SLATE, va="center")
        fig.text(
            x + 0.162, 0.862, str(value), fontsize=11,
            fontweight="bold", color=NAVY, ha="right", va="center",
        )

    ax = fig.add_axes([0.16, 0.235, 0.68, 0.55])
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    ax.set_xlabel("Mức độ tác động", fontsize=10.5, labelpad=10, color=DARK)
    ax.set_ylabel("Xác suất xảy ra", fontsize=10.5, labelpad=10, color=DARK)
    ax.tick_params(length=0, labelsize=9, colors=SLATE)
    for spine in ax.spines.values():
        spine.set_visible(False)

    for p in range(1, 6):
        for i in range(1, 6):
            score = p * i
            ax.add_patch(Rectangle(
                (i - 0.5, p - 0.5), 1, 1,
                facecolor=_fill(score), edgecolor=GRID, linewidth=2.0,
            ))
            ax.text(
                i + 0.34, p + 0.34, str(score),
                ha="right", va="top", fontsize=7.3, color=MUTED,
            )
            count = counts.get((p, i), 0)
            if count:
                ax.text(
                    i, p + 0.01, str(count),
                    ha="center", va="center", fontsize=15,
                    fontweight="bold", color=NAVY,
                )
                ax.text(
                    i, p - 0.22, "rủi ro",
                    ha="center", va="center", fontsize=7.2, color=DARK,
                )

    legend = [
        ("Thấp", LOW, "1–4"),
        ("Trung bình", MEDIUM, "5–9"),
        ("Cao", HIGH, "10–15"),
        ("Rất cao", CRITICAL, "16–25"),
    ]
    x = 0.16
    for label, fill, score in legend:
        fig.patches.append(Rectangle(
            (x, 0.145), 0.018, 0.018,
            transform=fig.transFigure,
            facecolor=fill, edgecolor="#B7C0C8", linewidth=0.5,
        ))
        fig.text(
            x + 0.025, 0.146, f"{label} ({score})",
            fontsize=7.9, color=DARK, va="bottom",
        )
        x += 0.17

    fig.text(
        0.16, 0.095,
        "Cách đọc: điểm rủi ro = xác suất × tác động. Số lớn trong ô là số rủi ro cùng vị trí.",
        fontsize=8, color=SLATE,
    )
    fig.text(
        0.16, 0.06,
        "Mã và tên từng rủi ro được đối chiếu trong bảng Risk Register ngay sau hình.",
        fontsize=8, color=SLATE,
    )

    out = BytesIO()
    fig.savefig(
        out, format="png", dpi=220, bbox_inches="tight",
        facecolor=WHITE, pad_inches=0.12,
    )
    plt.close(fig)
    out.seek(0)
    return out


def risk_register_rows(case01, case02, case03):
    return [
        {
            "STT": x["id"],
            "Rủi ro": x["risk"],
            "Nguồn": x["source"],
            "Xác suất": x["p"],
            "Tác động": x["i"],
            "Điểm": x["score"],
            "Mức độ": _band(x["score"]),
        }
        for x in _collect(case01, case02, case03)
    ]
