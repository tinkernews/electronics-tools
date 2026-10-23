"""The formulas behind the free bench calculators at tinkernews.com/tools.

Extracted so they can be used in scripts, test rigs and firmware build tooling
without opening a browser. No dependencies, no telemetry, MIT licensed.

Everything here is the standard engineering arithmetic, and every function is
tested against the numbers the interactive versions print, so the two cannot
drift apart silently.
"""

E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3,
       3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]


def smd_resistor(code):
    """Decode a chip resistor code into ohms.

    Three digits (103) are E24, two significant figures plus a zero count.
    Four digits (1002) are E96, three significant figures plus a zero count.
    R, K and M stand in for the decimal point and the unit, because a full stop
    does not survive on a 1 mm package. 0 and 000 are a zero ohm jumper, which
    this returns as 0.0.

    >>> smd_resistor("103")
    10000.0
    >>> smd_resistor("4R7")
    4.7
    >>> smd_resistor("1K5")
    1500.0
    """
    s = str(code).strip().upper()
    if not s or not any(c.isdigit() for c in s):
        raise ValueError(f"not a resistor code: {code!r}")
    if s in ("0", "000", "0000"):
        return 0.0
    for marker, scale in (("R", 1.0), ("K", 1e3), ("M", 1e6)):
        if marker in s:
            head, _, tail = s.partition(marker)
            digits = (head or "0") + "." + (tail or "0")
            return round(float(digits) * scale, 6)
    if not s.isdigit():
        raise ValueError(f"not a resistor code: {code!r}")
    if len(s) == 3:
        return float(s[:2]) * (10 ** int(s[2]))
    if len(s) == 4:
        return float(s[:3]) * (10 ** int(s[3]))
    raise ValueError(f"unexpected code length: {code!r}")


def nearest_e24(value):
    """The nearest standard E24 value, in both directions.

    Returns (lower, upper). Both are parts you can buy anywhere.

    >>> nearest_e24(150)
    (150.0, 150.0)
    >>> nearest_e24(13)
    (12.0, 13.0)
    """
    if value <= 0:
        raise ValueError("value must be positive")
    decade = 10 ** (len(str(int(value))) - 1) if value >= 1 else 1.0
    while decade > value:
        decade /= 10
    while decade * 10 <= value:
        decade *= 10
    candidates = sorted({round(m * decade, 6) for m in E24}
                        | {round(m * decade * 10, 6) for m in E24}
                        | {round(m * decade / 10, 6) for m in E24})
    lower = max([c for c in candidates if c <= value], default=candidates[0])
    upper = min([c for c in candidates if c >= value], default=candidates[-1])
    return lower, upper


def led_resistor(supply_v, forward_v, current_ma):
    """Series resistor for an LED, plus the heat it has to survive.

    R = (Vs - Vf) / I. The power rating to buy is at least double the
    dissipation, so the part runs cool.

    >>> led_resistor(5, 2, 20)["resistor"]
    150.0
    """
    if current_ma <= 0:
        raise ValueError("current must be positive")
    drop = supply_v - forward_v
    if drop <= 0:
        raise ValueError("supply must exceed the LED forward voltage")
    amps = current_ma / 1000.0
    exact = drop / amps
    lower, upper = nearest_e24(exact)
    # pick the E24 value that lands closest to the target current without
    # overshooting it badly; a slightly high resistance is the safe direction.
    pick = upper if upper / exact <= 1.05 else lower
    actual_ma = drop / pick * 1000.0
    watts = drop * amps
    return {
        "resistor": round(pick, 6),
        "exact": round(exact, 6),
        "current_ma": round(actual_ma, 3),
        "dissipation_w": round(watts, 4),
        "buy_rating_w": round(max(watts * 2, 0.25), 3),
    }


def trace_width_amps(current_a, temp_rise_c=10.0, copper_oz=1.0, external=True):
    """IPC-2221 nominal curve: minimum trace width for a current.

    width(mil) = (I / (k * dT^0.44))^(1/0.725) / (copper_oz * 1.378)

    k is 0.048 for an external layer and 0.024 for an internal one, and the
    1.378 mil factor is the thickness of one ounce of copper. Returns mils and
    millimetres. Steady state only: inrush is a different problem.

    >>> trace_width_amps(1)["width_mil"]
    11.8
    """
    if current_a <= 0:
        raise ValueError("current must be positive")
    if temp_rise_c <= 0:
        raise ValueError("temperature rise must be positive")
    k = 0.048 if external else 0.024
    area_mil2 = (current_a / (k * temp_rise_c ** 0.44)) ** (1 / 0.725)
    width_mil = area_mil2 / (copper_oz * 1.378)
    return {
        "area_mil2": round(area_mil2, 2),
        "width_mil": round(width_mil, 1),
        "width_mm": round(width_mil * 0.0254, 3),
        "layer": "external" if external else "internal",
    }
