from setuptools import find_packages, setup
setup(
    name="SQL_Assistant",
    version="0.1.0",
    author="Saurabh Kamal",
    author_email="saurabh.kamal1",
    packages=find_packages(),
    install_requires=[]   # It will take all the requirements from requirements.txt and install
)

# This will help to install any kinds of folder as a local package because here we will be following the modular coding; I will try
# I am importing some function from different modules, and for this setup.py is required.