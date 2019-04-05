from setuptools import find_packages, setup

DESC = "Drop in replacement for py-aiger's AIG object with lazy composition."

setup(
    name='py-aiger-lazy',
    version='0.0.1',
    description=DESC,
    url='http://github.com/mvcisback/py-aiger-lazy',
    author='Marcell Vazquez-Chanlatte',
    author_email='marcell.vc@eecs.berkeley.edu',
    license='MIT',
    install_requires=[
        'attr',
        'funcy',
        'py-aiger',
    ],
    packages=find_packages(),
)
