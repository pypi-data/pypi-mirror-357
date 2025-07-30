from setuptools import setup, find_packages

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setup(
    name="Bruce_li_pro",
    version="0.0.1",
    author="Bruce Li",
    author_email="bruce.li@example.com",
    description="高效数据处理与API集成工具库",

    long_description_content_type="text/markdown",
    url="https://github.com/bruce-li/Bruce_li_pro",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "pandas>=1.0",
        "numpy>=1.20",
        "requests>=2.25",
        "matplotlib>=3.0"
    ],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0", "sphinx>=5.0"],
        "full": ["seaborn>=0.11", "plotly>=5.0"]
    },
)