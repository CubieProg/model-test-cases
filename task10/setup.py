from setuptools import setup, find_packages

setup(
    name="graphcoloring",
    version="0.0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "matplotlib>=3.5.2",
        "networkx>=2.8.4",
        "numpy>=1.24.4",
        "plotly>=5.11.0",
        "scipy>=1.15.1"
    ]
)