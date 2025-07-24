from setuptools import setup, find_packages

setup(
    name="sftp_auto_sync",
    version="0.1.0",
    author="Khaled Ibrahim",
    author_email="ibrahim84khaled@gmail.com",
    description="Outil d'analyse et de synchronisation automatique de plugins pmmp via SFTP",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/khIbrahim/sftp_auto_sync",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "paramiko>=3.5.0",
        "python-dotenv>=1.1.0",
        "rich>=14.0.0",
        "PyYAML>=6.0.0",
        "GitPython>=3.1.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "sftp-auto-sync=main:main",
        ],
    },
    include_package_data=True,
)
