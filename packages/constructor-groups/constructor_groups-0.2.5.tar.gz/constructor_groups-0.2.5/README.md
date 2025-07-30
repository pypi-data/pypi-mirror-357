# Constructor Groups Python SDK

Welcome to the official Constructor Groups Python SDK! This SDK provides a set of tools for integrating with the Constructor Groups platform, allowing developers to easily interact with Constructor Groups APIs and services.

## Installation

Install the SDK via pip:

```bash
pip install constructor-groups
```

## Getting Started

To get started with the Constructor Groups SDK, you first need to initialize it with your credentials. You can find your API keys in the Constructor Groups dashboard under Settings > Developer Settings.


Then, initialize the SDK:

```python
from constructor_groups.client import APIClient

client = APIClient()

client.set_domain("<DOMAIN>")

client.set_credentials(
    access_key="<ACCESS_KEY>",
    secret_key="<SECRET_KEY>",
)
```

## Documentation

Full documentation and API reference can be found in our [Constructor Groups Developer Wiki](https://developer.perculus.com/v2-en). Here, you'll find comprehensive guides, code examples, and troubleshooting tips to help you make the most out of the Constructor Groups SDK.
