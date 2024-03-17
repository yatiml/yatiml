from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='yatiml',
    version='0.11.1',
    description="Reading, checking and writing YAML from Python",
    long_description=readme + '\n\n',
    author="Lourens Veen",
    author_email='l.veen@esciencecenter.nl',
    url='https://github.com/yatiml/yatiml',
    package_data={'yatiml': ['py.typed']},
    packages=[
        'yatiml',
    ],
    package_dir={'yatiml': 'yatiml'},
    include_package_data=True,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='yatiml',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
    install_requires=[
        'PyYAML>=5.1,!=5.4.1',
        'typing_extensions'
    ]
)
