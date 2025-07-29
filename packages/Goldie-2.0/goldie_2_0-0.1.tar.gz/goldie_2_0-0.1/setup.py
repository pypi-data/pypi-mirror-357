from setuptools import setup, find_packages

setup(
    name = "Goldie-2.0",
    version = "0.1",
    author = "Muhammad Faizan", 
    description = "This is a speech to text package created by Muhamamd Faizan"    
)

packages = find_packages(),
install_requirements = [
    'selenium',
    'webdriver_manager'
]