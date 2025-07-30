from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="multiserviciosweb",
    version="1.1.1",
    author="Edson Burgos",
    author_email="edsonburgosmacedo@gmail.com",
    description="Validate, calculate and obtain CURP information in México.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EdsonBurgosMsWeb/valida-curp-client-py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    keywords="valida curp méxico client api",
    project_urls={
        "Bug Reports": "https://github.com/EdsonBurgosMsWeb/valida-curp-client-py/issues",
        "Source": "https://github.com/EdsonBurgosMsWeb/valida-curp-client-py",
        "Homepage": "https://valida-curp.com.mx/",
        "documentation": "https://api.valida-curp.com.mx/documentacion/",
    },
)