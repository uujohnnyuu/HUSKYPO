import io
import os

from setuptools import setup, find_packages

from huskypo import version

setup(
    name='huskypo',
    version=version.version,
    description='UI Automation Page Objects design pattern.',
    long_description=io.open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Johnny',
    author_email='johnny071531@gmail.com',
    url='https://github.com/uujohnnyuu/huskyPO',
    license='Apache 2.0',
    keywords=['huskypo', 'page object', 'selenium', 'appium', 'automation'],
    packages=find_packages(),
    install_requires=[
        'Appium-Python-Client >= 3.1.0',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ],
)
