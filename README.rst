Gapy
====

Gapy is a thin service account client for Google Analytics.

Get set up
----------

First you need to create either a `service account <https://developers.google.com/accounts/docs/OAuth2ServiceAccount>`_ or client ID in your
`Google API Console <https://code.google.com/apis/console>`_. If you're
authenticating as a service account you'll need to download your private key.

If you're authenticating as a web or installed application you'll need to
download your client secrets file. Use the `Google Developers Console <https://console.developers.google.com/>`_ to do this:

- Create a Project for thte application, and add the Analytics API to the Enabled APIs list.
- In "Credentials", click "Create new Client ID".
- Choose "Installed Application" and type should be "Other".
- Once it's generated your ID, click the new "Download JSON" button and save this file as client_secrets.json.

Then just create a gapy client and start querying.

- `storage_path` is the location where you want gapy to keep the `storage.db` file that it will generate the first time it runs.
- Ids, metrics and dimensions can be provided as lists or single values.


.. code :: python

    import gapy.client

    # For a service account
    client = gapy.client.from_private_key(
        "your account name",
        private_key="your private key",
        storage_path="path/to/storage.db")

    # For a web or installed application
    client = gapy.client.from_secrets_file(
        "/path/to/client_secrets.json",
        storage_path="/path/to/storage.db")
    )


    reach_data = client.query.get("12345",
                datetime(2012, 1, 1),
                datetime(2012, 2, 2),
                ['ga:visits', 'ga:visitors'],
                'ga:date')

Google API documentation
------------------------

This library is a layer over the Google Python API. If you wish to work on it, it may be necessary to consult `the Google Analytics API documentation <https://developers.google.com/resources/api-libraries/documentation/analytics/v3/python/latest/analytics_v3.data.ga.html>`_.

