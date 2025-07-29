from setuptools import setup, find_packages

setup(
    name="cleanclassify",
    version="0.1",
    author="Safa Mahveen",
    author_email="thesafamahveen@gmail.com",
    description="A beginner-friendly Python Package to clean, classify, and visualize CSV data via a simple GUI.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SafaMahveen/cleanclassify.git",  
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas>=2.3.0",
        "numpy>=2.3.1",
        "matplotlib>=3.10.3",
        "scikit-learn>=1.7.0"
    ],
    entry_points={
        "console_scripts": [
            "cleanclassify=cleanclassify.__main__:launch_gui"
        ],
    },
    python_requires='>=3.8',
    license="MIT",
    keywords="machine-learning tkinter gui classification sklearn pandas csv"
)
