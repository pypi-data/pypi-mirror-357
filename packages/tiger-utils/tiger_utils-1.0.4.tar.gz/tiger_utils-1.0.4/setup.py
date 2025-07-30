from setuptools import setup, find_packages

setup(
  name="tiger_utils",
  version="1.0.4",
  description="A utility package",
  author="peterbc",
  author_email="peterbailec@gmail.com",
  url="https://github.com/peterbaile/tiger-utils",  # Update with your repo
  packages=find_packages(),  # Automatically finds modules
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires=">=3",  # Minimum Python version
)
