import os.path
import pathlib
from setuptools import setup, find_packages

CURRENT_DIR = pathlib.Path(__file__).parent
readme_file = CURRENT_DIR / "README.md"
changelog_file = CURRENT_DIR / "CHANGELOG.md"

# Combine README and CHANGELOG if both exist
long_description = ""
if readme_file.exists():
    long_description += readme_file.read_text(encoding="utf-8")

if changelog_file.exists():
    long_description += "\n\n" + changelog_file.read_text(encoding="utf-8")

def get_dependencies():
    return ["requests", "setuptools", "peewee", "mysql-connector-python"]


setup(
    name='exsited',
    version='1.0.13',
    description='Exsited SDK',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ashiq Rahman',
    author_email='ashiq@webalive.com.au',
    url='https://github.com/exsited/exsited-python',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=get_dependencies(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    project_urls={
        'Documentation': 'https://stageexsited.mywebcommander.com/exsited-sdk-introduction',
    },
)