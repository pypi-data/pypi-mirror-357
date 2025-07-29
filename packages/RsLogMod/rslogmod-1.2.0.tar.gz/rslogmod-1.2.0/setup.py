from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="RsLogMod",
    version="1.2.0",
    description="A versatile logging module for Python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="D-3-X",
    author_email="felix.dxlan@gmail.com",
    url="https://github.com/D-3-X/RsLogMod/",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    license="MIT",
    keywords="logging, log rotation, python logging, programmable customization",
    project_urls={
        "Bug Tracker": "https://github.com/D-3-X/RsLogMod/issues",
        "Documentation": "https://github.com/D-3-X/RsLogMod#readme",
        "Source Code": "https://github.com/D-3-X/RsLogMod",
    },
    package_data={
        "RsLogMod": ["configs/*.json"],
    }
)
