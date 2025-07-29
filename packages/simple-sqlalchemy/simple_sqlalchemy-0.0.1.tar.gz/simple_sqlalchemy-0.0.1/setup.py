from setuptools import setup, find_packages

# Change this to the package name you want to test
PACKAGE_NAME = "simple-sqlalchemy"

setup(
    name=PACKAGE_NAME,
    version="0.0.1",
    author="Test Author",
    author_email="test@example.com",
    description="A test package for checking PyPI name availability",
    long_description="This is a minimal test package used to check if a package name is available on PyPI.",
    long_description_content_type="text/plain",
    url="https://github.com/test/test-package",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
