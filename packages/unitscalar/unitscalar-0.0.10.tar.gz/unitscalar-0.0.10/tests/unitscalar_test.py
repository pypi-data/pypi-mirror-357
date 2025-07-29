import unittest
from unitscalar import UnitScalar as us


class UnitScalarTest(unittest.TestCase):
    def setUp(self):
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    def test_unit_parsing(self):
        # Trivial unit
        self.assertEqual(us.UnitScalar(3.14, "m").__str__(), "3.14 m")
        self.assertEqual(us.UnitScalar(3.14, "1/m").__str__(), "3.14 1/m")
        self.assertEqual(us.UnitScalar(3.14, "m/s").__str__(), "3.14 m/s")
        self.assertEqual(us.UnitScalar(3.14, "m/s2").__str__(), "3.14 m/s2")
        self.assertEqual(us.UnitScalar(3.14, "m2/s2").__str__(), "3.14 m2/s2")

        # Unit string parsing tests
        self.assertEqual(
            us.UnitScalar._parse_units("m"), ([us.UnitScalar.SimpleUnit("m", 1)], [], 1)
        )
        self.assertEqual(
            us.UnitScalar._parse_units("s"), ([us.UnitScalar.SimpleUnit("s", 1)], [], 1)
        )
        self.assertEqual(
            us.UnitScalar._parse_units("m2"),
            ([us.UnitScalar.SimpleUnit("m", 2)], [], 1),
        )
        self.assertEqual(
            us.UnitScalar._parse_units("m3"),
            ([us.UnitScalar.SimpleUnit("m", 3)], [], 1),
        )
        self.assertEqual(
            us.UnitScalar._parse_units("m22"),
            ([us.UnitScalar.SimpleUnit("m", 22)], [], 1),
        )
        self.assertEqual(
            us.UnitScalar._parse_units("m2 s4"),
            (
                [us.UnitScalar.SimpleUnit("m", 2), us.UnitScalar.SimpleUnit("s", 4)],
                [],
                1,
            ),
        )
        self.assertEqual(
            us.UnitScalar._parse_units("m s4"),
            (
                [us.UnitScalar.SimpleUnit("m", 1), us.UnitScalar.SimpleUnit("s", 4)],
                [],
                1,
            ),
        )
        self.assertEqual(
            us.UnitScalar._parse_units("1/m"),
            ([], [us.UnitScalar.SimpleUnit("m", 1)], 1),
        )
        self.assertEqual(
            us.UnitScalar._parse_units("1/mm"),
            ([], [us.UnitScalar.SimpleUnit("m", 1)], 1000),
        )
        self.assertEqual(
            us.UnitScalar._parse_units("mm/mm"),
            (
                [us.UnitScalar.SimpleUnit("m", 1)],
                [us.UnitScalar.SimpleUnit("m", 1)],
                1,
            ),
        )

    def test_unit_reduction(self):
        # Unit fraction reduction tests
        self.assertEqual(
            us.UnitScalar._reduce_units(
                [us.UnitScalar.SimpleUnit("m", 1)], [us.UnitScalar.SimpleUnit("m", 1)]
            ),
            ([], []),
        )
        self.assertEqual(
            us.UnitScalar._reduce_units(
                [us.UnitScalar.SimpleUnit("m", 2)], [us.UnitScalar.SimpleUnit("m", 1)]
            ),
            ([us.UnitScalar.SimpleUnit("m", 1)], []),
        )
        self.assertEqual(
            us.UnitScalar._reduce_units(
                [us.UnitScalar.SimpleUnit("m", 1)], [us.UnitScalar.SimpleUnit("m", 2)]
            ),
            ([], [us.UnitScalar.SimpleUnit("m", 1)]),
        )

    def test_arithmetic(self):
        # Equality testing
        self.assertNotEqual(us.UnitScalar(3.14, "m"), us.UnitScalar(3, "m"))
        self.assertNotEqual(us.UnitScalar(3.14, "m"), us.UnitScalar(3.14, "s"))
        self.assertEqual(us.UnitScalar(3.14, "m s"), us.UnitScalar(3.14, "s m"))

        # Basic arithmetic checkouts
        self.assertEqual(
            us.UnitScalar(3.14, "m") + us.UnitScalar(3.14, "m"),
            us.UnitScalar(6.28, "m"),
        )
        self.assertEqual(
            us.UnitScalar(3.14, "m") - us.UnitScalar(1.14, "m"), us.UnitScalar(2, "m")
        )
        self.assertEqual(
            us.UnitScalar(3.14, "m/s") * us.UnitScalar(3.14, "1/s"),
            us.UnitScalar(3.14**2, "m/s2"),
        )
        self.assertEqual(
            us.UnitScalar(3.14, "m/s") / us.UnitScalar(3.14, "1/s"),
            us.UnitScalar(1, "m"),
        )
        self.assertEqual(
            us.UnitScalar(3.14, "m/s") ** 2, us.UnitScalar(3.14**2, "m2/s2")
        )
        self.assertEqual(
            us.UnitScalar(3.14, "m/s2") ** 3, us.UnitScalar(3.14**3, "m3/s6")
        )
        self.assertEqual(us.UnitScalar(2.0, "") + 1, us.UnitScalar(3, ""))
        self.assertEqual(1 + us.UnitScalar(2.0, ""), us.UnitScalar(3, ""))
        self.assertEqual(us.UnitScalar(2.0, "") / 3, us.UnitScalar(2 / 3, ""))
        self.assertEqual(1 / us.UnitScalar(2.0, ""), us.UnitScalar(1 / 2, ""))

    def test_reformatting(self):
        # Verifying unit agreement between different units
        self.assertTrue(us.UnitScalar(1.0, "lbf").units_agree("kg m/s2"))
        self.assertTrue(us.UnitScalar(1.0, "kg m/s2").units_agree("lbf"))
        self.assertFalse(us.UnitScalar(1.0, "kg").units_agree("lbf"))

        # Verify converting to equivalent units
        self.assertEqual(us.UnitScalar(1.0, "uA").to_units("A"), 1e-6)
        self.assertAlmostEqual(us.UnitScalar(1.0, "lbf").to_units("N"), 4.44822162)
        with self.assertRaises(Exception):
            us.UnitScalar(1.0, "lbf").to_units("A")

        # Verify formatting in equivalent units
        self.assertEqual(
            us.UnitScalar(3141.59, "m/s").__format__("0.2f;km/s"), "3.14 km/s"
        )
        self.assertEqual(
            us.UnitScalar(3.14159, "kg").__format__("0.3f;lbm"), "6.926 lbm"
        )


if __name__ == "__main__":
    unittest.main()
