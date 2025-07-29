# Accurate Hijri

📅 **Accurate Hijri–Gregorian Converter**  
A Python package for accurate two-way conversion between Gregorian and Hijri dates using the Umm al-Qura calendar dataset.

---

## ✨ Features

- ✅ Convert **Gregorian to Hijri**
- ✅ Convert **Hijri to Gregorian**
- 📚 Based on **official Umm al-Qura** calendar data
- 🔁 Supports **round-trip conversion**
- ⚠️ Handles **invalid or out-of-range** dates with clear errors

---

## 📦 Installation

First, ensure you have Python 3.7+ and `pip` installed:

```bash
pip install accurate-hijri
from accurate_hijri import AccurateHijriConverter, HijriDate
from datetime import datetime

# Load the converter
converter = AccurateHijriConverter()

# Convert Gregorian → Hijri
g_date = datetime(2024, 4, 10)
hijri = converter.to_hijri(g_date)
print(hijri)  # Output: 1 Shawwal 1445 AH

# Convert Hijri → Gregorian
h_date = HijriDate(1445, 10, 1)
gregorian = converter.to_gregorian(h_date)
print(gregorian.date())  # Output: 2024-04-10
```

🙏 Acknowledgments
Umm al-Qura Calendar Data: Based on the official Saudi calendar dataset.

Thanks to the Python open-source community for the incredible tools.

Heartfelt gratitude to my mother and sister for their constant encouragement, love, and support throughout this project.

📄 License
Licensed under the MIT License.
