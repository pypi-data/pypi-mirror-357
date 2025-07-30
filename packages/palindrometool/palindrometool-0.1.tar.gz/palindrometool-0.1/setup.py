from setuptools import setup,find_packages

setup(
    name='palindrometool',
    version='0.1',
    packages=find_packages(),
    description='Check if a word or sentence is a palindrome',
    author='Jeet Thakkar',
    author_email='thakkarjeet536@gmail.com',

    classifiers=['Programming Language :: Python :: 3',
                 'Operating System :: OS Independent',
                 ],
                 python_requires='>=3.6',
    )
