import unittest

from tests.utils import TempEnv
from zekniri.doctor import run_doctor, generate_bug_report, DOCTOR_CHECKS


class DoctorTest(unittest.TestCase):
    def test_doctor_runs_without_crashing(self):
        with TempEnv():
            self.assertTrue(DOCTOR_CHECKS)
            run_doctor()

    def test_bug_report_written(self):
        with TempEnv() as t:
            path = generate_bug_report()
            self.assertTrue(path.is_file())
            self.assertIn("ZEKniri", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
