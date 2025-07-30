from setuptools import setup, find_packages

setup(
    name='vacancycalculator',
    version='0.2.0.2',
    author='TiagodBe',
    license='MIT',
    description='Defect analysis and vacancy calculation for materials science',
    packages=find_packages(where="src"),       # 👈 busca paquetes en src/
    package_dir={'': 'src'},                   # 👈 le dice a Python que src/ es la raíz
    install_requires=[
        'scikit-learn',
        'pandas',
        'xgboost'
    ],
    author_email='santiagobergamin@gmail.com',
    url='https://github.com/TiagoBe0/VFScript-CDScanner',
)
