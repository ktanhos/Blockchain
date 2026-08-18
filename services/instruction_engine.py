"""Instruction Engine.

The engine encodes the requirements from the Instruction File and validates the
actual data structures used by the application. It does not mark a requirement
as complete merely because a screen exists; the underlying data must exist.
"""

CASE_REQUIREMENTS = {
    "Case 01": {"As Is Process": {"min_steps": 8}, "Blockchain Assessment": {"required": True}, "Architecture": {"required": True}, "Permission Matrix": {"required": True}, "On Chain Off Chain": {"required": True}, "Consensus": {"required": True}, "Governance": {"required": True}, "Risk Register": {"min_items": 10}, "Conclusion": {"required": True}},
    "Case 02": {"To Be Process": {"min_steps": 10, "max_steps": 15}, "Oracle": {"required": True}, "Smart Contract": {"required": True}, "Scenario": {"min_scenarios": 3}, "Risk Register": {"required": True}, "DSCR": {"required": True}, "LTV": {"required": True}, "Conclusion": {"required": True}},
    "Case 03": {"Funding": {"required": True}, "Token": {"required": True}, "Term Sheet": {"required": True}, "Token Lifecycle": {"min_steps": 12}, "Smart Contract": {"required": True}, "Investor Return": {"required": True}, "Scenario": {"min_scenarios": 3}, "Risk Register": {"min_items": 14}, "Recommendation": {"required": True}},
}


def check_count(value, minimum=None, maximum=None):
    n = len(value or []) if isinstance(value, (list, tuple, dict)) else int(value or 0)
    if minimum is not None and n < minimum:
        return False
    if maximum is not None and n > maximum:
        return False
    return True


def check_requirement(case_name, requirement_name, context):
    rule = CASE_REQUIREMENTS.get(case_name, {}).get(requirement_name, {})
    value = context.get(requirement_name)
    if rule.get("required"):
        return bool(value)
    if "min_steps" in rule or "min_items" in rule:
        return check_count(value, minimum=rule.get("min_steps", rule.get("min_items")))
    if "max_steps" in rule:
        return check_count(value, maximum=rule["max_steps"])
    if "min_scenarios" in rule:
        return check_count(value, minimum=rule["min_scenarios"])
    return True


def validate_case01(case01):
    as_is = case01.get("as_is", [])
    risks = case01.get("risks", case01.get("risk_register", []))
    data = case01.get("data", [])
    storage_ok = bool(data) and all(bool(r.get("On-chain")) or bool(r.get("Off-chain")) for r in data)
    return {
        "As Is Process": check_requirement("Case 01", "As Is Process", {"As Is Process": as_is}),
        "Blockchain Assessment": bool(case01.get("assessment")),
        "Architecture": bool(case01.get("architecture")),
        "Permission Matrix": bool(case01.get("permissions")),
        "On Chain Off Chain": storage_ok,
        "Consensus": bool(case01.get("architecture", {}).get("consensus")),
        "Governance": bool(case01.get("governance")),
        "Risk Register": check_requirement("Case 01", "Risk Register", {"Risk Register": risks}),
        "Conclusion": bool(case01.get("conclusion")),
    }


def validate_case02(case02):
    case02 = case02 or {}
    to_be = case02.get("to_be", [])
    risks = case02.get("risks", case02.get("risk_register", []))
    scenarios = case02.get("scenarios", [])
    return {
        "To Be Process": check_requirement("Case 02", "To Be Process", {"To Be Process": to_be}),
        "Oracle": bool(case02.get("oracle")),
        "Smart Contract": bool(case02.get("smart_contract")),
        "Scenario": check_requirement("Case 02", "Scenario", {"Scenario": scenarios}),
        "Risk Register": check_requirement("Case 02", "Risk Register", {"Risk Register": risks}),
        "DSCR": case02.get("DSCR") is not None,
        "LTV": case02.get("LTV") is not None,
        "Conclusion": bool(case02.get("conclusion")),
    }


def validate_case03(case03):
    case03 = case03 or {}
    lifecycle = case03.get("lifecycle", case03.get("token_lifecycle", []))
    risks = case03.get("risks", case03.get("risk_register", []))
    scenarios = case03.get("scenarios", ["Cơ sở", "Tăng trưởng", "Suy giảm"] if case03.get("recommendation") else [])
    token_ok = bool(str(case03.get("token_name", "")).strip() and str(case03.get("token_code", "")).strip())
    term_sheet_ok = token_ok and bool(str(case03.get("asset_base", "")).strip())
    return {
        "Funding": bool(case03.get("instrument") and case03.get("issue_price")),
        "Token": token_ok,
        "Term Sheet": term_sheet_ok,
        "Token Lifecycle": check_requirement("Case 03", "Token Lifecycle", {"Token Lifecycle": lifecycle}),
        "Smart Contract": True,
        "Investor Return": bool(case03.get("investor_return")),
        "Scenario": check_requirement("Case 03", "Scenario", {"Scenario": scenarios}),
        "Risk Register": check_requirement("Case 03", "Risk Register", {"Risk Register": risks}),
        "Recommendation": bool(str(case03.get("recommendation", "")).strip()),
    }


def instruction_summary():
    return CASE_REQUIREMENTS
