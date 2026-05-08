from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

WARSAW = ZoneInfo("Europe/Warsaw")

FLAGS = {
    "Meksyk":                       "🇲🇽",
    "RPA":                          "🇿🇦",
    "Korea Południowa":             "🇰🇷",
    "Czechy":                       "🇨🇿",
    "Kanada":                       "🇨🇦",
    "Bośnia i Hercegowina":         "🇧🇦",
    "USA":                          "🇺🇸",
    "Paragwaj":                     "🇵🇾",
    "Katar":                        "🇶🇦",
    "Szwajcaria":                   "🇨🇭",
    "Brazylia":                     "🇧🇷",
    "Maroko":                       "🇲🇦",
    "Haiti":                        "🇭🇹",
    "Szkocja":                      "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "Australia":                    "🇦🇺",
    "Turcja":                       "🇹🇷",
    "Niemcy":                       "🇩🇪",
    "Curaçao":                      "🇨🇼",
    "Holandia":                     "🇳🇱",
    "Japonia":                      "🇯🇵",
    "Wybrzeże Kości Słoniowej":     "🇨🇮",
    "Ekwador":                      "🇪🇨",
    "Szwecja":                      "🇸🇪",
    "Tunezja":                      "🇹🇳",
    "Hiszpania":                    "🇪🇸",
    "Wyspy Zielonego Przylądka":    "🇨🇻",
    "Belgia":                       "🇧🇪",
    "Egipt":                        "🇪🇬",
    "Arabia Saudyjska":             "🇸🇦",
    "Urugwaj":                      "🇺🇾",
    "Iran":                         "🇮🇷",
    "Nowa Zelandia":                "🇳🇿",
    "Francja":                      "🇫🇷",
    "Senegal":                      "🇸🇳",
    "Irak":                         "🇮🇶",
    "Norwegia":                     "🇳🇴",
    "Argentyna":                    "🇦🇷",
    "Algieria":                     "🇩🇿",
    "Austria":                      "🇦🇹",
    "Jordania":                     "🇯🇴",
    "Portugalia":                   "🇵🇹",
    "DR Kongo":                     "🇨🇩",
    "Anglia":                       "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Chorwacja":                    "🇭🇷",
}


def flag(team: str) -> str:
    return FLAGS.get(team, "🏳️")


# odds: (home_win, draw, away_win) — pre-tournament estimates, update when available
# All times are in Polish time (CEST = UTC+2)
KOLEJKA_1 = [
    # June 11
    {"id": "k1_01", "date": "2026-06-11", "time": "21:00", "home": "Meksyk",                   "away": "RPA",                       "odds": (1.80, 3.40, 4.50)},
    # June 12
    {"id": "k1_02", "date": "2026-06-12", "time": "04:00", "home": "Korea Południowa",          "away": "Czechy",                    "odds": (2.60, 3.20, 2.70)},
    {"id": "k1_03", "date": "2026-06-12", "time": "21:00", "home": "Kanada",                    "away": "Bośnia i Hercegowina",      "odds": (1.90, 3.40, 4.00)},
    # June 13
    {"id": "k1_04", "date": "2026-06-13", "time": "03:00", "home": "USA",                       "away": "Paragwaj",                  "odds": (1.70, 3.50, 5.00)},
    {"id": "k1_05", "date": "2026-06-13", "time": "21:00", "home": "Katar",                     "away": "Szwajcaria",                "odds": (3.50, 3.20, 2.10)},
    # June 14
    {"id": "k1_06", "date": "2026-06-14", "time": "00:00", "home": "Brazylia",                  "away": "Maroko",                    "odds": (1.45, 4.20, 7.00)},
    {"id": "k1_07", "date": "2026-06-14", "time": "03:00", "home": "Haiti",                     "away": "Szkocja",                   "odds": (5.00, 3.50, 1.70)},
    {"id": "k1_08", "date": "2026-06-14", "time": "06:00", "home": "Australia",                 "away": "Turcja",                    "odds": (2.40, 3.30, 3.00)},
    {"id": "k1_09", "date": "2026-06-14", "time": "19:00", "home": "Niemcy",                    "away": "Curaçao",                   "odds": (1.08, 10.0, 25.0)},
    {"id": "k1_10", "date": "2026-06-14", "time": "22:00", "home": "Holandia",                  "away": "Japonia",                   "odds": (1.70, 3.60, 5.00)},
    # June 15
    {"id": "k1_11", "date": "2026-06-15", "time": "01:00", "home": "Wybrzeże Kości Słoniowej",  "away": "Ekwador",                   "odds": (2.20, 3.20, 3.40)},
    {"id": "k1_12", "date": "2026-06-15", "time": "04:00", "home": "Szwecja",                   "away": "Tunezja",                   "odds": (2.00, 3.30, 3.80)},
    {"id": "k1_13", "date": "2026-06-15", "time": "18:00", "home": "Hiszpania",                 "away": "Wyspy Zielonego Przylądka", "odds": (1.12, 8.00, 20.0)},
    {"id": "k1_14", "date": "2026-06-15", "time": "21:00", "home": "Belgia",                    "away": "Egipt",                     "odds": (1.40, 4.20, 8.00)},
    # June 16
    {"id": "k1_15", "date": "2026-06-16", "time": "00:00", "home": "Arabia Saudyjska",          "away": "Urugwaj",                   "odds": (3.20, 3.20, 2.30)},
    {"id": "k1_16", "date": "2026-06-16", "time": "03:00", "home": "Iran",                      "away": "Nowa Zelandia",             "odds": (2.00, 3.30, 3.80)},
    {"id": "k1_17", "date": "2026-06-16", "time": "21:00", "home": "Francja",                   "away": "Senegal",                   "odds": (1.35, 4.50, 8.50)},
    # June 17
    {"id": "k1_18", "date": "2026-06-17", "time": "00:00", "home": "Irak",                      "away": "Norwegia",                  "odds": (4.50, 3.40, 1.75)},
    {"id": "k1_19", "date": "2026-06-17", "time": "03:00", "home": "Argentyna",                 "away": "Algieria",                  "odds": (1.25, 5.50, 12.0)},
    {"id": "k1_20", "date": "2026-06-17", "time": "06:00", "home": "Austria",                   "away": "Jordania",                  "odds": (1.60, 3.80, 5.50)},
    {"id": "k1_21", "date": "2026-06-17", "time": "19:00", "home": "Portugalia",                "away": "DR Kongo",                  "odds": (1.30, 5.00, 10.0)},
    {"id": "k1_22", "date": "2026-06-17", "time": "22:00", "home": "Anglia",                    "away": "Chorwacja",                 "odds": (1.50, 3.90, 6.50)},
]

_PL_MONTHS = {6: "cze", 7: "lip"}


def format_day_label(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.day} {_PL_MONTHS[dt.month]}"


def get_matches_by_day() -> dict[str, list]:
    result: dict[str, list] = {}
    for m in KOLEJKA_1:
        result.setdefault(m["date"], []).append(m)
    return result


def is_betting_open(date_str: str, time_str: str) -> bool:
    kickoff = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=WARSAW)
    return datetime.now(WARSAW) < kickoff - timedelta(hours=1)


def kickoff_datetime(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=WARSAW)


def team_label(team: str, odds_value: float) -> str:
    """Flag + name + odds: '🇲🇽 Meksyk (1.80)'"""
    return f"{flag(team)} {team} ({odds_value:.2f})"


def outcome_label(outcome: str, match: dict) -> str:
    o = match["odds"]
    if outcome == "home":
        return team_label(match["home"], o[0])
    if outcome == "draw":
        return f"🤝 Remis ({o[1]:.2f})"
    return team_label(match["away"], o[2])
