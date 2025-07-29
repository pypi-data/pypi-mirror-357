from setuptools import setup, find_packages

setup(
    name='mathexpr',
    version='1.0.2',
    packages=find_packages(),
    install_requires=[

    ],
    author='griuc',
    author_email='griguchaev@yandex.ru',
    description='A library for parsing math strings',
    long_description=open('mathexpr/README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/professionsalincpp/MathParse',
    license='MIT'
)