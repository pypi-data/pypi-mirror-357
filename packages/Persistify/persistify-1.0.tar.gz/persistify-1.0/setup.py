from setuptools import setup, find_packages

requirements = []
for line in ("requirements.txt").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if line and not line.startswith("#"):
        requirements.append(line)

setup(
    name="Persistify",
    python_requires='>=3.0',
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'pycryptodome>=3.10.1'
    ],

    description="Library for saving Python data structures as Python code.",
    
    author="SuperWhiteDev",

    url="https://github.com/SuperWhiteDev/Persistify",

    license="MIT",

    long_description=open("README.md").read() if open("README.md") else "",
    long_description_content_type="text/markdown",
)
