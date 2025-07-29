from setuptools import setup, find_packages

setup(
    name="cleanslay",
    version="0.1.0",
    description="Safe JSON serializer for complex Python objects (Pydantic, Pandas, NumPy, etc.)",
    author="Pragman",
    author_email="a@staphi.com",
    url="https://github.com/grakn/cleanslay",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    extras_require={
        "test": [
            "pytest",
            "numpy",
            "pandas",
            "pydantic",
        ]
    },
)
