from setuptools import setup, find_packages
import os

# Read version from __version__.py
version_contents = {}
with open(os.path.join("albanianlanguage", "__version__.py"), encoding="utf-8") as f:
    exec(f.read(), version_contents)

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="albanianlanguage",
    version=version_contents["__version__"],
    packages=find_packages(),
    install_requires=[],
    author="Florijan Qosja",
    author_email="florijanqosja@gmail.com",
    description="A comprehensive package for the Albanian language processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/florijanqosja/albanianlanguage",
    project_urls={
        "Bug Tracker": "https://github.com/florijanqosja/albanianlanguage/issues",
        "Documentation": "https://github.com/florijanqosja/albanianlanguage",
        "Source Code": "https://github.com/florijanqosja/albanianlanguage",
    },
    package_data={"albanianlanguage": ["data/*.csv"]},
    include_package_data=True,
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="albanian, nlp, language-processing, linguistics",
)
