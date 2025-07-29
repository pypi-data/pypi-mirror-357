from setuptools import setup, find_packages

setup(
    name='seizurekit',
    version='0.1.0',
    author='Talha Ilyas',
    author_email='mr.talhailyas@gmail.com',
    description='A Python toolkit for seizure detection evaluation and analysis.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Mr-TalhaIlyas/seizurekit', # Replace with your repo URL
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'scikit-learn',
        'tqdm',
        'matplotlib', # Added for future visualizations
        'pandas',  # Added for data handling
    ],
    # Add this entry_points section
    entry_points={
        'console_scripts': [
            'seizurekit = seizurekit.__main__:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
    ],
    python_requires='>=3.8',
)