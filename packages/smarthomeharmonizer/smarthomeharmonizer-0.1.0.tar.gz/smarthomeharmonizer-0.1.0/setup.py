"""Setup configuration for SmartHomeHarmonizer."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read version
exec(open('smarthomeharmonizer/__version__.py').read())

setup(
    name='smarthomeharmonizer',
    version=__version__,
    author='Praveen Chinnusamy',
    author_email='praveenchinnusamy@gmail.com',
    description='A GenAI assistant-enabled Python framework for bridging IoT devices with voice assistants',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cppraveen/SmartHomeHarmonizer',
    packages=find_packages(exclude=['tests*', 'docs*', 'examples*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Home Automation',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    install_requires=[
        'Flask>=2.0.0',
        'requests>=2.25.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov>=4.0',
            'pytest-flask>=1.2',
            'flake8>=6.0',
            'black>=23.0',
            'mypy>=1.0',
            'sphinx>=6.0',
            'tox>=4.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'smarthomeharmonizer=smarthomeharmonizer.cli:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/cppraveen/SmartHomeHarmonizer/issues',
        'Source': 'https://github.com/cppraveen/SmartHomeHarmonizer',
        'Documentation': 'https://smarthomeharmonizer.readthedocs.io',
    },
)
