from setuptools import setup, find_packages

setup(
    name="composite_silhouette",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "scipy",
        "matplotlib",
        "joblib>=1.4.2"
    ],
    python_requires=">=3.8",
    description="A robust clustering evaluation framework that combines micro- and macro-averaged silhouette scores into a composite metric using statistical weighting.",
    url="https://github.com/semoglou/composite_silhouette",  
    author="Angelos Semoglou",
    author_email="a.semoglou@outlook.com",
    license="MIT"
)
