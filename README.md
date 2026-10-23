# electronics-tools

The arithmetic behind the free bench calculators at
[tinkernews.com/tools](https://www.tinkernews.com/tools?utm_source=github&utm_medium=readme&utm_campaign=tools-lib),
as a small dependency free Python module.

No network calls, no telemetry, MIT licensed. Use it in scripts, test rigs,
production test code or firmware build tooling without opening a browser.

```python
from calculators import smd_resistor, led_resistor, trace_width_amps

smd_resistor("103")        # 10000.0   (E24, three digit)
smd_resistor("4R7")        # 4.7       (R is the decimal point)
led_resistor(5, 2, 20)     # 150 ohm, 0.06 W, buy a 0.25 W part
trace_width_amps(1)        # 11.8 mil, 0.3 mm of 1 oz copper, external layer
```

## What is in here

| Function | Does | Notes |
|---|---|---|
| `smd_resistor(code)` | chip resistor code to ohms | three digit E24, four digit E96, R/K/M decimal markers, `0` and `000` as a zero ohm jumper |
| `nearest_e24(value)` | nearest purchasable E24 value | returns both directions, lower and upper |
| `led_resistor(supply, forward, mA)` | series resistor, actual current, dissipation, rating to buy | picks the E24 value closest to the target, erring high |
| `trace_width_amps(current, dT, copper_oz, external)` | IPC-2221 minimum trace width | steady state only, mils and millimetres |

## Why the numbers can be trusted

Every function is tested against the values the interactive versions on the site
print, so the library and the web tool cannot drift apart silently:

```
python -m unittest test_calculators -v
```

A worked example from the tests: a 2 V LED on 5 V at 20 mA gives exactly 150
ohm, 0.06 W of heat, and a 0.25 W part. On 12 V the exact answer is 500 ohm,
which is **not** an E24 value, so the library returns 510 ohm at 19.6 mA rather
than pretending a 500 is on the shelf.

## Deliberately not included

- **Wire gauge and voltage drop.** The drop depends on a resistance table plus a
  round trip assumption, and getting either wrong is worse than not shipping it.
  The interactive version carries the table.
- **Battery life.** Duty cycle assumptions, not arithmetic.
- **Anything with a datasheet in it.** Those change between board revisions.

## Licence

MIT, see LICENSE. The pinout charts and the interactive tools stay on
[tinkernews.com/tools](https://www.tinkernews.com/tools), free and without a
signup.
