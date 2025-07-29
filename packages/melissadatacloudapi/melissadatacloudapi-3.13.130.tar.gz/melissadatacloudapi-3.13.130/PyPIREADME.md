# Melissa Cloud API Python Package

[![Static Badge](https://img.shields.io/badge/pypi-v3.13.130-blue)](https://pypi.org/project/melissadatacloudapi/) [![Static Badge](https://img.shields.io/badge/documentation-docs-33aaff)](https://docs.melissa.com/cloud-api/cloud-api/cloud-api-packages-installation-guide.html#pip-installation-python) [![Static Badge](https://img.shields.io/badge/source_code-github-orange)](https://github.com/MelissaData/MelissaCloudAPI-PyPI) [![Static Badge](https://img.shields.io/badge/sample_code-github-75ff7e)](https://github.com/MelissaData/MelissaCloudAPI-Python3)



## Overview

The Melissa Cloud API Python Package provides a unified and streamlined way to access all Melissa Cloud APIs within a single, easy-to-use package. This allows developers to seamlessly integrate and access Melissa's powerful cloud-based services directly from their own development environment. 

For more details about how to use the Melissa Cloud API Python Package, please visit the [Melissa Docs](https://docs.melissa.com/cloud-api/cloud-api/cloud-api-packages-installation-guide.html#pip-installation-python)

For more details about Melissa Cloud APIs, please click [here](https://docs.melissa.com/cloud-api/cloud-api/cloud-api-index.html)

## Features

- **Comprehensive API Coverage:** Access all Melissa Cloud APIs through a unified interface
- **Ease of Integration:** Simplifies the process of integrating Melissa's Cloud APIs into your applications
- **Consistent Interface:** Offers a standardized way to interact with different Melissa Cloud APIs

# Getting Started

These instructions will get you a copy of the package integrated into your development environment.

### Licensing

All Melissa cloud services require a license to use. This license is an encrypted series of letters, numbers, and symbols. This license can also either be a Credit license or a Subscription license. Both ways use the same service, so you do not need to change your code to move from one model to another.

To learn more about how to set up a license key with Melissa, please click [here](https://docs.melissa.com/cloud-api/cloud-api/licensing.html)

### Installation

**To integrate the package source code with another Python project, proceed with the following instructions:**

### Install with pip - reccommended method

1. Ensure that you have pip installed on your machine. You can check this by using : 
    ```
    pip --version
    ```
    For information on installing and using pip please see https://pip.pypa.io/en/stable/installation/
    
2. Run the command:
    ```
    pip install melissadatacloudapi
    ```
3. Add to your project:
    ```
    import melissadatacloudapi
    ```
    Or if you want to only add specific classes add something like this:
    ```
    from melissadatacloudapi.RecordRequests import GlobalPhoneRecordRequest
    from melissadatacloudapi.cloudapis.GlobalPhone import GlobalPhone
    from melissadatacloudapi.apiresponse import GlobalPhoneResponse
    from melissadatacloudapi.PostReqestBase import GlobalPhonePostRequest
    ```

#### Import to your project manually

1.  Navigate to the project directory where you would like to add the package.

2.  Clone the package repository using the command:
    ```
    git clone [https://github.com/MelissaData/MelissaCloudAPI-PyPI](https://github.com/MelissaData/MelissaCloudAPI-PyPI)
    ```
    This will create a directory named `MelissaCloudAPI-PyPI` in your current location.

3.  Locate the package files: Inside the `MelissaCloudAPI-PyPI` directory, you will find the actual package files within a subdirectory also named `melissadatacloudapi`.

4.  Copy the `melissadatacloudapi` directory: Copy the entire `melissadatacloudapi` directory.

5.  Navigate to your project's main directory.

6.  Paste the `melissadatacloudapi` directory into your project's main directory. Your project structure should now look something like this (example):

    ```
    your_project/
    ├── your_script.py
    ├── ...
    └── melissadatacloudapi/
        ├── __init__.py
        ├── cloudapis/
        │   ├── ...
        ├── apiresponse/
        │   ├── ...
        ├── PostReqestBase.py
        └── RecordRequests.py
    ```



## Contact Us
For free technical support, please call us at 800-MELISSA ext. 4 (800-635-4772 ext. 4) or email us at Tech@Melissa.com.
