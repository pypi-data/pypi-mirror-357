from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='htyy',
    version='0.0.8',
    description='htyy',
    long_description=long_description,
    author='huang yi yi',
    author_email='363766687@qq.com',
    packages=find_packages(),
    package_data={
        "htyy":["*.pyd","*.pyi"],
    },
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        "watchdog",
        "paramiko",
        "pycryptodome",
        "pywin32",
        "rich",
        "plyer",
        "mpmath",
        "miniaudio",
        "argostranslate",
        "googletrans",
        "pyautogui",
        "py7zr",
        "cryptography",
    ],
)