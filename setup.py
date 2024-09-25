from setuptools import setup, find_packages

setup(
    name='choreboss',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'SQLAlchemy',
        'marshmallow',
        'user-agents',
        'ua-parser',
        'PyYAML'
    ],
    entry_points={
        'console_scripts': [
            'run=run:main',
        ],
    },
)
