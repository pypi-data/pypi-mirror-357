from setuptools import setup, find_packages

setup(
    name='atris',
    version='0.1.0',
    description='A seamless ensemble and evaluation library for ML models',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'scikit-learn',
        'numpy',
        'scipy',
        'xgboost',
        'lightgbm',
        'catboost',
        'pyod',  # for HBOS and other anomaly detection models
    ],
    python_requires='>=3.7',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
) 