from setuptools import setup, find_packages

setup(
    name='vr1',
    version='0.01',
    description='OpenMC model of VR-1 reactor Vrabec',
    author='Ondrej Chvala, Alex Macris, Soha Aslam',
    author_email='ochvala@utexas.edu',
    url='https://github.com/ondrejch/VR1-openmc',
    packages=find_packages(),
    license='MIT',
    install_requires=[
        'numpy',
        'json5',
        'pytest',
        'scipy',
        # 'openmc',
        'matplotlib~=3.9',
        'uncertainties',
        'setuptools',
    ],
    python_requires=">=3.8",
    include_package_data=True   
)
