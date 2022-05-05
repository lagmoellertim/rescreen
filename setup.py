from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='rescreen',
    author='Tim-Luca Lagmöller',
    author_email='mail@lagmoellertim.de',
    description='Screen Manager with fractional scaling support for X11',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT License',
    version='1.0.0',
    url='https://github.com/lagmoellertim/rescreen',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        'console_scripts': [
            'rescreen = rescreen.entrypoints.user_interface:main',
            'rescreen-watchdog = rescreen.entrypoints.screen_watchdog:main'
        ]
    },
    install_requires=requirements,
    packages=find_packages()
)
