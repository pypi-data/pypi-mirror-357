# FitRequest

`FitRequest` is a Python library designed to simplify the creation of REST API clients by automating code generation.
It enables developers to generate both synchronous and asynchronous methods for interacting with REST APIs,
handle response formatting, and manage authentication seamlessly.

[![Skillcorner](https://img.shields.io/badge/skillcorner-LimeGreen.svg?labelColor=grey&style=plastic&logo=data:image/svg%2bxml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhLS0gQ3JlYXRlZCB3aXRoIElua3NjYXBlIChodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy8pIC0tPgoKPHN2ZwogICB2ZXJzaW9uPSIxLjEiCiAgIGlkPSJzdmcyIgogICB3aWR0aD0iMjM3LjMzMzMzIgogICBoZWlnaHQ9IjI2Ni42NjY2NiIKICAgdmlld0JveD0iMCAwIDIzNy4zMzMzMyAyNjYuNjY2NjYiCiAgIHNvZGlwb2RpOmRvY25hbWU9IlNraWxsY29ybmVyIE5lb24gR3JlZW4gSWNvbi5lcHMiCiAgIHhtbG5zOmlua3NjYXBlPSJodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy9uYW1lc3BhY2VzL2lua3NjYXBlIgogICB4bWxuczpzb2RpcG9kaT0iaHR0cDovL3NvZGlwb2RpLnNvdXJjZWZvcmdlLm5ldC9EVEQvc29kaXBvZGktMC5kdGQiCiAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPGRlZnMKICAgICBpZD0iZGVmczYiIC8+CiAgPHNvZGlwb2RpOm5hbWVkdmlldwogICAgIGlkPSJuYW1lZHZpZXc0IgogICAgIHBhZ2Vjb2xvcj0iI2ZmZmZmZiIKICAgICBib3JkZXJjb2xvcj0iIzAwMDAwMCIKICAgICBib3JkZXJvcGFjaXR5PSIwLjI1IgogICAgIGlua3NjYXBlOnNob3dwYWdlc2hhZG93PSIyIgogICAgIGlua3NjYXBlOnBhZ2VvcGFjaXR5PSIwLjAiCiAgICAgaW5rc2NhcGU6cGFnZWNoZWNrZXJib2FyZD0iMCIKICAgICBpbmtzY2FwZTpkZXNrY29sb3I9IiNkMWQxZDEiIC8+CiAgPGcKICAgICBpZD0iZzgiCiAgICAgaW5rc2NhcGU6Z3JvdXBtb2RlPSJsYXllciIKICAgICBpbmtzY2FwZTpsYWJlbD0iaW5rX2V4dF9YWFhYWFgiCiAgICAgdHJhbnNmb3JtPSJtYXRyaXgoMS4zMzMzMzMzLDAsMCwtMS4zMzMzMzMzLDAsMjY2LjY2NjY3KSI+CiAgICA8ZwogICAgICAgaWQ9ImcxMCIKICAgICAgIHRyYW5zZm9ybT0ic2NhbGUoMC4xKSI+CiAgICAgIDxwYXRoCiAgICAgICAgIGQ9Ik0gMCwwIFYgNDAzLjg1MiBIIDE0NDMuMjMgTCA4OTAsOTU3LjI1IDY1MS42NzYsNzE4LjgyOCA2Ni4wODU5LDEzMDQuNTQgYyAtMjkuMzk4NCwyOS41MyAtNDYuODI0Miw3MS42MiAtNDYuODI0MiwxMTIuNzEgbCAtMC43MTA5LDExMSBjIDAsMzA3Ljk4IDE5NC44MjAyLDQ3MS43NSA1NDkuNDMzMiw0NzEuNzUgSCAxNzgwIFYgMTU5Ni4wOSBIIDMzMi45OCBMIDg5MCwxMDM4Ljg0IGwgMjM4LjMzLDIzOC40OCA1ODUuNTgsLTU4NS43NjkgYyAyOS4yOCwtMjkuMjg5IDQ2Ljg5LC03MS4zOTEgNDYuODksLTExMi43MjMgViA0NzEuNzUgQyAxNzYwLjgsMTYzLjc3IDE1NzMuNjgsMCAxMjE1LjE2LDAgSCAwIgogICAgICAgICBzdHlsZT0iZmlsbDojMzNmZjZiO2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lIgogICAgICAgICBpZD0icGF0aDEyIiAvPgogICAgPC9nPgogIDwvZz4KPC9zdmc+Cg==)](https://skillcorner.com/)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=public-corner_fitrequest&metric=coverage)](https://sonarcloud.io/summary/new_code?id=public-corner_fitrequest)
[![Build](https://img.shields.io/gitlab/pipeline-status/public-corner/fitrequest?branch=main)](https://gitlab.com/public-corner/fitrequest/-/pipelines/latest?ref=main)
[![PyPI - Version](https://img.shields.io/pypi/v/fitrequest.svg)](https://pypi.python.org/pypi/fitrequest)
[![Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://fitrequest.readthedocs.io/en/latest/)
[![License](https://img.shields.io/gitlab/license/public-corner/fitrequest)](https://gitlab.com/public-corner/fitrequest/-/blob/main/LICENSE.md)
[![Twitter Follow](https://img.shields.io/twitter/follow/skillcorner?style=social)](https://twitter.com/skillcorner)

---

## Key Features

### What This Module Does
- **Easy Synchronous and Asynchronous Code Generation**: Quickly create methods to interact with REST endpoints.
- **Response Formatting**: Automatically handle JSON and XML responses and support JSONPath exploration for JSON responses.
- **Docstring Templating**: Generate meaningful docstrings for each method.
- **Basic Authentication**: Support basic authentication using environment variables or AWS secrets.
- **FitRequest Variable Management**: Easily retrieve data from AWS, system environment variables, or set default values.
- **Argument Generation**: Automatically generate method arguments based on endpoint variables.
- **Decorator handling**: Easily enhance generated fitrequest methods with custom decorators.
- **Retry Behavior**: A ``@retry`` decorator is provided to allow user to implement basic retry logic.
- **Rich syntax options**: Several syntax options provided that can be tailored to your needs and preferences.
- **Auto-generated CLI**: An out-of-the-box CLI is provided with fitrequest classes to easily test methods from a terminal.


### What This Module Doesn’t Do
- **Handle OpenApi**: Generate python clients from *OpenAPI* documents. This may be a future feature.
- **Complex Authentication**: For complex authentication, use a custom HTTPX Authentication method or directly provide the `auth` argument to the generated method.
- **Multiple Request Methods**: Generates only one method per endpoint.
- **XML/HTML Parsing**: Limited support for extracting data from XML and HTML.
- **Streaming Handling**: Does not handle streaming requests/responses. This may be a future feature.

---

## Installation

```bash
pip install fitrequest
```

---

## A Simple Example

```python
from fitrequest.client import FitRequest

class RestApiClient(FitRequest):
    """Awesome class generated with FitRequest."""

    client_name = 'rest_api'
    base_url = 'https://test.skillcorner.fr'
    method_docstring = 'Calling endpoint: {endpoint}'

    method_config_list = [
        {
            'base_name': 'items',
            'endpoint': '/items/',
            'add_async_method': True,
        },
        {
            'name': 'get_item',
            'endpoint': '/items/{item_id}',
        },
        {
            'name': 'get_item_details',
            'endpoint': '/items/{item_id}/details/{detail_id}',
        },
    ]

client = RestApiClient()
```

With the above class, you can perform the following actions:

```python
# Synchronous calls
response = client.get_item(item_id=3)
response = client.get_item_details(item_id=3, detail_id=7)
response = client.get_items()

# Asynchronous calls
response = await client.get_items()
```

---

## Help

See [documentation](https://fitrequest.readthedocs.io/en/latest/) for more details.


---

## Contact
For support, contact the Skillcorner Team: [support@skillcorner.com](mailto:support@skillcorner.com).
