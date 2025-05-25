from setuptools import setup

setup(
    name='VR1 in OpenMC',
    version='0.01',
    packages=[
        'vr1',
        'pke'
    ],
    url='https://github.com/ondrejch/VR1-openmc',
    license='MIT',
    author='Ondrej Chvala, Alex Macris',
    author_email='ochvala@utexas.edu',
    description='OpenMC model of VR-1 reactor Vrabec',
    install_requires=[
        'numpy',
        'json5',
        'pytest',
        'scipy',
        'openmc',
        'matplotlib~=3.9'
        'uncertainties',
        'setuptools',
    ]
)
