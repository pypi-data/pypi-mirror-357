from setuptools import setup, find_packages

setup(
    name='rewar',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['pygame'],
    author='Ankit Rewar',
    author_email='ankitrewar001@gmail.com',
    description='A description of your Python file',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ZeroDayDoom/hello',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
