# Gapy

Gapy is a thin service account client for Google Analytics. 

# Get set up

First you need to create a service account in your [Google API Console](https://code.google.com/apis/console).
Then just create a gapy client and start querying. Ids, metrics and dimensions are provided without the `ga:` prefix.
They can be provided as lists or single values.

```python
import gapy

client = gapy.service_account("your account name",
            private_key="your private key",
            storage_path="path/to/storage.db")
client.query.get("12345",
            datetime(2012, 1, 1),
            datetime(2012, 2, 2),
            ["visits", "visitors"],
            "date")
```


