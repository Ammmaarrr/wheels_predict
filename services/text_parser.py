"""
Text parsing utilities to extract structured vehicle info from free text.
Adapted from the Jupyter enrichment logic.
"""

from __future__ import annotations

import re
from typing import Dict, Optional


# Regexes and lexicons
num_re = re.compile(r"(?<!\d)(\d{1,3}(?:[\,\.]\d{3})+|\d+(?:\.\d+)?)(?!\d)")
km_re = re.compile(r"(\d[\d,\.]*?)\s*(?:km|kms|kilometer|kilometers)\b", re.I)
cc_re = re.compile(r"(\d{3,4})\s*cc\b", re.I)
year_re = re.compile(r"\b(19\d{2}|20\d{2})\b")
price_pk_re = re.compile(r"\b(?:pkr|rs\.?|rupees)\s*([\d,\.]+)\b", re.I)
price_unit_re = re.compile(r"\b(?:pkr\s*)?([\d,\.]+)\s*(lacs?|lac|million|m|crore|cr)\b", re.I)
city_in_re = re.compile(r"for sale in\s*([A-Za-z\-\s]+?)(?:\s+for\b|,|\.|$)", re.I)

colors = {
    'white','black','silver','grey','gray','blue','red','green','yellow','gold','brown','maroon','beige','purple','orange'
}
body_types = {'hatchback','sedan','suv','crossover','mpv','van','wagon','coupe','convertible','jeep','pickup'}
fuels = {'petrol','diesel','cng','hybrid','electric'}
transmissions = {'automatic','manual','cvt','ags','auto'}
conditions = {'used','new','reconditioned'}

known_makes = {
    'suzuki','toyota','honda','daihatsu','hyundai','kia','nissan','mitsubishi','mercedes','bmw','audi','changan','prince','faw','mg','proton','peugeot','dfsk',
}

model_body_map = {
    # Suzuki
    'wagon r': 'Hatchback', 'alto': 'Hatchback', 'cultus': 'Hatchback', 'swift': 'Hatchback', 'mehran': 'Hatchback', 'bolan': 'Van',
    # Toyota
    'corolla': 'Sedan', 'yaris': 'Sedan', 'vitz': 'Hatchback', 'aqua': 'Hatchback', 'prius': 'Hatchback', 'fortuner': 'SUV', 'hilux': 'Pickup', 'passo': 'Hatchback',
    # Honda
    'civic': 'Sedan', 'city': 'Sedan', 'fit': 'Hatchback', 'vezel': 'Crossover', 'br-v': 'MPV', 'brv': 'MPV',
    # Nissan / Daihatsu
    'dayz': 'Hatchback', 'mira': 'Hatchback', 'move': 'Hatchback',
    # Hyundai / KIA
    'tucson': 'SUV', 'elantra': 'Sedan', 'sonata': 'Sedan', 'sportage': 'SUV', 'picanto': 'Hatchback',
    # Others
    'mg hs': 'SUV', 'mg zs': 'SUV', 'alsvin': 'Sedan', 'saga': 'Sedan', 'pearl': 'Hatchback'
}


def parse_price_to_pkr(text: str) -> Optional[int]:
    if not text:
        return None
    t = text.lower()
    m = price_unit_re.search(t)
    if m:
        try:
            num = float(m.group(1).replace(',', ''))
        except Exception:
            num = None
        unit = m.group(2).lower()
        if num is not None:
            if unit.startswith('lac'):
                return int(num * 100_000)
            if unit.startswith('m') or unit.startswith('million'):
                return int(num * 1_000_000)
            if unit.startswith('cr') or unit.startswith('crore'):
                return int(num * 10_000_000)
    m = price_pk_re.search(t)
    if m:
        val = m.group(1).replace(',', '')
        try:
            return int(float(val))
        except Exception:
            return None
    return None


def extract_simple_token(text: str, candidates: set) -> Optional[str]:
    if not text:
        return None
    t = text.lower()
    for w in candidates:
        if re.search(rf"\b{re.escape(w)}\b", t):
            return w
    return None


def parse_make_model_variant(title: str, year: Optional[int]) -> Dict[str, Optional[str]]:
    res = {"make": None, "model": None, "variant": None}
    if not title:
        return res
    tokens = title.split()
    if not tokens:
        return res
    mk = None
    start = 0
    for i, tok in enumerate(tokens):
        low = tok.lower().strip(',:-()')
        if low in known_makes:
            mk = tokens[i]
            start = i + 1
            break
    if mk is None:
        first = tokens[0]
        if first and first[0].isupper():
            mk = first
            start = 1
        else:
            return res
    res["make"] = mk.title()
    stop = len(tokens)
    for j in range(start, len(tokens)):
        tok = tokens[j]
        if year and re.fullmatch(r"\d{4}", tok):
            stop = j
            break
        low = tok.lower().strip(',./')
        if low in {'used','new','for','sale','in','pkr'}:
            stop = j
            break
    mid = tokens[start:stop]
    if not mid:
        return res
    if len(mid) >= 2:
        res["variant"] = mid[-1].upper() if mid[-1].isalpha() else mid[-1]
        res["model"] = " ".join(mid[:-1]).title()
    else:
        res["model"] = mid[0].title()
    return res


def infer_body_type(make: Optional[str], model: Optional[str], text: str) -> Optional[str]:
    t = text.lower()
    avoid_wagon = 'wagon r' in t
    bt = extract_simple_token(text, body_types)
    if bt:
        if bt == 'wagon' and avoid_wagon:
            bt = None
        if bt:
            return bt.title()
    key = (model or '').lower().strip()
    key = re.sub(r"\s+", ' ', key)
    if key in model_body_map:
        return model_body_map[key]
    for k, v in model_body_map.items():
        if k in key:
            return v
    return None


def infer_fuel_type(text: str, make: Optional[str], model: Optional[str]) -> Optional[str]:
    t = text.lower()
    if re.search(r"\bhybrid\b", t):
        return 'Hybrid'
    if re.search(r"\belectric|ev\b", t):
        return 'Electric'
    if re.search(r"\bdiesel\b", t):
        return 'Diesel'
    if re.search(r"\bcng\b", t):
        return 'CNG'
    return 'Petrol'


def parse_text_record(text: str) -> Dict[str, Optional[object]]:
    out: Dict[str, Optional[object]] = {
        'make': None, 'model': None, 'variant': None, 'year': None,
        'condition': None, 'location': None, 'price_pkr': None,
        'engine_cc': None, 'color': None, 'mileage_km': None,
        'transmission': None, 'fuel_type': None, 'body_type': None,
    }
    if not text:
        return out
    t = str(text)
    my = None
    m = year_re.search(t)
    if m:
        try:
            yv = int(m.group(1))
            if 1980 <= yv <= 2030:
                my = yv
        except Exception:
            pass
    out['year'] = my
    out['price_pkr'] = parse_price_to_pkr(t)
    m = cc_re.search(t)
    if m:
        try:
            out['engine_cc'] = int(m.group(1))
        except Exception:
            pass
    m = km_re.search(t)
    if m:
        val = m.group(1).replace(',', '')
        try:
            out['mileage_km'] = int(float(val))
        except Exception:
            pass
    col = extract_simple_token(t, colors)
    if col:
        out['color'] = 'Gray' if col == 'grey' else col.title()
    fu = extract_simple_token(t, fuels)
    if fu:
        out['fuel_type'] = fu.title()
    tr = extract_simple_token(t, transmissions)
    if tr:
        out['transmission'] = 'Automatic' if tr in {'automatic','auto','cvt','ags'} else tr.title()
    cd = extract_simple_token(t, conditions)
    if cd:
        out['condition'] = cd.title()
    m = city_in_re.search(t)
    if m:
        out['location'] = m.group(1).strip().title()
    mmv = parse_make_model_variant(t.split('.')[:1][0], out['year'])
    out.update(mmv)
    if not out['body_type']:
        out['body_type'] = infer_body_type(out.get('make'), out.get('model'), t)
    if not out['fuel_type']:
        out['fuel_type'] = infer_fuel_type(t, out.get('make'), out.get('model'))
    return out


__all__ = [
    'parse_text_record', 'parse_price_to_pkr', 'infer_body_type', 'infer_fuel_type'
]
