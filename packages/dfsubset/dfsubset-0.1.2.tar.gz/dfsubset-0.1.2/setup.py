from setuptools import setup, find_packages

setup(
    name="dfsubset",
    version="0.1.2",
    description="An R-style subset() function for pandas DataFrames.",
    author="Sambili Tonny",
    author_email="your_email@example.com",
    packages=find_packages(),
    install_requires=["pandas"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)