def format_currency(value: float) -> str:
    return f"${value:,.2f}"

def format_percentage(value: float) -> str:
    return f"{value:.2%}"

def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0
