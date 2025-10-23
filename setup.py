from setuptools import find_packages
from setuptools import setup

from beanstalk_dispatch import get_version


setup(
    name="beanstalk_dispatch",
    version=get_version().replace(" ", "-"),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude="test_app"),
    description="Django application to schedule and run functions on an AWS SQS queue.",
    url="http://github.com/joshblum/beanstalk-dispatch",
    license="Apache 2",
    author="Joshua Blum",
    author_email="jblum18@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    install_requires=open("requirements.txt").readlines(),
    python_requires=">=3.6, <4",
    tests_require=open("test-requirements.txt").readlines(),
    include_package_data=True,
)
