from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

WARSAW = ZoneInfo("Europe/Warsaw")

# All times are in Polish time (CEST = UTC+2), converted from BST (UK) source
KOLEJKA_1 = [
    # June 11
    {"id": "k1_01", "date": "2026-06-11", "time": "21:00", "home": "Meksyk",                      "away": "RPA"},
    # June 12
    {"id": "k1_02", "date": "2026-06-12", "time": "04:00", "home": "Korea Południowa",             "away": "Czechy"},
    {"id": "k1_03", "date": "2026-06-12", "time": "21:00", "home": "Kanada",                       "away": "Bośnia i Hercegowina"},
    # June 13
    {"id": "k1_04", "date": "2026-06-13", "time": "03:00", "home": "USA",                          "away": "Paragwaj"},
    {"id": "k1_05", "date": "2026-06-13", "time": "21:00", "home": "Katar",                        "away": "Szwajcaria"},
    # June 14
    {"id": "k1_06", "date": "2026-06-14", "time": "00:00", "home": "Brazylia",                     "away": "Maroko"},
    {"id": "k1_07", "date": "2026-06-14", "time": "03:00", "home": "Haiti",                        "away": "Szkocja"},
    {"id": "k1_08", "date": "2026-06-14", "time": "06:00", "home": "Australia",                    "away": "Turcja"},
    {"id": "k1_09", "date": "2026-06-14", "time": "19:00", "home": "Niemcy",                       "away": "Curaçao"},
    {"id": "k1_10", "date": "2026-06-14", "time": "22:00", "home": "Holandia",                     "away": "Japonia"},
    # June 15
    {"id": "k1_11", "date": "2026-06-15", "time": "01:00", "home": "Wybrzeże Kości Słoniowej",     "away": "Ekwador"},
    {"id": "k1_12", "date": "2026-06-15", "time": "04:00", "home": "Szwecja",                      "away": "Tunezja"},
    {"id": "k1_13", "date": "2026-06-15", "time": "18:00", "home": "Hiszpania",                    "away": "Wyspy Zielonego Przylądka"},
    {"id": "k1_14", "date": "2026-06-15", "time": "21:00", "home": "Belgia",                       "away": "Egipt"},
    # June 16
    {"id": "k1_15", "date": "2026-06-16", "time": "00:00", "home": "Arabia Saudyjska",             "away": "Urugwaj"},
    {"id": "k1_16", "date": "2026-06-16", "time": "03:00", "home": "Iran",                         "away": "Nowa Zelandia"},
    {"id": "k1_17", "date": "2026-06-16", "time": "21:00", "home": "Francja",                      "away": "Senegal"},
    # June 17
    {"id": "k1_18", "date": "2026-06-17", "time": "00:00", "home": "Irak",                         "away": "Norwegia"},
    {"id": "k1_19", "date": "2026-06-17", "time": "03:00", "home": "Argentyna",                    "away": "Algieria"},
    {"id": "k1_20", "date": "2026-06-17", "time": "06:00", "home": "Austria",                      "away": "Jordania"},
    {"id": "k1_21", "date": "2026-06-17", "time": "19:00", "home": "Portugalia",                   "away": "DR Kongo"},
    {"id": "k1_22", "date": "2026-06-17", "time": "22:00", "home": "Anglia",                       "away": "Chorwacja"},
]

_PL_MONTHS = {
    6: "cze", 7: "lip",
}


def format_day_label(date_str: str) -> str:
    """'2026-06-14' → '14 cze'"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.day} {_PL_MONTHS[dt.month]}"


def get_matches_by_day() -> dict[str, list]:
    result: dict[str, list] = {}
    for m in KOLEJKA_1:
        result.setdefault(m["date"], []).append(m)
    return result


def is_betting_open(date_str: str, time_str: str) -> bool:
    """True if current Warsaw time is more than 1 hour before kickoff."""
    kickoff = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=WARSAW)
    return datetime.now(WARSAW) < kickoff - timedelta(hours=1)


def kickoff_datetime(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=WARSAW)


def outcome_label(outcome: str, match: dict) -> str:
    if outcome == "home":
        return f"🏠 {match['home']} wygra"
    if outcome == "draw":
        return "🤝 Remis"
    return f"✈️ {match['away']} wygra"
