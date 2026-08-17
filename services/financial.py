def calculate_financials(profile: dict) -> dict:
    d1 = profile["D1"]
    d2 = profile["D2"]
    d3 = profile["D3"]
    d4 = profile["D4"]
    n = profile["N"]

    # Các công thức theo tài liệu case study.
    V = 50 + (n % 451)
    loan_ratio = 0.40 + (d3 * 0.02)
    T = 2 + (d2 % 5)
    r = 0.075 + (d4 * 0.0025)
    collateral_ratio = 1.20 + (d1 * 0.05)

    loan_amount = V * loan_ratio
    external_capital = V - loan_amount
    interest = loan_amount * r
    revenue1 = V * (1.2 + d1 * 0.05)
    ebitda_margin = 0.12 + d2 * 0.01
    ebitda1 = revenue1 * ebitda_margin
    principal_payment = loan_amount / T
    debt_service1 = principal_payment + interest
    dscr = ebitda1 / debt_service1 if debt_service1 else 0.0

    collateral_value = loan_amount * collateral_ratio
    ltv = loan_amount / collateral_value if collateral_value else 0.0
    residual_cash = ebitda1 - debt_service1

    return {
        "V": V,
        "LoanRatio": loan_ratio,
        "LoanAmount": loan_amount,
        "ExternalCapital": external_capital,
        "T": T,
        "r": r,
        "CollateralRatio": collateral_ratio,
        "Interest": interest,
        "Revenue1": revenue1,
        "EbitdaMargin": ebitda_margin,
        "EBITDA1": ebitda1,
        "PrincipalPayment": principal_payment,
        "DebtService1": debt_service1,
        "DSCR": dscr,
        "CollateralValue": collateral_value,
        "LTV": ltv,
        "ResidualCash": residual_cash,
    }
