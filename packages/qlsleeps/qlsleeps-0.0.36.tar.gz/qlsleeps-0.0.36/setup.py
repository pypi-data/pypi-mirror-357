from setuptools import setup, find_packages

setup(
    name='qlsleeps',
    version='0.0.36',
    keywords='eeg sleep staging analysis',
    description='a python analyse tool for QLan Sleep Analysis',
    license='MIT License',
    url='http://8.136.42.241:8088/quanlan/python/qleegss/-/tree/dev',
    author='scg',
    author_email='shangchungang@eegion.com',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=['scipy', 'numpy', 'torch', 'tqdm', 'lspopt', 'pandas', 'reportlab', 'openpyxl', 'matplotlib'],
)
