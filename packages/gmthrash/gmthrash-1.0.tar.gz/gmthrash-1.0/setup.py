from setuptools import setup, find_packages

#with open("README.md", 'r') as f:
#    long_description = f.read()

setup(
   name='gmthrash',
   version='1.0',
   description='Forward Convolution Calculations for Crossed Molecular Beams Experiments',
   license="MIT",
#   long_description=long_description,
   author='Kazuumi Fujioka',
   author_email='kazuumi@hawaii.edu',
   url="https://github.com/kaka-zuumi/GMTHRASH",
   packages=find_packages(include=['GMTHRASH_cli'],exclude=['GMTHRASH']),  #same as name
   install_requires=['pandas', 'numpy', 'scipy', 'matplotlib', 'sys', 're', 'customtkinter', 'tkinter'], #external packages as dependencies
   scripts=[
            'GMTHRASH.py',
            'GMTHRASH_cli.py',
           ]
)
