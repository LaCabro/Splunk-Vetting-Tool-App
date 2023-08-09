from setuptools import setup, find_packages

setup(
    name='vetting_app',
    version='1.0.0',
    packages=find_packages(),
    package_data={
        'vetting_app': ['data/*'],
    },
    install_requires=[
        # List any dependencies your app may have
    ],
    entry_points={
        'console_scripts': [
            'svta = vetting_app.VetAssist:main'
        ]
    },
)
