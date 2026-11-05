"""Rule-based eligibility check. No AI involved: the answer comes only from the exam data."""
from datetime import timedelta

from services.exams import fmt, to_date

# form value -> (label shown to the user, key used in the exam's "relaxation" data)
CATEGORIES = {
    "general": ("General / EWS", None),
    "obc": ("OBC (non-creamy layer)", "OBC"),
    "sc": ("SC", "SC"),
    "st": ("ST", "ST"),
    "pwbd": ("Person with disability (PwBD)", "PwBD"),
    "exsm": ("Ex-serviceman", "ExServicemen"),
}

EDUCATION = {
    "graduate": "Graduate",
    "final_year": "Final-year student",
    "not_graduate": "Not a graduate",
}


def _years_before(d, years):
    try:
        return d.replace(year=d.year - years)
    except ValueError:  # 29 February
        return d.replace(year=d.year - years, day=28)


def check_eligibility(exam, dob, education, category, percent=None):
    """Returns {"status": "eligible" | "check" | "not_eligible", "reasons": [...], "warnings": [...]}"""
    rules = exam["eligibility"]
    _, key = CATEGORIES[category]
    reasons, warnings = [], []

    # Age: uses the birth-date range, the same way the notifications state it
    cutoff = to_date(rules.get("age_cutoff"))
    if cutoff is None:
        warnings.append("The age cut-off date for this exam isn't recorded, so your age wasn't checked.")
    else:
        relax, relax_known = 0, True
        if key:
            if key in rules.get("relaxation", {}):
                relax = rules["relaxation"][key]
            else:
                relax_known = False
                warnings.append(
                    "Age relaxation for your category isn't recorded for this exam, "
                    "so the general age limit was used."
                )
        max_age = rules["age_max"] + relax
        oldest = _years_before(cutoff, max_age) + timedelta(days=1)
        youngest = _years_before(cutoff, rules["age_min"])

        if dob > youngest:
            reasons.append(
                f"Too young: you must be born on or before {fmt(youngest)} "
                f"(minimum age {rules['age_min']} on {fmt(cutoff)})."
            )
        elif dob < oldest:
            msg = (
                f"Over the age limit: you must be born on or after {fmt(oldest)} "
                f"(maximum age {max_age} on {fmt(cutoff)})."
            )
            if relax_known:
                reasons.append(msg)
            else:
                warnings.append(msg + " You may still qualify with a relaxation; check the notification.")

    # Education
    if education == "not_graduate":
        reasons.append("A graduation degree is required.")
    elif education == "final_year":
        warnings.append(
            "Final-year students can apply only if the notification lets you finish "
            "graduation by its deadline; check it."
        )

    # Marks
    min_pct = rules.get("min_percent")
    if min_pct:
        if percent is None:
            warnings.append(f"At least {min_pct}% in graduation is needed; enter your percentage to check.")
        elif percent < min_pct:
            if key is None:
                reasons.append(f"This exam asks for at least {min_pct}% in graduation.")
            else:
                warnings.append(
                    f"The general requirement is {min_pct}% in graduation. Reserved categories "
                    "may get a lower cut-off; check the notification."
                )

    if exam.get("verification") in ("partial", "low"):
        warnings.append("Some details for this exam are unconfirmed; verify with the official notification.")

    status = "not_eligible" if reasons else ("check" if warnings else "eligible")
    return {"status": status, "reasons": reasons, "warnings": warnings}
