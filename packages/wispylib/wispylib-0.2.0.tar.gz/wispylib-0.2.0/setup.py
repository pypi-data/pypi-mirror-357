from setuptools import setup, find_packages

setup(
    name='wispylib',
    version='0.2.0',
    description='A link scraping and redirect-checking utility',
    author='Ryu saiki',
    author_email='you@none.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
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
