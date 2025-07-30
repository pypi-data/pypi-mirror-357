from setuptools import setup, find_packages 

setup(




    name='vacancycalculator',
    version='0.2.0.0',
    author='TiagodBe',
    license='MIT',
    description='Defect analysis and vacancy calculation for materials science',
    
    packages=find_packages(where="src"),  # 👈 le decís que busque dentro de src
    package_dir={'': 'src'},              # 👈 mapeás el namespace raíz a src                                                                                                             
    install_requires=['scikit-learn','pandas','xgboost'],
    author_email='santiagobergamin@gmail.com',
    url='https://github.com/TiagoBe0/VFScript-CDScanner'

)