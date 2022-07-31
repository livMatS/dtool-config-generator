import os
from setuptools import setup


def local_scheme(version):
    """Skip the local version (eg. +xyz of 0.6.1.dev4+gdf99fe2)
    to be able to upload to Test PyPI"""
    return ""


url = "https://github.com/livMatS/dtool-config-generator"
readme = open('README.rst', encoding="utf8").read()

setup(
    name="dtool-config-generator",
    packages=["dtool_config_generator"],
    description="Web service to generate dtool configuration files",
    long_description=readme,
    include_package_data=True,
    author="Johannes L. Hörmann",
    author_email="johannes.hoermann@imtek.uni-freiburg.de",
    url=url,
    use_scm_version={
        "local_scheme": local_scheme,
        "root": '.',
        "relative_to": __file__,
        "write_to": os.path.join(
            "dtool_config_generator", "version.py"),
    },
    install_requires=[
        "flask",
        "flask-marshmallow",
        "flask-smorest",
        "flask-cors",
        "flask-jwt-extended[asymmetric_crypto]>=4.0",
        "flask-login",
        "flask-ldap3-login",
        "pyyaml",
    ],
    setup_requires=['setuptools_scm'],
    tests_require=[
        "pytest",
        "pytest-cov",
        "pytest-docker[docker-compose-v1]",
        "ldap3"
    ],
    license="MIT"
)
