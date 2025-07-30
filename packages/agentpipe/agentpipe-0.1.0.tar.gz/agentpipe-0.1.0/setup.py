from setuptools import setup, find_packages

# Read the contents of the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentpipe",
    version="0.1.0",
    author="Koen van Eijk",
    author_email="vaneijk.koen@gmail.com",
    description="A minimal, composable library for building LLM-powered agents and pipes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/koenvaneijk/agentpipe",  # Assuming a GitHub URL, can be changed.
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.8',
    install_requires=[
        'zenllm',
        'Jinja2',
        'pydantic',
    ],
    license="MIT",
)