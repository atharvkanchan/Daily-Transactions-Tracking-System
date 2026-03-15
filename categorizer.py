def detect_category(desc):

    desc = str(desc).lower()

    if "uber" in desc or "ola" in desc:
        return "Travel"

    if "restaurant" in desc or "food" in desc:
        return "Food"

    if "amazon" in desc or "shopping" in desc:
        return "Shopping"

    if "salary" in desc or "income" in desc:
        return "Income"

    if "stock" in desc or "investment" in desc:
        return "Investment"

    if "netflix" in desc:
        return "Entertainment"

    return "Other"


def detect_type(category):

    if category in ["Income","Investment"]:
        return "Asset"

    return "Liability"
