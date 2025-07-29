# -None*- coding: utf-8 -*-

"""
Tests for the infdate module
"""

import datetime
import math
import secrets
import unittest


import infdate


MAX_ORDINAL = datetime.date.max.toordinal()


def random_deterministic_date() -> infdate.Date:
    """Helper function: create a random deterministic Date"""
    return infdate.Date.fromordinal(secrets.randbelow(MAX_ORDINAL) + 1)


class VerboseTestCase(unittest.TestCase):
    """Testcase showinf maximum differences"""

    def setUp(self):
        """set maxDiff"""
        self.maxDiff = None  # pylint: disable=invalid-name ; name from unittest module


class Date(VerboseTestCase):
    """Date objects"""

    def test_max(self):
        """Date.max"""
        max_date = infdate.Date.max
        with self.subTest("ordinal"):
            self.assertEqual(max_date.toordinal(), math.inf)
        #
        with self.subTest("bool"):
            self.assertFalse(max_date)
        #
        for attribute in ("year", "month", "day"):
            with self.subTest("failure", attribute=attribute):
                self.assertRaisesRegex(
                    ValueError, "^Non-deterministic date$", getattr, max_date, attribute
                )
            #
        #
        with self.subTest("repr"):
            self.assertEqual(repr(max_date), "Date(inf)")
        #
        with self.subTest("isoformat"):
            self.assertEqual(max_date.isoformat(), "<inf>")
        #

    def test_min(self):
        """Date.min"""
        min_date = infdate.Date.min
        with self.subTest("ordinal"):
            self.assertEqual(min_date.toordinal(), -math.inf)
        #
        with self.subTest("bool"):
            self.assertFalse(min_date)
        #
        for attribute in ("year", "month", "day"):
            with self.subTest("failure", attribute=attribute):
                self.assertRaisesRegex(
                    ValueError, "^Non-deterministic date$", getattr, min_date, attribute
                )
            #
        #
        with self.subTest("repr"):
            self.assertEqual(repr(min_date), "Date(-inf)")
        #
        with self.subTest("isoformat"):
            self.assertEqual(min_date.isoformat(), "<-inf>")
        #

    def test_nan_init(self):
        """Try to initialize with NaN"""
        self.assertRaisesRegex(
            ValueError, "^Cannot instantiate from NaN$", infdate.Date, math.nan
        )

    def test_float_init(self):
        """Try to initialize with a regular float"""
        self.assertRaisesRegex(
            ValueError,
            "^Cannot instantiate from a regular deterministic float$",
            infdate.Date,
            12.345,
        )

    def test_arbitrary_date(self):
        """arbitrary date"""
        some_date = infdate.Date(2023, 5, 23)
        expected_ordinal = datetime.date(2023, 5, 23).toordinal()
        with self.subTest("ordinal"):
            self.assertEqual(some_date.toordinal(), expected_ordinal)
        #
        with self.subTest("bool"):
            self.assertTrue(some_date)
        #
        for attribute, expected_value in (("year", 2023), ("month", 5), ("day", 23)):
            with self.subTest(
                "success", attribute=attribute, expected_value=expected_value
            ):
                self.assertEqual(getattr(some_date, attribute), expected_value)
            #
        #
        with self.subTest("repr"):
            self.assertEqual(repr(some_date), "Date(2023, 5, 23)")
        #
        with self.subTest("isoformat"):
            self.assertEqual(some_date.isoformat(), "2023-05-23")
        #

    def test_replace(self):
        """.replace() method"""
        min_date = infdate.Date.min
        with self.subTest("failure"):
            self.assertRaisesRegex(
                ValueError, "^Non-deterministic date$", min_date.replace, month=6
            )
        #
        some_date = infdate.Date(1234, 5, 6)
        old_year = 1234
        old_month = 5
        old_day = 6
        for new_year in (1, 2000, 5000, 9999):
            with self.subTest("replaced", new_year=new_year):
                new_date = some_date.replace(year=new_year)
                self.assertEqual(new_date.year, new_year)
                self.assertEqual(new_date.month, old_month)
                self.assertEqual(new_date.day, old_day)
            #
        #
        for new_month in (1, 4, 7, 12):
            with self.subTest("replaced", new_month=new_month):
                new_date = some_date.replace(month=new_month)
                self.assertEqual(new_date.year, old_year)
                self.assertEqual(new_date.month, new_month)
                self.assertEqual(new_date.day, old_day)
            #
        #
        for new_day in (1, 10, 16, 31):
            with self.subTest("replaced", new_day=new_day):
                new_date = some_date.replace(day=new_day)
                self.assertEqual(new_date.year, old_year)
                self.assertEqual(new_date.month, old_month)
                self.assertEqual(new_date.day, new_day)
            #
        #

    def test_hashable(self):
        """hash(date_instance) capability; Date instances are usable as dict keys"""
        isaac = infdate.Date(1643, 1, 4)
        ada = infdate.Date(1815, 12, 10)
        birthdays = {isaac: "Newton", ada: "Lovelace"}
        self.assertEqual(birthdays[isaac], "Newton")
        self.assertEqual(birthdays[ada], "Lovelace")

    def test_sub_or_add_days(self):
        """date_instance +/- number of days capability"""
        bernoulli = infdate.Date(1655, 1, 6)
        self.assertEqual(bernoulli + 60, infdate.Date(1655, 3, 7))
        self.assertEqual(bernoulli - 60, infdate.Date(1654, 11, 7))
        self.assertEqual(bernoulli - math.inf, infdate.Date.min)
        self.assertEqual(bernoulli + math.inf, infdate.Date.max)
        self.assertEqual(infdate.Date.max - 1, infdate.Date.max)
        self.assertEqual(infdate.Date.max + 1, infdate.Date.max)
        self.assertEqual(infdate.Date.min - 1, infdate.Date.min)
        self.assertEqual(infdate.Date.min + 1, infdate.Date.min)
        self.assertEqual(infdate.Date.max - math.inf, infdate.Date.min)
        self.assertEqual(infdate.Date.max + math.inf, infdate.Date.max)
        self.assertEqual(infdate.Date.min - math.inf, infdate.Date.min)
        self.assertEqual(infdate.Date.min + math.inf, infdate.Date.max)
        self.assertRaises(ValueError, bernoulli.__add__, math.nan)
        self.assertRaises(ValueError, bernoulli.__sub__, math.nan)
        # Adding math.nan to or subtrating it from the infinity dates
        # does not raise an error because infinity is checked first,
        # before calculating a result
        self.assertEqual(infdate.Date.min + math.nan, infdate.Date.min)
        self.assertEqual(infdate.Date.max - math.nan, infdate.Date.max)

    def test_sub_date(self):
        """date_instance - date_instance capability"""
        chernobyl = infdate.Date(1986, 4, 26)
        fukushima = infdate.Date(2011, 3, 11)
        self.assertEqual(fukushima - chernobyl, 9085)
        self.assertEqual(chernobyl - fukushima, -9085)
        self.assertEqual(infdate.Date.max - fukushima, math.inf)
        self.assertEqual(chernobyl - infdate.Date.min, math.inf)
        self.assertEqual(infdate.Date.min - fukushima, -math.inf)
        self.assertEqual(chernobyl - infdate.Date.max, -math.inf)
        self.assertEqual(infdate.Date.min - infdate.Date.max, -math.inf)
        self.assertEqual(infdate.Date.max - infdate.Date.min, math.inf)
        # subtracting infinite dates from themselves results in NaN
        self.assertTrue(math.isnan(infdate.Date.max - infdate.Date.max))
        self.assertTrue(math.isnan(infdate.Date.min - infdate.Date.min))

    # pylint: disable=comparison-with-itself ; to show lt/gt ↔ le/ge difference

    def test_lt(self):
        """less than"""
        mindate = infdate.Date.min
        maxdate = infdate.Date.max
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(mindate < random_date)
                self.assertFalse(random_date < mindate)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date < maxdate)
                self.assertFalse(maxdate < random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date < random_date)
            #
        #

    def test_le(self):
        """less than or equal"""
        mindate = infdate.Date.min
        maxdate = infdate.Date.max
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(mindate <= random_date)
                self.assertFalse(random_date <= mindate)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date <= maxdate)
                self.assertFalse(maxdate <= random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date <= random_date)
            #
        #

    def test_gt(self):
        """greater than"""
        mindate = infdate.Date.min
        maxdate = infdate.Date.max
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(mindate > random_date)
                self.assertTrue(random_date > mindate)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date > maxdate)
                self.assertTrue(maxdate > random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date > random_date)
            #
        #

    def test_ge(self):
        """greater than or equal"""
        mindate = infdate.Date.min
        maxdate = infdate.Date.max
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(mindate >= random_date)
                self.assertTrue(random_date >= mindate)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date >= maxdate)
                self.assertTrue(maxdate >= random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date <= random_date)
            #
        #

    def test_ne(self):
        """not equal"""
        mindate = infdate.Date.min
        maxdate = infdate.Date.max
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(mindate != random_date)
                self.assertTrue(random_date != mindate)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date != maxdate)
                self.assertTrue(maxdate != random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date != random_date)
            #
        #

    def test_str(self):
        """hash(date_instance) capability; Date instances are usable as dict keys"""
        isaac = infdate.Date(1643, 1, 4)
        self.assertEqual(str(isaac), "1643-01-04")

    def test_today(self):
        """.today() classmethod"""
        today = datetime.date.today()
        self.assertEqual(
            infdate.Date.today(), infdate.Date(today.year, today.month, today.day)
        )
