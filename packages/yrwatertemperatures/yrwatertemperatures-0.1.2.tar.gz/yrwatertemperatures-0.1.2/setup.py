from setuptools import setup, find_packages

setup(
    name='yrwatertemperatures',
    version='0.1.2',
    author='Jørn Pettersen',
    author_email='joern.pettersen@gmail.com',
    description='A Python client to fetch water temperatures in Norway from YR.no.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jornpe/yr-norwegian-water-temperatures', # Replace with your repo URL
    packages=find_packages(),
    install_requires=[
        'requests>=2.20.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    project_urls={
        'Bug Tracker': 'https://github.com/jornpe/yr-norwegian-water-temperatures/issues',
    },
)