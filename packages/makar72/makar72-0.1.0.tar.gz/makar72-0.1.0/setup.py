from setuptools import setup, find_packages

setup(
    name="makar72",
    version="0.1.0",
    description="Че надо",
    author="Ваше Имя",
    packages=find_packages(),
    include_package_data=True,
    package_data={"makar72": ["3.txt", "4.txt", "5.txt"]},
    python_requires=">=3.7",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
