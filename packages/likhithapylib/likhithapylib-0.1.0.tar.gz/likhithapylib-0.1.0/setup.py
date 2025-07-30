from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='likhithapylib',
    version='0.1.0',
    description='A simple data visualization library using matplotlib',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jayavarapu Likhitha Swapna',
    author_email='likhithaswapna703@gmail.com',
    url='https://github.com/jayavarapulikhitha/likhithapylib',
    packages=find_packages(),
    install_requires=['matplotlib'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
