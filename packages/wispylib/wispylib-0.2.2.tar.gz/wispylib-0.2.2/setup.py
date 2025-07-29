from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='wispylib',
    version='0.2.2',
    description='A link scraping and redirect-checking utility',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Ryu saiki',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'tldextract',
    ],
    entry_points={
        'console_scripts': [
            'wispylib-cli=wispylib.core:cringio_cli',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
