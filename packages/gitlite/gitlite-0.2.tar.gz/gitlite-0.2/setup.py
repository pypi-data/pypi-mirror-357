from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
with open('README.md', 'r') as f:
    description = f.read()

setup(
    name="gitlite",
    version="0.2",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "gitlite=gitlite.main:main",
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown"
)