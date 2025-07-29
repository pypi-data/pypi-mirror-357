from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vinzy_automl",
    version="1.0.0",
    author="Vinayak Bhosale",
    description="Automated Machine Learning package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vinayak-97/vinzy_automl",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        'numpy>=1.20.0',
        'pandas>=1.0.0',
        'scikit-learn>=1.0.0',
        'matplotlib>=3.5.0',
    ],
    extras_require={
        'full': [
            'xgboost>=1.5.0',
            'lightgbm>=3.3.0',
            'catboost>=1.0.0',
        ]
    },
)