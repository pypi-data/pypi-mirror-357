from setuptools import setup, find_packages 

setup(




    name='pypipackageexamplesbs',
    version='0.1.4',
    author='TiagodBe',
    license='MIT',
    description='A simple example package for PyPI',
    packages=find_packages(),                                                                                                               
    install_requires=['scikit-learn'],
    author_email='santiagobergamin@gmail.com',
    url='https://github.com/TiagoBe0/PYPIPACKAGEEXAMPLE.git'

)