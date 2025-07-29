from setuptools import setup, find_packages

setup(
    name="hashidf",
    version="0.1.1",
    packages=find_packages(),
    package_data={"hashidf": ["data.txt"]},
    install_requires=[],
    author="HashIDF Contributors",
    author_email="support@hashidf.org",
    description="A utility library for decoding Base64, ROT13, and SHA256 hashes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hashidf/hashidf",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
)