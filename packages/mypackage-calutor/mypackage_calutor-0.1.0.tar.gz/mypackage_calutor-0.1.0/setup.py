from setuptools import setup, find_packages

setup(
    name='mypackage-calutor',
    version='0.1.0',
    author='Saiyam Jain',
    author_email='sj@yopmail.com',
    description='A simple calculator package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'calculator=mypackage.saiyamcal.calculator:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
)
