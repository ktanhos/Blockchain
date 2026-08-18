"""Compatibility wrapper for the Report Builder.

The final report is intentionally kept editable rather than generated as PDF.
The main application still imports this function in the current release, so
this wrapper renders the new builder and stops the legacy PDF section.
"""

import streamlit as st

from services.report_ui import render_report_builder


def build_integrated_report(profile, financials, case01, case02, case03, consistency_results, *, project_id=None, student_id=None):
    render_report_builder(st, project_id, student_id, profile, financials, case01, case02, case03)
    st.stop()
