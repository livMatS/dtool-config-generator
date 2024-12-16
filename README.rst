Dtool Config Generator
======================

Utility service for generating dtool configuration and readme files from templates.

Features
--------

- User log in via LDAP
- User confirmation e-mail to admin at first user log in
- User-specific generation of dtool ``README.yml`` template
- User-specific generation of dtool config file
- Generation of NetApp StorageGRID S3 access and secret key pairs via NetApp StorageGRID REST API
- Creation of dtool-lookup-server users via dtool-lookup-server REST API

Installation
------------

Install with ::

    $ pip install dtool-config-generator

Setup and configuration
-----------------------

Configure the Flask app
^^^^^^^^^^^^^^^^^^^^^^^

The dtool-config-generator is a Flask app. Flask needs to know where to look for
the app. One therefore needs to define the ``FLASK_APP`` environment variable::

    $ export FLASK_APP=dtool_config_generator

The Flask app will aso need a configuration file specified with::

    $export FLASK_CONFIG_FILE=/path/to/production.cfg


Starting the flask app
^^^^^^^^^^^^^^^^^^^^^^

The Flask web app can be started using the command below::

    $ flask run


Using the CLI
------------------------------------------------

Listing users
^^^^^^^^^^^^^

List all users in dtool-config-generator database with ::

    $ flask user list

StorageGRID API commands
^^^^^^^^^^^^^^^^^^^^^^^^

List all access keys for a user on NetApp StorageGRID endpoint with ::

    $ flask sg list testuser
    [{'accountId': '80888526281258163391',
      'displayName': '****************DT91',
      'expires': '2024-09-28T11:06:30.000Z',
      'id': 'SGKHmb8jGT7fNsI7d-OmA_KgnAtRci-LsqGApLbbkw==',
      'userURN': None,
      'userUUID': '67467f87-d617-42fa-b507-9b8ea7616d48'}]

Sync dtool-config-generator user to NetApp StorageGRID endpoint (i.e. create if not yet existent) with ::

    $ flask sg sync testuser
    Synced user 'testuser': '67467f87-d617-42fa-b507-9b8ea7616d48'

Revoke all keys for a user with ::

    $ flask sg revoke testuser

Create an access key - secret key pair for a user with ::

    $ flask sg create testuser
    Access key 'WLDZ4FSCUPCEO6FEV9XQ'
    Secret key '0CoPq/2PkXadbY6XwvPBMpqcA3vbRQqkGZ/XSSJN'

Revoke all keys and create one new pair for a user with ::

    $ flask sg recreate testuser
    Access key 'WLDZ4FSCUPCEO6FEV9XQ'
    Secret key '0CoPq/2PkXadbY6XwvPBMpqcA3vbRQqkGZ/XSSJN'

Pay attention, these commands print both keys plain text to stdout.


Testing
------------------------------------------------

Many tests only work within a semi-productive environment with access to NetApp StorageGRID and dtool-lookup-server REST API interfaces and are marked as ``integrationtest``. Configure such an environment within ``production.cfg`` within the repository root ad run tests with ``pytest``.
Alternatively, deselect such tests with ``pytest -m "not integrationtest"``.
Some tests rely on ``docker`` for launching an LDAP server.