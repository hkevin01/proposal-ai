from setuptools import setup, find_packages

setup(
    name="proposal-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "pyqt5",
        "spacy",
        "fpdf",
        "python-docx",
        "matplotlib",
        "pandas",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "proposal-ai=src.main:main"
        ]
    },
    author="hkevin01",
    description="AI-powered proposal submission and analytics platform",
    url="https://github.com/hkevin01/proposal-ai",
)
