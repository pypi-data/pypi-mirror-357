from setuptools import setup, find_packages

setup(
    name="smartenforcement",
    version="0.0.1",
    author="",
    author_email="",
    description="A placeholder for a project in planning. This package reserves the namespace for future development.",
    long_description="A placeholder package that reserves the PyPI namespace for future development.",
    long_description_content_type="text/plain",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
)