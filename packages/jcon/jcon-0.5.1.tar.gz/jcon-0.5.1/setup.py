from setuptools import setup, find_packages # type: ignore

setup(
    name='jcon',
    version='0.5.1',
    description='Python package to move Windows desktop icons',
    author='Jett S',
    author_email='your.email@example.com',
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Utilities',
    ],
)
