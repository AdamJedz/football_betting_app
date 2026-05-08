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
    "Kolumbia":                     "🇨🇴",
    "Uzbekistan":                   "🇺🇿",
    "Panama":                       "🇵🇦",
    "Ghana":                        "🇬🇭",
}


def flag(team: str) -> str:
    return FLAGS.get(team, "🏳️")


# Groups (for reference):
# A: Meksyk, Korea Południowa, RPA, Czechy
# B: Kanada, Bośnia i Hercegowina, Katar, Szwajcaria
# C: Brazylia, Maroko, Haiti, Szkocja
# D: USA, Paragwaj, Australia, Turcja
# E: Niemcy, Curaçao, Wybrzeże Kości Słoniowej, Ekwador
# F: Holandia, Japonia, Tunezja, Szwecja
# G: Belgia, Iran, Egipt, Nowa Zelandia
# H: Hiszpania, Wyspy Zielonego Przylądka, Arabia Saudyjska, Urugwaj
# I: Francja, Senegal, Irak, Norwegia
# J: Argentyna, Algieria, Austria, Jordania
# K: Portugalia, DR Kongo, Kolumbia, Uzbekistan
# L: Anglia, Chorwacja, Panama, Ghana

# All times are in Polish time (CEST = UTC+2)
# TEST BRANCH: all dates compressed into May 8-12 2026 for live testing
KOLEJKA_1 = [
    # May 8
    {"id": "k1_01", "date": "2026-05-08", "time": "01:00", "home": "Meksyk",                   "away": "RPA",                       "odds": (1.80, 3.40, 4.50)},
    {"id": "k1_02", "date": "2026-05-08", "time": "03:00", "home": "Korea Południowa",          "away": "Czechy",                    "odds": (2.60, 3.20, 2.70)},
    {"id": "k1_03", "date": "2026-05-08", "time": "05:00", "home": "Kanada",                    "away": "Bośnia i Hercegowina",      "odds": (1.90, 3.40, 4.00)},
    {"id": "k1_04", "date": "2026-05-08", "time": "07:00", "home": "USA",                       "away": "Paragwaj",                  "odds": (1.70, 3.50, 5.00)},
    {"id": "k1_05", "date": "2026-05-08", "time": "09:00", "home": "Katar",                     "away": "Szwajcaria",                "odds": (3.50, 3.20, 2.10)},
    {"id": "k1_06", "date": "2026-05-08", "time": "11:00", "home": "Brazylia",                  "away": "Maroko",                    "odds": (1.45, 4.20, 7.00)},
    {"id": "k1_07", "date": "2026-05-08", "time": "13:00", "home": "Haiti",                     "away": "Szkocja",                   "odds": (5.00, 3.50, 1.70)},
    {"id": "k1_08", "date": "2026-05-08", "time": "15:00", "home": "Australia",                 "away": "Turcja",                    "odds": (2.40, 3.30, 3.00)},
    {"id": "k1_09", "date": "2026-05-08", "time": "17:00", "home": "Niemcy",                    "away": "Curaçao",                   "odds": (1.08, 10.0, 25.0)},
    {"id": "k1_10", "date": "2026-05-08", "time": "19:00", "home": "Holandia",                  "away": "Japonia",                   "odds": (1.70, 3.60, 5.00)},
    {"id": "k1_11", "date": "2026-05-08", "time": "21:00", "home": "Wybrzeże Kości Słoniowej",  "away": "Ekwador",                   "odds": (2.20, 3.20, 3.40)},
    {"id": "k1_12", "date": "2026-05-08", "time": "23:00", "home": "Szwecja",                   "away": "Tunezja",                   "odds": (2.00, 3.30, 3.80)},
    # May 9
    {"id": "k1_13", "date": "2026-05-09", "time": "01:00", "home": "Hiszpania",                 "away": "Wyspy Zielonego Przylądka", "odds": (1.12, 8.00, 20.0)},
    {"id": "k1_14", "date": "2026-05-09", "time": "03:00", "home": "Belgia",                    "away": "Egipt",                     "odds": (1.40, 4.20, 8.00)},
    {"id": "k1_15", "date": "2026-05-09", "time": "05:00", "home": "Arabia Saudyjska",          "away": "Urugwaj",                   "odds": (3.20, 3.20, 2.30)},
    {"id": "k1_16", "date": "2026-05-09", "time": "07:00", "home": "Iran",                      "away": "Nowa Zelandia",             "odds": (2.00, 3.30, 3.80)},
    {"id": "k1_17", "date": "2026-05-09", "time": "09:00", "home": "Francja",                   "away": "Senegal",                   "odds": (1.35, 4.50, 8.50)},
    {"id": "k1_18", "date": "2026-05-09", "time": "11:00", "home": "Irak",                      "away": "Norwegia",                  "odds": (4.50, 3.40, 1.75)},
    {"id": "k1_19", "date": "2026-05-09", "time": "13:00", "home": "Argentyna",                 "away": "Algieria",                  "odds": (1.25, 5.50, 12.0)},
    {"id": "k1_20", "date": "2026-05-09", "time": "15:00", "home": "Austria",                   "away": "Jordania",                  "odds": (1.60, 3.80, 5.50)},
    {"id": "k1_21", "date": "2026-05-09", "time": "17:00", "home": "Portugalia",                "away": "DR Kongo",                  "odds": (1.30, 5.00, 10.0)},
    {"id": "k1_22", "date": "2026-05-09", "time": "19:00", "home": "Anglia",                    "away": "Chorwacja",                 "odds": (1.50, 3.90, 6.50)},
    {"id": "k1_23", "date": "2026-05-09", "time": "21:00", "home": "Panama",                    "away": "Ghana",                     "odds": (2.80, 3.20, 2.60)},
    {"id": "k1_24", "date": "2026-05-09", "time": "23:00", "home": "Kolumbia",                  "away": "Uzbekistan",                "odds": (1.80, 3.40, 4.50)},
]

KOLEJKA_2 = [
    # May 10
    {"id": "k2_01", "date": "2026-05-10", "time": "01:00", "home": "Czechy",                    "away": "RPA",                       "odds": (2.00, 3.20, 3.80)},
    {"id": "k2_02", "date": "2026-05-10", "time": "03:00", "home": "Szwajcaria",                "away": "Bośnia i Hercegowina",      "odds": (1.85, 3.30, 4.50)},
    {"id": "k2_03", "date": "2026-05-10", "time": "05:00", "home": "Kanada",                    "away": "Katar",                     "odds": (1.60, 3.80, 6.00)},
    {"id": "k2_04", "date": "2026-05-10", "time": "07:00", "home": "Meksyk",                    "away": "Korea Południowa",          "odds": (1.90, 3.30, 4.20)},
    {"id": "k2_05", "date": "2026-05-10", "time": "09:00", "home": "USA",                       "away": "Australia",                 "odds": (2.10, 3.20, 3.40)},
    {"id": "k2_06", "date": "2026-05-10", "time": "11:00", "home": "Szkocja",                   "away": "Maroko",                    "odds": (2.60, 3.20, 2.80)},
    {"id": "k2_07", "date": "2026-05-10", "time": "13:00", "home": "Brazylia",                  "away": "Haiti",                     "odds": (1.12, 8.00, 22.0)},
    {"id": "k2_08", "date": "2026-05-10", "time": "15:00", "home": "Turcja",                    "away": "Paragwaj",                  "odds": (2.20, 3.30, 3.20)},
    {"id": "k2_09", "date": "2026-05-10", "time": "17:00", "home": "Holandia",                  "away": "Szwecja",                   "odds": (1.85, 3.30, 4.20)},
    {"id": "k2_10", "date": "2026-05-10", "time": "19:00", "home": "Niemcy",                    "away": "Wybrzeże Kości Słoniowej",  "odds": (1.55, 4.00, 6.50)},
    {"id": "k2_11", "date": "2026-05-10", "time": "21:00", "home": "Ekwador",                   "away": "Curaçao",                   "odds": (1.30, 5.00, 10.0)},
    {"id": "k2_12", "date": "2026-05-10", "time": "23:00", "home": "Tunezja",                   "away": "Japonia",                   "odds": (3.20, 3.10, 2.30)},
    # May 11
    {"id": "k2_13", "date": "2026-05-11", "time": "01:00", "home": "Hiszpania",                 "away": "Arabia Saudyjska",          "odds": (1.15, 7.00, 18.0)},
    {"id": "k2_14", "date": "2026-05-11", "time": "03:00", "home": "Belgia",                    "away": "Iran",                      "odds": (1.60, 3.70, 6.00)},
    {"id": "k2_15", "date": "2026-05-11", "time": "05:00", "home": "Urugwaj",                   "away": "Wyspy Zielonego Przylądka", "odds": (1.45, 4.20, 7.50)},
    {"id": "k2_16", "date": "2026-05-11", "time": "07:00", "home": "Nowa Zelandia",             "away": "Egipt",                     "odds": (2.80, 3.10, 2.60)},
    {"id": "k2_17", "date": "2026-05-11", "time": "09:00", "home": "Argentyna",                 "away": "Austria",                   "odds": (1.35, 4.50, 8.50)},
    {"id": "k2_18", "date": "2026-05-11", "time": "11:00", "home": "Francja",                   "away": "Irak",                      "odds": (1.15, 7.50, 20.0)},
    {"id": "k2_19", "date": "2026-05-11", "time": "13:00", "home": "Norwegia",                  "away": "Senegal",                   "odds": (2.20, 3.20, 3.20)},
    {"id": "k2_20", "date": "2026-05-11", "time": "15:00", "home": "Jordania",                  "away": "Algieria",                  "odds": (3.00, 3.20, 2.40)},
    {"id": "k2_21", "date": "2026-05-11", "time": "17:00", "home": "Portugalia",                "away": "Uzbekistan",                "odds": (1.20, 7.00, 15.0)},
    {"id": "k2_22", "date": "2026-05-11", "time": "19:00", "home": "Anglia",                    "away": "Ghana",                     "odds": (1.50, 4.00, 6.50)},
    {"id": "k2_23", "date": "2026-05-11", "time": "21:00", "home": "Panama",                    "away": "Chorwacja",                 "odds": (4.50, 3.40, 1.75)},
    {"id": "k2_24", "date": "2026-05-11", "time": "23:00", "home": "Kolumbia",                  "away": "DR Kongo",                  "odds": (1.80, 3.40, 4.50)},
]

KOLEJKA_3 = [
    # May 12 — Group B (simultaneous)
    {"id": "k3_01", "date": "2026-05-12", "time": "01:00", "home": "Szwajcaria",                "away": "Kanada",                    "odds": (2.10, 3.20, 3.40)},
    {"id": "k3_02", "date": "2026-05-12", "time": "01:00", "home": "Bośnia i Hercegowina",      "away": "Katar",                     "odds": (2.00, 3.30, 3.80)},
    # May 12 — Group C (simultaneous)
    {"id": "k3_03", "date": "2026-05-12", "time": "03:00", "home": "Szkocja",                   "away": "Brazylia",                  "odds": (8.00, 5.00, 1.25)},
    {"id": "k3_04", "date": "2026-05-12", "time": "03:00", "home": "Maroko",                    "away": "Haiti",                     "odds": (1.70, 3.50, 5.00)},
    # May 12 — Group A (simultaneous)
    {"id": "k3_05", "date": "2026-05-12", "time": "05:00", "home": "Czechy",                    "away": "Meksyk",                    "odds": (2.80, 3.10, 2.60)},
    {"id": "k3_06", "date": "2026-05-12", "time": "05:00", "home": "RPA",                       "away": "Korea Południowa",          "odds": (3.00, 3.20, 2.40)},
    # May 12 — Group D (simultaneous)
    {"id": "k3_07", "date": "2026-05-12", "time": "07:00", "home": "USA",                       "away": "Turcja",                    "odds": (2.20, 3.30, 3.20)},
    {"id": "k3_08", "date": "2026-05-12", "time": "07:00", "home": "Australia",                 "away": "Paragwaj",                  "odds": (2.50, 3.20, 2.90)},
    # May 12 — Group E (simultaneous)
    {"id": "k3_09", "date": "2026-05-12", "time": "09:00", "home": "Niemcy",                    "away": "Ekwador",                   "odds": (1.45, 4.20, 7.00)},
    {"id": "k3_10", "date": "2026-05-12", "time": "09:00", "home": "Wybrzeże Kości Słoniowej",  "away": "Curaçao",                   "odds": (1.60, 3.80, 6.00)},
    # May 12 — Group F (simultaneous)
    {"id": "k3_11", "date": "2026-05-12", "time": "11:00", "home": "Holandia",                  "away": "Tunezja",                   "odds": (1.50, 4.00, 7.00)},
    {"id": "k3_12", "date": "2026-05-12", "time": "11:00", "home": "Japonia",                   "away": "Szwecja",                   "odds": (2.60, 3.20, 2.70)},
    # May 12 — Group I (simultaneous)
    {"id": "k3_13", "date": "2026-05-12", "time": "13:00", "home": "Francja",                   "away": "Norwegia",                  "odds": (1.60, 3.70, 6.00)},
    {"id": "k3_14", "date": "2026-05-12", "time": "13:00", "home": "Senegal",                   "away": "Irak",                      "odds": (1.90, 3.30, 4.20)},
    # May 12 — Group H (simultaneous)
    {"id": "k3_15", "date": "2026-05-12", "time": "15:00", "home": "Hiszpania",                 "away": "Urugwaj",                   "odds": (1.50, 4.00, 7.00)},
    {"id": "k3_16", "date": "2026-05-12", "time": "15:00", "home": "Arabia Saudyjska",          "away": "Wyspy Zielonego Przylądka", "odds": (1.70, 3.50, 5.00)},
    # May 12 — Group G (simultaneous)
    {"id": "k3_17", "date": "2026-05-12", "time": "17:00", "home": "Belgia",                    "away": "Nowa Zelandia",             "odds": (1.35, 5.00, 9.00)},
    {"id": "k3_18", "date": "2026-05-12", "time": "17:00", "home": "Egipt",                     "away": "Iran",                      "odds": (2.70, 3.10, 2.70)},
    # May 12 — Group L (simultaneous)
    {"id": "k3_19", "date": "2026-05-12", "time": "19:00", "home": "Anglia",                    "away": "Panama",                    "odds": (1.30, 5.00, 10.0)},
    {"id": "k3_20", "date": "2026-05-12", "time": "19:00", "home": "Chorwacja",                 "away": "Ghana",                     "odds": (1.90, 3.30, 4.20)},
    # May 12 — Group K (simultaneous)
    {"id": "k3_21", "date": "2026-05-12", "time": "21:00", "home": "Portugalia",                "away": "Kolumbia",                  "odds": (1.65, 3.80, 5.50)},
    {"id": "k3_22", "date": "2026-05-12", "time": "21:00", "home": "Uzbekistan",                "away": "DR Kongo",                  "odds": (2.20, 3.20, 3.20)},
    # May 12 — Group J (simultaneous)
    {"id": "k3_23", "date": "2026-05-12", "time": "23:00", "home": "Argentyna",                 "away": "Jordania",                  "odds": (1.20, 7.00, 15.0)},
    {"id": "k3_24", "date": "2026-05-12", "time": "23:00", "home": "Austria",                   "away": "Algieria",                  "odds": (2.40, 3.20, 3.00)},
]

_PL_MONTHS = {5: "maj", 6: "cze", 7: "lip"}


def format_day_label(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.day} {_PL_MONTHS[dt.month]}"


def get_matches_by_day(matches: list) -> dict[str, list]:
    result: dict[str, list] = {}
    for m in matches:
        result.setdefault(m["date"], []).append(m)
    return result


def is_betting_open(date_str: str, time_str: str) -> bool:
    kickoff = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=WARSAW)
    return datetime.now(WARSAW) < kickoff - timedelta(hours=1)


def kickoff_datetime(date_str: str, time_str: str) -> datetime:
    return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=WARSAW)


def can_set_result(date_str: str, time_str: str, username: str) -> bool:
    """Admin: any time. Others: 2h after kickoff."""
    kickoff = kickoff_datetime(date_str, time_str)
    now = datetime.now(WARSAW)
    if username == "admin":
        return True
    return now >= kickoff + timedelta(hours=2)


def result_unlock_time(date_str: str, time_str: str) -> datetime:
    return kickoff_datetime(date_str, time_str) + timedelta(hours=2)


def outcome_label(outcome: str, match: dict) -> str:
    if outcome == "home":
        return match["home"]
    if outcome == "draw":
        return "🤝 Remis"
    return match["away"]


def outcome_opts(match: dict, odds: tuple) -> dict:
    return {
        "home": f"{match['home']} ({odds[0]:.2f})",
        "draw": f"🤝 Remis ({odds[1]:.2f})",
        "away": f"{match['away']} ({odds[2]:.2f})",
    }
