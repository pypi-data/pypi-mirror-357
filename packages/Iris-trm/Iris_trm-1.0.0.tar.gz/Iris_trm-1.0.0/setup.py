from setuptools import setup, find_packages

setup(
    name='Iris_trm',
    version='1.0.0',
    author='Cha Verde',
    author_email='chaverde08@gmail.com',
    description='Apenas alguns códigos para melhorar a interação com o terminal',
    long_description="a",
    long_description_content_type='text/markdown',
    url='',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'pyfiglet',
        'keyboard'
    ],
)
