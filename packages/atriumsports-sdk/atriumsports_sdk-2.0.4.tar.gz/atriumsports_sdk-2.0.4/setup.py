import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    setuptools.setup(
        name="atriumsports_sdk",
        version="2.0.4",
        author="Atrium Sports",
        author_email="python_dev@atriumsports.com",
        description="Python module for integration to Atrium Sports APIs",
        long_description=long_description,
        long_description_content_type="text/markdown",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires=">=3.7",
        install_requires=[
            "requests",
            "paho-mqtt>=2.1.0",
            "python-dateutil>=2.5.3",
            "setuptools>=21.0.0",
            "urllib3>=1.25.3,<2.1.0",
            "pydantic>=2",
            "typing-extensions>=4.7.1",
            "aenum>=3.1.11",
            "pyjwt>=2.8.0",
        ],
    )
