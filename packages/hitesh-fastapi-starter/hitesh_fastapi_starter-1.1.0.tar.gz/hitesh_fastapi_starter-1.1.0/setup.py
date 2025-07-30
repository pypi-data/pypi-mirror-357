from setuptools import setup, find_packages

setup(
    name="hitesh-fastapi-starter",
    version="1.1.0",
    author="Hitesh Ladumor",
    author_email="your_email@example.com",  # Apna email daal
    description="Generate a FastAPI starter project structure",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your_github/hitesh-fastapi-starter",  # Apna GitHub URL daal
    packages=find_packages(),
    install_requires=[
        "fastapi",
    ],
    entry_points={
        "console_scripts": [
            "hitesh-fastapi-starter=fastapi_starter.generator:create_fastapi_project_cli"
        ],
    },




    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
