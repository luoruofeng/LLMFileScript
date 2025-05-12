from setuptools import setup, find_packages

setup(
    name="llmfilescript",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyYAML>=6.0",
        "openai",
    ],
    tests_require=[
        "flake8>=6.1.0",
        "pytest>=8.0.0"
    ],
    entry_points={
        "console_scripts": [
            "lfs=main:main"
        ]
    },
    python_requires=">=3.11",
)