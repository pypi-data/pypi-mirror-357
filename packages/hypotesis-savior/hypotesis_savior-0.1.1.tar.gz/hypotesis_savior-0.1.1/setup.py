from setuptools import setup, find_packages

setup(
    name='hypotesis_savior',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'matplotlib',
        'seaborn',
        'statsmodels',
        'plotly',
    ],
    author='Dmitry Koptev',
    author_email='flme.ya@yandex.ru',
    description='A/B Testing Toolkit with CUPED, stratification, bootstrapping and more.',
    long_description='A/B Testing Toolkit with CUPED, stratification, bootstrapping and different statistical criteria for hypotesis testing.',
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
