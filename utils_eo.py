from typing import Sequence
from lightbulb import Choice
from csv import DictReader
import re
from functools import lru_cache
from datetime import datetime, date, timedelta, UTC

BOOLEAN_CHOICES = [
    Choice(name="Jes", value=1),
    Choice(name="Ne", value=-1),
]

__COLORS = {}

with open("colors.csv", "r", encoding="utf8") as f:
    reader = DictReader(f)
    for color in reader:
        __COLORS[color["Koloro"][:-1]] = {"hel": color["Hela"], "malhel": color["Malhela"]}

@lru_cache
def get_color(name: str) -> str:
    """
    Koloro nomata `name`

    Rezultas la sescifera RVB-kodaĵo,
    se la nomo estas difinita en `colors.csv`
    """
    name = name.strip().lower()
    if re.match(r"#([0-9a-f]{3}){1,2}", name):
        return name
    if name.endswith("n"): name = name[:-1]
    if name.endswith("j"): name = name[:-1]
    match = re.match(r"((?:(?:mal)?hel)?)(?:[ae] ?)?([a-zĉĝĥĵŝŭ]+)$", name[:-1])
    if not match:
        raise ValueError(f"{name} ne estas valida koloro")
    shade, color = match.groups()
    if shade == "": shade = "hel"
    if color not in __COLORS:
        raise ValueError(f"{name} ne estas valida koloro")
    return __COLORS[color][shade]

def human_readable_time(time: datetime) -> str:
    """
    Komprenebla por homoj esprimo de la dato kaj la tempo
    prezentitaj en `time`. La formato estas:
        Hodiaŭ je 12:34 laŭ UTC
    aŭ
        1887-12-15 12:34 laŭ UTC
    """
    rezulto = ""
    time = time.astimezone(UTC)
    original_date = time.date()
    today = datetime.now(UTC).date()
    day_delta = timedelta(days=1)
    yesterday = today - day_delta
    tomorrow = today + day_delta
    if original_date == today:
        rezulto = "Hodiaŭ"
    elif original_date == yesterday:
        rezulto = "Hieraŭ"
    elif original_date == tomorrow:
        rezulto = "Morgaŭ"
    else:
        rezulto = original_date.isoformat()
    rezulto += f" je {time.time().isoformat('minutes')} laŭ UTC"
    return rezulto

def plural(number: int) -> str:
    """
    Pluralo (multnombro)
    
    Rezultas "j" se `number` ne estas unu kaj "" se `number` estas unu
    """
    return "j" if number != 1 else ""

def __conjunction_join(sequence: Sequence[str], conjunction: str) -> str:
    """
    Kunigi per konjunkcio

    Rezultas tekstaĵo kuniganta la elementojn de `sequence`
    per komoj kaj la konjunkcio `conjunction`
    """
    if len(sequence) <= 2:
        return " kaj ".join(sequence)
    return ", ".join(sequence[:-1]) + " " + conjunction + " " + sequence[-1]

def aux_join(sequence: Sequence[str]) -> str:
    """
    Kunigi per «aŭ»

    Rezultas tekstaĵo kuniganta la elementojn de `sequence`
    per komoj kaj la konjunkcio «aŭ»
    """
    return __conjunction_join(sequence, "aŭ")

def kaj_join(sequence: Sequence[str]) -> str:
    """
    Kunigi per «kaj»

    Rezultas tekstaĵo kuniganta la elementojn de `sequence`
    per komoj kaj la konjunkcio «kaj»
    """
    return __conjunction_join(sequence, "kaj")