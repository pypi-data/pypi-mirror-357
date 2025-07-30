from setuptools import setup, find_packages

setup(
    name='autotuner',
    version='1.0.0',
    description='AutoTuner: Smart Sorting and Graph Algorithm Selector with Visualization',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Krishna Koushik',
    author_email='mahamkalikoushik0@gmail.com',
    url='https://github.com/koushik-mahamkali/autotuner', 
    license='MIT',

    packages=find_packages(include=['autotuner_core', 'autotuner_core.*']),
    include_package_data=True,
    zip_safe=False,

    python_requires='>=3.7',
    install_requires=[
        'matplotlib',
        'networkx',
        'pandas',
        'seaborn',
        'mplcyberpunk'
    ],

    entry_points={
        'console_scripts': [
            'autotuner-sort=autotuner_core.cli.sort_cli:main',
            'autotuner-graph=autotuner_core.cli.graph_cli:main',
        ],
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    project_urls={
        'Source': 'https://github.com/koushik-mahamkali/autotuner', 
        'Bug Tracker': 'https://github.com/koushik-mahamkali/autotuner/issues', 
    },
)
