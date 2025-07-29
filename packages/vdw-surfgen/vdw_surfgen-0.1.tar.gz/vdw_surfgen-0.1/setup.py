from setuptools import setup, find_packages

setup(
    name="vdw-surfgen",
    version="0.1",
    packages=find_packages(),
    install_requires=["numpy", "matplotlib"],
    entry_points={
        "console_scripts": [
            "vsg=vdw_surfgen.cli:cli_entry",
        ]
    },
    author="Stephen O. Ajagbe",
    description="Generate van der Waals surface points from XYZ molecules",
    python_requires=">=3.7",
)
