from setuptools import setup, find_packages

setup(
    name='boron-haren',
    version='0.1.3',
    description='HAREN++: Hybrid Associative Retrieval Engine with Nullified Worst-Case',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Harsith S',
    author_email='harsithharsith217@gmail.com',
    packages=find_packages(),
    install_requires=['numpy'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
