from setuptools import setup, find_packages

setup(
    name="EasyCliMenu",
    version="0.1.0",
    author="Bowser-2077",
    author_email="hostinfire@gmail.com",
    description="Simple CLI menu library for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  # si tu as un repo github
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
)
