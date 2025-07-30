from setuptools import setup, find_packages

setup(
    name='agvd',
    version='0.1.2',
    description='AGVD Variant Query Command Line Tool',
    author='WMudaki',
    author_email='wilson@mudaki.co.ke',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/wmudaki/agvdPy',
    packages=find_packages(),
    py_modules=['agvd', 'exceptions', 'query', 'cli', 'utils', 'core'],
    install_requires=[
        'pysam',
        'tqdm',
        'requests',
        'pandas',
        'openpyxl'  # for Excel file support
    ],
    entry_points={
        'console_scripts': [
            'agvd=cli:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
