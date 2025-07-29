from setuptools import find_packages
from setuptools import setup


# with open("README.md", "r", encoding="utf-8") as f:
#    long_description = f.read()

setup(
    name="gifconverter_hsj",
    version="1.0.0",
    description="Test package for distribution",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    author="algento",
    author_email="tromberx@gmail.com",
    url="",
    download_url="",
    install_requires=["pillow"],
    include_package_data=True,
    packages=find_packages(),
    keywords=["GIFCONVERTER", "gifconverter"],
    python_requires=">=3",
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
