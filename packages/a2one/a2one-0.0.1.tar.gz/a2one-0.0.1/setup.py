from setuptools import setup, find_packages

setup(
    name='a2one',  # PyPI name
    version='0.0.1',
    packages=find_packages(where='a2one'),
    package_dir={'': 'a2one'},
    author='Thalaivar',
    author_email='ragavan@example.com',
    description='Thalaivar\'s personal metadata module',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/thalaivar96/a2one',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
