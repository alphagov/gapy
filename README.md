# Gapy

Gapy is a thin service account client for Google Analytics. 

# Get set up

First you need to create a service account in your [Google API Console](https://code.google.com/apis/console).
Then just create a gapy client and start querying.

{{{python
import gapy

client = gapy.service_account()
client.query.get("12345", datetime(2012, 1, 1), datetime(2012, 2, 2), "visits", "date")
}}}
