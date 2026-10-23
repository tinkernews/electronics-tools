"""Tests pinned to the numbers the live calculators print.

If these fail, the library and tinkernews.com/tools have drifted apart, and the
library is the one that is probably wrong.
"""
import unittest

from calculators import (led_resistor, nearest_e24, smd_resistor,
                        trace_width_amps)


class TestSMD(unittest.TestCase):
    def test_three_digit(self):
        self.assertEqual(smd_resistor("103"), 10000.0)
        self.assertEqual(smd_resistor("102"), 1000.0)
        self.assertEqual(smd_resistor("220"), 22.0)
        self.assertEqual(smd_resistor("101"), 100.0)
        self.assertEqual(smd_resistor("104"), 100000.0)
        self.assertEqual(smd_resistor("105"), 1000000.0)

    def test_four_digit_e96(self):
        self.assertEqual(smd_resistor("1002"), 10000.0)

    def test_decimal_markers(self):
        self.assertEqual(smd_resistor("4R7"), 4.7)
        self.assertEqual(smd_resistor("R33"), 0.33)
        self.assertEqual(smd_resistor("1K5"), 1500.0)
        self.assertEqual(smd_resistor("2M2"), 2200000.0)

    def test_jumper(self):
        self.assertEqual(smd_resistor("0"), 0.0)
        self.assertEqual(smd_resistor("000"), 0.0)

    def test_rejects_junk(self):
        with self.assertRaises(ValueError):
            smd_resistor("abc")
        with self.assertRaises(ValueError):
            smd_resistor("12345")


class TestE24(unittest.TestCase):
    def test_exact_standard_value(self):
        self.assertEqual(nearest_e24(150), (150.0, 150.0))

    def test_brackets_between_standards(self):
        lower, upper = nearest_e24(13)
        self.assertLessEqual(lower, 13)
        self.assertGreaterEqual(upper, 13)

    def test_decades(self):
        self.assertEqual(nearest_e24(1000), (1000.0, 1000.0))


class TestLED(unittest.TestCase):
    def test_the_worked_example_on_the_page(self):
        # 5 V supply, 2 V LED, 20 mA = 150 ohms, 0.06 W, buy 0.25 W.
        r = led_resistor(5, 2, 20)
        self.assertEqual(r["resistor"], 150.0)
        self.assertEqual(r["exact"], 150.0)
        self.assertAlmostEqual(r["current_ma"], 20.0, places=1)
        self.assertAlmostEqual(r["dissipation_w"], 0.06, places=3)
        self.assertEqual(r["buy_rating_w"], 0.25)

    def test_twelve_volt_build(self):
        # 500 ohms is the exact answer and is not an E24 value, so the nearest
        # purchasable part is 510, which lands at 19.6 mA rather than 20.
        r = led_resistor(12, 2, 20)
        self.assertEqual(r["exact"], 500.0)
        self.assertEqual(r["resistor"], 510.0)
        self.assertAlmostEqual(r["current_ma"], 19.6, places=1)
        self.assertAlmostEqual(r["dissipation_w"], 0.2, places=3)

    def test_rejects_impossible_supply(self):
        with self.assertRaises(ValueError):
            led_resistor(2, 3, 20)


class TestTraceWidth(unittest.TestCase):
    def test_the_worked_example_on_the_page(self):
        # 1 A, 10 C rise, 1 oz, external = 16.3 mil2, 11.8 mil, 0.3 mm.
        r = trace_width_amps(1)
        self.assertAlmostEqual(r["area_mil2"], 16.3, places=1)
        self.assertEqual(r["width_mil"], 11.8)
        self.assertEqual(r["width_mm"], 0.3)
        self.assertEqual(r["layer"], "external")

    def test_internal_layers_need_more_copper(self):
        ext = trace_width_amps(1, external=True)
        internal = trace_width_amps(1, external=False)
        self.assertGreater(internal["width_mil"], ext["width_mil"])
        # k doubles, so the copper area scales by 2^(1/0.725). Compare the
        # unrounded area, since width_mil carries one decimal place.
        self.assertAlmostEqual(internal["area_mil2"] / ext["area_mil2"],
                               2 ** (1 / 0.725), places=2)

    def test_copper_weight(self):
        one = trace_width_amps(1, copper_oz=1)["width_mil"]
        two = trace_width_amps(1, copper_oz=2)["width_mil"]
        self.assertAlmostEqual(one / two, 2.0, places=2)

    def test_rejects_zero_current(self):
        with self.assertRaises(ValueError):
            trace_width_amps(0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
