from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jcon",
    version="0.5.8",
    author="Jett S",
    author_email="fallinganvil8@gmail.com",
    description="Move Windows desktop icons programmatically in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",  # <- this tells PyPI to render Markdown
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
