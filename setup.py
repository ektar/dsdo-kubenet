"""Tools for deploying a kubernetes-based data science environment to AWS
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dsdo_kubenet',

    version='1.0.0',

    description='Tools for deploying a kubernetes-based data science environment to AWS',
    long_description=long_description,

    url='https://github.com/ektar/dsdo-kubenet',

    author='Eric Carlson',
    author_email='eric@ds-do.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='datascience kubernetes',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        # 'peppercorn'
        ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'dsdo_kubenet': ['templates/*', 'manifests/*'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'create-kops-config=dsdo_kubenet.scripts.create_kops_config:main',
            'dsdo-prep=dsdo_kubenet.scripts.dsdo_prep:main',
            'fetch-instance-info=dsdo_kubenet.scripts.fetch_instance_info:main',
            'create-certs=dsdo_kubenet.scripts.create_certs:main',
            'launch-bastion=dsdo_kubenet.scripts.launch_bastion:main',
            'launch-ingress=dsdo_kubenet.scripts.launch_ingress:main',
            'launch-ldap=dsdo_kubenet.scripts.launch_ldap:main',
            'launch-terminal=dsdo_kubenet.scripts.launch_terminal:main',
            'prepare-efs=dsdo_kubenet.scripts.prepare_efs:main',
            'update-launch-dns=dsdo_kubenet.scripts.update_launch_dns:main'
        ],
    },
)