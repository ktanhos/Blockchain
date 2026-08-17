"""Instruction Engine.

This module centralizes the requirements used by the application. It does not
replace the Instruction File; it encodes the requirements so the UI and
consistency checker can validate the same rules consistently.
"""

CASE_REQUIREMENTS = {
    "Case 01": {
        "As Is Process": {"min_steps": 8},
        "Blockchain Assessment": {"required": True},
        "Architecture": {"required": True},
        "Permission Matrix": {"required": True},
        "On Chain Off Chain": {"required": True},
        "Consensus": {"required": True},
        "Governance": {"required": True},
        "Risk Register": {"min_items": 10},
        "Conclusion": {"required": True},
    },
    "Case 02": {
        "To Be Process": {"min_steps": 10, "max_steps": 15},
        "Oracle": {"required": True},
        "Smart Contract": {"required": True},
        "Scenario": {"min_scenarios": 3},
        "Risk Register": {"required": True},
        "DSCR": {"required": True},
        "LTV": {"required": True},
        "Conclusion": {"required": True},
    },
    "Case 03": {
        "Funding": {"required": True},
        "Token": {"required": True},
        "Term Sheet": {"required": True},
        "Token Lifecycle": {"min_steps": 12},
        "Smart Contract": {"required": True},
        "Investor Return": {"required": True},
        "Scenario": {"min_scenarios": 3},
        "Risk Register": {"min_items": 14},
        "Recommendation": {"required": True},
    },
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
    return {
        "As Is Process": check_requirement("Case 01", "As Is Process", {"As Is Process": as_is}),
        "Blockchain Assessment": bool(case01.get("assessment")),
        "Architecture": bool(case01.get("architecture")),
        "Permission Matrix": bool(case01.get("permissions")),
        "On Chain Off Chain": bool(case01.get("on_chain_off_chain")),
        "Consensus": bool(case01.get("consensus")),
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
        "Risk Register": bool(risks),
        "DSCR": case02.get("DSCR") is not None,
        "LTV": case02.get("LTV") is not None,
        "Conclusion": bool(case02.get("conclusion")),
    }


def validate_case03(case03):
    case03 = case03 or {}
    lifecycle = case03.get("token_lifecycle", [])
    risks = case03.get("risks", case03.get("risk_register", []))
    scenarios = case03.get("scenarios", [])
    return {
        "Funding": bool(case03.get("external_capital") or case03.get("funding")),
        "Token": bool(case03.get("token")),
        "Term Sheet": bool(case03.get("term_sheet")),
        "Token Lifecycle": check_requirement("Case 03", "Token Lifecycle", {"Token Lifecycle": lifecycle}),
        "Smart Contract": bool(case03.get("smart_contract")),
        "Investor Return": bool(case03.get("investor_return")),
        "Scenario": check_requirement("Case 03", "Scenario", {"Scenario": scenarios}),
        "Risk Register": check_requirement("Case 03", "Risk Register", {"Risk Register": risks}),
        "Recommendation": bool(case03.get("recommendation")),
    }


def instruction_summary():
    return CASE_REQUIREMENTS
