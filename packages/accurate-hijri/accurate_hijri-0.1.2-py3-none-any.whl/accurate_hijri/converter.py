import csv
from datetime import datetime, timedelta
import importlib.resources

HIJRI_MONTHS = [
    "", "Muharram", "Safar", "Rabi al-Awwal", "Rabi al-Thani", "Jumada al-Awwal", "Jumada al-Thani",
    "Rajab", "Sha'ban", "Ramadan", "Shawwal", "Dhul-Qa'dah", "Dhul-Hijjah"
]

class HijriDate:
    def __init__(self, year, month, day):
        if not (1 <= month <= 12):
            raise ValueError("Hijri month must be between 1 and 12")
        if not (1 <= day <= 30):
            raise ValueError("Hijri day must be between 1 and 30")

        self.year = year
        self.month = month
        self.day = day

    def __repr__(self):
        return f"HijriDate({self.year}, {self.month}, {self.day})"

    def __str__(self):
        return f"{self.day} {HIJRI_MONTHS[self.month]} {self.year} AH"

    def __eq__(self, other):
        return (
            isinstance(other, HijriDate) and
            self.year == other.year and
            self.month == other.month and
            self.day == other.day
        )

class AccurateHijriConverter:
    def __init__(self):
        self.hijri_data = []

        with importlib.resources.files("accurate_hijri.data").joinpath("umm_al_qura.csv").open("r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                gy = int(row["gy"])
                gm = int(row["gm"])
                gd = int(row["gd"])
                g_date = datetime(gy, gm, gd)

                self.hijri_data.append({
                    "gregorian_start": g_date,
                    "hijri_year": int(row["hy"]),
                    "hijri_month": int(row["hm"]),
                    "hijri_day": int(row["hd"])
                })

    def to_hijri(self, gregorian_date):
        for row in reversed(self.hijri_data):
            if gregorian_date >= row["gregorian_start"]:
                delta = (gregorian_date - row["gregorian_start"]).days
                day = row["hijri_day"] + delta
                month = row["hijri_month"]
                year = row["hijri_year"]

                # Rough handling for overflow (basic assumption: 30 days/month)
                while day > 30:
                    day -= 30
                    month += 1
                    if month > 12:
                        month = 1
                        year += 1

                return HijriDate(year, month, day)

        raise ValueError("Date out of supported range")

    def to_gregorian(self, hijri_date):
        for row in self.hijri_data:
            if (row["hijri_year"] == hijri_date.year and
                row["hijri_month"] == hijri_date.month and
                row["hijri_day"] == 1):

                delta_days = hijri_date.day - 1
                return row["gregorian_start"] + timedelta(days=delta_days)

        raise ValueError("Hijri date not found in dataset or out of range")
