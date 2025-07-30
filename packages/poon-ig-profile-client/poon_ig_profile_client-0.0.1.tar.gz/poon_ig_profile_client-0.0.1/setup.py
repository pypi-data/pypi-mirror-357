from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="poon-ig-profile-client",
    version="0.0.1",
    author="username",
    author_email="email@gmail.com",
    description="Some description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/repo.git",
    license="MIT",
    packages=find_packages(),
    package_dir={'client': 'Client'},
    install_requires=[
        'requests'
    ],
    tests_require=[
        'coverage', 'wheel', 'pytest', 'requests_mock'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha"
    ]
)