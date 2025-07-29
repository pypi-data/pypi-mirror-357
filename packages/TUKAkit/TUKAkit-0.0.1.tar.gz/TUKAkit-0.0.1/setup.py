import os
from setuptools import setup, find_packages

setup(
    name='TUKAkit',
    version='0.0.1',
    description="Toolkit for evaluating crystal structures with the TUKA criteria",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    author='Bin Cao',
    author_email='binjacobcao@gmail.com',
    maintainer='Bin Cao',
    maintainer_email='binjacobcao@gmail.com',
    license='MIT License',
    url='https://github.com/Bin-Cao/TUKA-criteria',
    packages=find_packages(include=['TUKAkit', 'TUKAkit.*']),
    package_data={
        'TUKAkit.testing': ['data/*.cif'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.6',
    install_requires=[

    ],
)
