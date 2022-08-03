#
# Copyright 2022 Johannes Laurin Hörmann
#
# ### MIT license
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
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
        "flask<2.2.0", # https://github.com/marshmallow-code/flask-smorest/issues/384
        "flask-admin",
        "flask-cors",
        "flask-jwt-extended[asymmetric_crypto]>=4.0",
        "flask-login",
        "flask-ldap3-login",
        "flask-mail",
        "flask-marshmallow",
        "flask-migrate",
        "flask-smorest",
        "flask-sqlalchemy",
        "itsdangerous",
        "marshmallow-sqlalchemy",
        "pyyaml",
        "requests"
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
