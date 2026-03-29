from collections import Counter


CRITICAL_CHANNELS = {"date", "barcode", "seal"}


def summarize_labels(results_with_labels, top_k=3):
    top_results = results_with_labels[:top_k]
    labels = [
        item["label"]
        for item in top_results
        if item["label"] in {"OK", "NOK"}
    ]

    counts = Counter(labels)
    return {
        "top_k": top_k,
        "labels": labels,
        "ok_count": counts.get("OK", 0),
        "nok_count": counts.get("NOK", 0),
    }


def channel_vote(channel_name: str, summary: dict) -> str:
    ok_count = summary["ok_count"]
    nok_count = summary["nok_count"]

    if nok_count >= 2:
        return "NOK"

    if ok_count >= 2 and nok_count == 0:
        return "OK"

    if ok_count == 0 and nok_count == 0:
        return "UNKNOWN"

    return "UNCERTAIN"


def aggregate_decision(channel_summaries: dict) -> dict:
    votes = {}
    for channel_name, summary in channel_summaries.items():
        votes[channel_name] = channel_vote(channel_name, summary)

    critical_nok = sum(
        1 for channel in CRITICAL_CHANNELS
        if votes.get(channel) == "NOK"
    )

    total_ok = sum(1 for v in votes.values() if v == "OK")
    total_nok = sum(1 for v in votes.values() if v == "NOK")
    total_uncertain = sum(1 for v in votes.values() if v == "UNCERTAIN")
    total_unknown = sum(1 for v in votes.values() if v == "UNKNOWN")

    if critical_nok >= 1:
        final_decision = "NOK"
        reason = "Legalább egy kritikus ROI csatorna hibás mintákhoz hasonlít."
    elif total_ok >= 3 and total_nok == 0:
        final_decision = "OK"
        reason = "A legtöbb csatorna megfelelő mintákhoz hasonlít."
    elif total_nok >= 2:
        final_decision = "NOK"
        reason = "Több csatorna hibás minták irányába szavazott."
    else:
        final_decision = "BIZONYTALAN"
        reason = "A csatornák vegyes vagy hiányos eredményt adtak."

    return {
        "final_decision": final_decision,
        "reason": reason,
        "votes": votes,
        "stats": {
            "ok": total_ok,
            "nok": total_nok,
            "uncertain": total_uncertain,
            "unknown": total_unknown,
        }
    }