
from setuptools import find_packages
from setuptools import setup

from beanstalk_dispatch import get_version


setup(
    name='beanstalk-dispatch',
    version=get_version().replace(' ', '-'),
    packages=find_packages(exclude='test_app'),
    description='Django application to schedule and run functions on an AWS SQS queue.',
    url='http://github.com/joshblum/beanstalk-dispatch',
    license='MIT',
    author='Joshua Blum',
    author_email='jblum18@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
    install_requires=open('requirements.txt').readlines(),
    python_requires='>=2.7, <4',
    tests_require=open('test-requirements.txt').readlines(),
    include_package_data=True
)
