import unittest
from pisense.database.validate import validate_value, ValidationError


class TestValidateValue(unittest.TestCase):

    def test_validate_int(self):
        self.assertIsNone(validate_value("42", "INT"))

        with self.assertRaises(ValidationError):
            validate_value("abc", "INT")

    def test_validate_decimal(self):
        self.assertIsNone(validate_value("3.14", "DECIMAL"))
        self.assertIsNone(validate_value("10", "DECIMAL"))

        with self.assertRaises(ValidationError):
            validate_value("hello", "DECIMAL")

    def test_validate_varchar(self):
        self.assertIsNone(validate_value("Hello", "VARCHAR(10)"))

        with self.assertRaises(ValidationError):
            validate_value("Too long here", "VARCHAR(5)")

    def test_validate_date(self):
        self.assertIsNone(validate_value("2026-02-20", "DATE"))

        with self.assertRaises(ValidationError):
            validate_value("20-02-2026", "DATE")

    def test_validate_time(self):
        self.assertIsNone(validate_value("14:30:00", "TIME"))

        with self.assertRaises(ValidationError):
            validate_value("2:30 PM", "TIME")

    def test_validate_bool(self):
        self.assertIsNone(validate_value(True, "BOOL"))
        self.assertIsNone(validate_value(False, "BOOL"))

        with self.assertRaises(ValidationError):
            validate_value("notabool", "BOOL")

if __name__ == "__main__":
    unittest.main()