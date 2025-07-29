from setuptools import setup, find_packages

setup(
    name='aa-greenlight',
    version='0.1.0',
    description='AllianceAuth plugin for fleet pings via Discord',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/gornik265/aa-greenlight',
    author='gornik265',
    author_email='piotrekcz94@gmail.com.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
