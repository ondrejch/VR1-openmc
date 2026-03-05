from setuptools import setup, find_packages

setup(
    name='vr1',
    version='0.1.0',
    description='OpenMC model of VR-1 reactor Vrabec',
    author='Ondrej Chvala, Alex Macris, Soha Aslam',
    author_email='ochvala@utexas.edu',
    url='https://github.com/ondrejch/VR1-openmc',
    packages=find_packages(),
    license='MIT',
    install_requires=[
        'numpy>=1.24',
        'json5>=0.9',
        'scipy>=1.10',
        'openmc>=0.15.0',
        'matplotlib>=3.9,<4.0',
        'uncertainties>=3.2',
    ],
    extras_require={
        'dev': ['pytest>=8.0'],
    },
    python_requires=">=3.10",
    include_package_data=True
)
