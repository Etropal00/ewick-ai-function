import re
from typing import Dict

CLICKBAIT_PAT = re.compile(r"(tu ne devineras|incroyable|jamais|choc|choc !|impossible|top \d+|secret|révélé)", re.I)
ENGAGEMENT_BAIT_PAT = re.compile(r"(partage|tague|commente|commente\s+oui|aime si|like si)", re.I)
MISLEADING_HEAD_PAT = re.compile(r"(\?|!!!)$")
LOW_QUALITY_LP_HINT_PAT = re.compile(r"(\bbit\.ly\b|\btinyurl\b|\b(ad|ads|popup)\b)", re.I)

def heuristics(input: Dict) -> Dict:
    title = input.get("title","")
    desc = input.get("description","")
    links = input.get("links", []) or []

    clickbait = 1.0 if CLICKBAIT_PAT.search(title + " " + desc or "") else 0.0
    engagement = 1.0 if ENGAGEMENT_BAIT_PAT.search(desc or "") else 0.0
    misleading = 0.3 if MISLEADING_HEAD_PAT.search(title or "") else 0.0

    low_lp = 0.0
    for lk in links:
        if LOW_QUALITY_LP_HINT_PAT.search(lk):
            low_lp = 0.6
            break

    risk_reduce = min(1.0, 0.2*clickbait + 0.4*misleading + 0.4*low_lp + 0.2*engagement)

    # REMOVE (ex très simplifié)
    risk_remove = 0.0
    hard_words = re.compile(r"(haine|doxxing|dox|escroquerie|menace|violence)", re.I)
    if hard_words.search(title + " " + desc):
        risk_remove = 1.0

    needs_inform = False
    claims_words = re.compile(r"(fait|chiffre|selon|étude|source|news|actualité|breaking)", re.I)
    synth_words = re.compile(r"(deepfake|ai|généré|synthétique)", re.I)
    if claims_words.search(title + " " + desc) or synth_words.search(title + " " + desc):
        needs_inform = True

    return {
        "signals": {
            "clickbait": float(clickbait),
            "engagement_bait": float(engagement),
            "misleading_thumb": float(0.0),
            "low_quality_landing": float(low_lp),
            "repeat_offender_hint": float(0.0)
        },
        "scores": {
            "risk_remove": float(risk_remove),
            "risk_reduce": float(risk_reduce)
        },
        "actions": {
            "needs_inform": bool(needs_inform)
        }
    }
