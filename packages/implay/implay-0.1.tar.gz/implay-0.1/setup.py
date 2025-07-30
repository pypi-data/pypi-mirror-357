from setuptools import setup, find_packages

setup(
    name='implay',
    version='0.1',
    author='subin erattakulangara',
    url='https://subinek.com/',
    packages=find_packages(),
    install_requires=[
        'ipywidgets',
        'opencv-python',
        'IPython',
        'numpy'
    ]
)