from setuptools import setup, find_packages


setup(
    name = 'method_flowchart',
    version='0.1.0',
    packages=find_packages(),
    description='Generate Mermaid flowcharts from Python methods',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Vipul Malhotra',
    author_email='vipulm124@gmail.com',
    url='',
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Documentation',
    ],
    keywords='mermaid flowchart ast code analysis documentation',
    entry_points={
        'console_scripts': [
            'method-flowchart=method_flowchart.cli:main',
        ],
    },
)