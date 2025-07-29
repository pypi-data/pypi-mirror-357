from setuptools import setup, find_packages

setup(
    name="twoja-nazwa-pakietu",
    version="0.1.0",
    author="Twoje Imię",
    author_email="twoj.email@example.com",
    description="Krótki opis twojej biblioteki",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        'my3dengine': ['sdl2.dll'],
    },
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)