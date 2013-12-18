Gapy
====

Gapy is a thin service account client for Google Analytics. 

Get set up
----------

First you need to create either a service account or client ID in your
[Google API Console](https://code.google.com/apis/console). If you're
authenticating as a service account you'll need to download your private key.
If you're authenticating as a web or installed application you'll need to
download your client secrets file (Download JSON in API Access list).

Then just create a gapy client and start querying. Ids, metrics and dimensions are provided without the `ga:` prefix.
They can be provided as lists or single values.

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
                ["visits", "visitors"],
                "date")

