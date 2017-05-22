from setuptools import setup

setup(
    name='matchtools',
    version='0.1.2',
    description='A set of tools for data matching and manipulation',
    author='Anton Kupenko & Dawid Kaczmarski',
    author_email='anton.kupenko@gmail.com, dawidkaczmarski@gmail.com',
    license='MIT',
    keywords='match matching comparison data attributes alignment integration',
    packages=['matchtools'],
    url='https://github.com/matchtools/matchtools',
    package_data={'': ['*.json']},
    include_package_data=True,
    install_requires=['datefinder', 'fuzzywuzzy', 'geopy', 'roman'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Office/Business',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
