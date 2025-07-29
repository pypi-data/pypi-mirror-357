import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "condensetech.cdk-constructs",
    "version": "0.5.14",
    "description": "Condense's opinionated constructs and stacks for AWS CDK",
    "license": "MIT",
    "url": "https://github.com/cdklabs/cdk-monitoring-constructs",
    "long_description_content_type": "text/markdown",
    "author": "Condense s.r.l.<tech@condense.tech>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/cdklabs/cdk-monitoring-constructs"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "condensetech.cdk_constructs",
        "condensetech.cdk_constructs._jsii"
    ],
    "package_data": {
        "condensetech.cdk_constructs._jsii": [
            "cdk-constructs@0.5.14.jsii.tgz"
        ],
        "condensetech.cdk_constructs": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.8",
    "install_requires": [
        "aws-cdk-lib>=2.149.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.103.1, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<5.0.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
