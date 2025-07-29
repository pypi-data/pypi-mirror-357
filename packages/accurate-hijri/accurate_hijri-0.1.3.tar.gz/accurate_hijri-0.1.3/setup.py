from setuptools import setup, find_packages

setup(
    name="accurate-hijri",
    version="0.1.3",
    author="Samreen Kazi",
    description="Accurate Hijri-Gregorian converter using Umm al-Qura calendar data",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Samreen-Kazi/accurate-hijri",  # Change this later
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.7',
)
