import pytest
from accurate_hijri.converter import AccurateHijriConverter, HijriDate
from datetime import datetime

# Load once per module
converter = AccurateHijriConverter("accurate_hijri/data/umm_al_qura.csv")

def test_round_trip_conversion():
    g_date = datetime(2024, 4, 10)
    h_date = converter.to_hijri(g_date)
    g_back = converter.to_gregorian(h_date)
    assert abs((g_date - g_back).days) <= 1

def test_known_date():
    g_date = datetime(2025, 6, 21)
    h_date = converter.to_hijri(g_date)
    assert h_date == HijriDate(1446, 12, 25)

def test_multiple_round_trips():
    dates = [
        datetime(2023, 1, 1),
        datetime(2024, 12, 31),
        datetime(2025, 3, 15),
        datetime(2020, 5, 24)
    ]
    for g_date in dates:
        h = converter.to_hijri(g_date)
        g_back = converter.to_gregorian(h)
        assert abs((g_date - g_back).days) <= 1

def test_invalid_hijri_month():
    with pytest.raises(ValueError, match="Hijri month must be between 1 and 12"):
        HijriDate(1445, 13, 10)

def test_invalid_hijri_day():
    with pytest.raises(ValueError, match="Hijri day must be between 1 and 30"):
        HijriDate(1445, 10, 35)

def test_out_of_range_gregorian():
    with pytest.raises(ValueError, match="Gregorian date is out of the supported range"):
        converter.to_hijri(datetime(1800, 1, 1))

def test_missing_hijri_date():
    # Definitely out of range in Umm al-Qura
    fake_hijri = HijriDate(1600, 1, 1)
    with pytest.raises(ValueError, match="Hijri date not found in dataset"):
        converter.to_gregorian(fake_hijri)
