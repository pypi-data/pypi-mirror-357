from setuptools import setup, find_packages


def get_readme():
    with open("./readme.md", 'r') as file:
        return file.read()


setup(
    name="py-downx",
    version="1.1.0",
    description="Flexible download manager",
    long_description=get_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/still-standing88/pydown/',
    license='MIT',
    author="still-standing88",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pydown=pydown.cli:main',
        ],
    },
    install_requires=["humanize", "validators", "paramiko", "httpx", "dataclasses-json"],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Documentation",
        "Topic :: Utilities",
    ],
    keywords="pydown py-down download downloads",
)
