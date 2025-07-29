from setuptools import setup, find_packages

setup(
    name="parametric-uhpc",
    version="1.0.0",
    description="Parametric model for UHPC flexural limit-state analysis",
    author="Devansh Patel",
    author_email="your_email@example.com",
    url="https://github.com/dpatel52/UHPC-HRC-limitstates",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "openpyxl"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    include_package_data=True,
)
