from setuptools import setup, find_packages

setup(
    name="zscheduler",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "schedule>=1.2.0",
        "python-dateutil>=2.8.2",
        "apscheduler>=3.10.0",
        "croniter>=1.3.0",
        "pytz>=2022.1",
    ],
    author="ZScheduler Team",
    author_email="zscheduler@example.com",
    description="High-performance task scheduling library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mexyusef/zscheduler",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
