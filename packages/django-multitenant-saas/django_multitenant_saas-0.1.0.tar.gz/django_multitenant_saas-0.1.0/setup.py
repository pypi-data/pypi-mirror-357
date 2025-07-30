import pathlib
from setuptools import setup, find_packages

# Get the long description from README.md
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="django-multitenant-saas",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="A plug-and-play multi-tenancy package for Django SaaS applications.",
    long_description=README,
    long_description_content_type='text/markdown',
    author="Pranav Dixit",
    author_email="pranavdixit20@gmail.com",
    install_requires=[
        "Django>=3.2",
    ],
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
