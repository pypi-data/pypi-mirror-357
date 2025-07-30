import setuptools

# Read the requirements from the requirements.txt file
with open("README.md", "r") as fh:
    long_description = fh.read()

package_name = "dataos-sdk-py"
package_version = "0.0.6"
description = "Dataos python sdk Package"

setuptools.setup(
    name="dataos-sdk-py",  # Replace with your own username
    version=package_version,
    author="devendrasr",
    author_email="devendra@tmdc.io",
    description="Dataos python sdk",
    long_description=long_description,
    install_requires=[
        "requests>=2.32.3",
        "pydantic>=2.9.2",
        "uplink>=0.9.7"
    ],
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/rubik_/dataos-sdk-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7'
)
