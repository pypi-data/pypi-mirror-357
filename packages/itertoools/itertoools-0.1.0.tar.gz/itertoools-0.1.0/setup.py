from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="itertoools",
    version="0.1.0",
    author="HIOL",  # Замените на ваше имя
    author_email="hiol.dev@gmail.com",  # Замените на ваш email
    description="Набор функций для решения задач по теории вероятностей",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nikakimvv/exam_teorver",  # Замените на ваш GitHub
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "sympy",
        "scipy",
        "numpy",
        "fractions",
    ],
) 