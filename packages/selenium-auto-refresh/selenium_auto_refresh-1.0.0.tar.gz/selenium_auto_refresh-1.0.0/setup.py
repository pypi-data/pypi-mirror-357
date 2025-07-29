from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="selenium-auto-refresh",
    version="1.0.0",
    author="lalitpal",
    author_email="happytaak8@gmail.com",
    description="Automatically refresh Selenium Chrome tabs at specified intervals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/selenium-auto-refresh",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No dependencies needed - works with any driver
    ],
    extras_require={
        "selenium": ["selenium>=3.141.0"],
        "seleniumbase": ["seleniumbase"],
        "undetected": ["undetected-chromedriver"],
    },
    keywords="selenium chrome refresh automation testing webdriver",
)