from setuptools import setup, find_packages

setup(
    name='ventilador',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'PyQt5>=5.15.10',
        'sympy>=1.9.0'
    ],
    entry_points={
        'console_scripts': [
            'ventilador = main:main'
        ]
    },
    author='Tu Nombre',
    author_email='tu@email.com',
    description='Descripción de tu proyecto de ventilador.',
    url='https://link.a.tu/repo/ventilador',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
