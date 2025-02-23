from setuptools import setup

setup(
    name='custom_deferrable_dataflow_operator',
    version='0.1.1',
    py_modules=['__init__', 'dataflow_trigger',
                'deferrable_dataflow_operator'],
    license='Apache License 2.0',
    package_dir={'': 'custom_operators'},
    # install_requires=[
    #     'apache-airflow',
    #     'google-cloud-dataflow',
    # ],
)
