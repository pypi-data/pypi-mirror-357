from setuptools import setup, find_packages

setup(
    name='amount_extractor_app',
    version='2.0.1',
    author='CRYPT_ATU',
    description='A GUI tool to extract and process currency values from text',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'amount_extractor': ['assets/*.ico', 'assets/*.png']
    },
    install_requires=[],
    entry_points={
        'gui_scripts': [
            'amount-extractor = amount_extractor.gui_launcher:launch_app'
        ],
    },
)
