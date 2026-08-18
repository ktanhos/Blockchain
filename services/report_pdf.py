"""Backward-compatible entry point for the Report Builder.

PDF generation is intentionally removed from the user workflow because the
Instruction requires a 30-40 page editable final report. The main application
still imports this function in the current release, so it now renders the
Report Builder and stops the old PDF flow before a PDF download is offered.
"""

from services.report_ui import render_report_builder


def build_integrated_report(profile, financials, case01, case02, case03, consistency_results, *, project_id=None, student_id=None):
    render_report_builder(None, project_id, student_id, profile, financials, case01, case02, case03)
    return b""
