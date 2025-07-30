from setuptools import setup, find_packages

setup(
    name="volleyball-prediction",
    version="0.1.7",  # versiyonu artır!
    author="Selinay Deniz",
    description="Python package to predict women's volleyball match results.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/selinydeniz/volleyball-prediction",
    project_urls={
        "Bug Tracker": "https://github.com/selinydeniz/volleyball-prediction/issues",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,  # HTML dahil etmek için şart
    install_requires=[
        "fastapi", "pandas", "joblib", "scikit-learn", "uvicorn", "pydantic"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)


