# PyCentral (Central Python Package SDK)

Welcome to PyCentral, a Python SDK for interacting with HPE Aruba Networking Central via REST APIs. This library provides tools for automating repetitive tasks, configuring multiple devices, monitoring, and more.

> [!WARNING]  
> This is a **pre-release version** of PyCentral-v2, and the features are constantly being updated as the APIs evolve. This version of the SDK allows you to make API calls to New Central, GLP, and Classic Central.  
> If you are looking for the stable version of PyCentral (v1), it is still available and fully supported. PyCentral-v1, which only supports Classic Central, can be found [here](https://pypi.org/project/pycentral/).

---

## New Central

This **pre-release** version allows users to make REST API calls to New Central, the next generation of HPE Aruba Networking Central. It also supports making REST API calls to the HPE GreenLake Platform.

Upgrading to this pre-release version will not break PyCentral-v1 code. All the PyCentral-v1 code has been moved to the `classic` folder within the PyCentral directory, ensuring backward compatibility. You can find Classic Central PyCentral Documentation [here](#classic-central).

---

### Installing the Pre-release

To install the latest pre-release version of PyCentral, use the following command:

```bash
pip3 install --pre pycentral
```

If you already have PyCentral-v1 and would like to upgrade to the pre-release version, use the following command:

```bash
pip3 install --upgrade --pre pycentral
```

---

### Getting Started

Once you have installed the pre-release version of PyCentral, you need to obtain the necessary authentication details based on the platform you are working with:

#### 1. **New Central Authentication**
   For New Central, you must obtain the following details before making API requests:
   - **Base URL or Cluster Name**: Base URL is the API Gateway URL for your New Central account based on the geographical cluster of your account on the HPE GreenLake Platform. You can find the base URL or cluster name of your New Central account's API Gateway from the table [here](https://developer.arubanetworks.com/new-central/docs/getting-started-with-rest-apis#base-urls).
   - **Client ID and Client Secret**: These credentials are required to generate an access token to authenticate API requests. You can obtain them by creating a Personal API Client for your New Central Account. Follow the detailed steps in the [Create Client Credentials documentation](https://developer.arubanetworks.com/new-central/docs/generating-and-managing-access-tokens#create-client-credentials).

#### 2. **HPE GreenLake (GLP) Authentication**
   If you are working with HPE GreenLake APIs, authentication is slightly different:
   - GLP does not require a Base URL.
   - You only need the **Client ID & Client Secret** for the HPE GreenLake Platform.

---

#### Example Script

Before running the script, create a `token.yaml` file in the same directory and populate it with the required credentials as follows:

```yaml
new_central:
  base_url: <api-base-url>
  client_id: <client-id>
  client_secret: <client-secret>
glp:
  client_id: <client-id>
  client_secret: <client-secret>
```

Once you have the `token.yaml` file ready, you can run the following Python script:

```python
import os
from pycentral import NewCentralBase

# Validate token file exists
token_file = "token.yaml"
if not os.path.exists(token_file):
    raise FileNotFoundError(
        f"Token file '{token_file}' not found. Please provide a valid token file."
    )

# Initialize NewCentralBase class with the token credentials for New Central/GLP
new_central_conn = NewCentralBase(
    token_info=token_file,
)

# New Central API Call
new_central_resp = new_central_conn.command(
    api_method="GET", api_path="network-monitoring/v1alpha1/aps"
)

print(new_central_resp)
print()
# GLP API Call
glp_resp = new_central_conn.command(
    api_method="GET", api_path="devices/v1/devices", app_name="glp"
)

print(glp_resp)
```

Run the script using the following command:

```bash
python3 demo.py
```

---

## Classic Central

The Classic Central functionality is still fully supported by the SDK and has been moved to a dedicated documentation page. For information on using the SDK with Classic Central, including authentication methods, API calls, and workflow examples, please see the [Classic Central Documentation](https://github.com/aruba/pycentral/blob/master/README.md).

### Documentation

- <a href="https://pycentral.readthedocs.io/en/latest/" target="_blank">Python package documentation</a>

### **Use-Cases and Workflows**
- <a href="https://developer.arubanetworks.com/central/docs/python-getting-started" target="_blank">HPE Aruba Networking Developer Hub</a>
- <a href="https://github.com/aruba/central-python-workflows/tree/main" target="_blank">central-python-workflows</a>
