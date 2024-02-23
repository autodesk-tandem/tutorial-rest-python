# Autodesk Tandem Data REST API - Tutorials (Python)
This repository contains various examples of how to use the Autodesk Tandem Data REST API to achieve certain workflows. These are reference implementations that can be adopted for specific scenarios.

## Prequisities
The examples are written in Python and require following:
- [Python 3.x](https://www.python.org/downloads/)
- [Python extension for Visual Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [APS application](https://aps.autodesk.com/myapps/). Add application to your facility with **Edit** permission.

### Dependencies
The examples use `requests` library for HTTP communication. Use following steps to install the library:

```sh
python -m pip install requests
```

## Configuration
The examples use 2-legged authentication in cases where authentication is needed. This requires that an application be added to a facility as a service:
1. Create new application using the [APS Portal](https://aps.autodesk.com/myapps/).
2. Open the facility in Autodesk Tandem.
3. Navigate to the "Users" tab on the left panel, then select "Service" and enter the *Client ID* of the application from step 1 above. Make sure to specify the correct permissions.
4. After this, the application should be able to use a 2-legged token when interacting with the facility.

**NOTE:** As an alternative,the application can be added to your Tandem account. In this case the application will have access to all facilities owned by the account.

## Usage
Most of the examples are self-contained. To run a specific example, use the following steps:
1. Open the folder using your code editor.
2. Locate the example you want to run and open it.
3. At the top of the source file there is a block of source code with global variables. Replace those variables according to your environment:
  ``` python
  # update values below according to your environment
  APS_CLIENT_ID = 'YOUR_CLIENT_ID'
  APS_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
  FACILITY_URN = 'YOUR_FACILITY_URN'
  ```
4. Place breakpoints as needed.
5. Start debugger. During debugging use the debuger windows to inspect values of variables.

## Examples
The examples are organized into multiple folders based on topic:
* **assets** - asset related examples
* **classification** - classification related examples
* **documents** - document related examples
* **facility** - facility related examples
* **groups** - group related examples
* **history** - history related examples
* **streams** - streams related examples
* **systems** - system related examples
* **views** - view related examples