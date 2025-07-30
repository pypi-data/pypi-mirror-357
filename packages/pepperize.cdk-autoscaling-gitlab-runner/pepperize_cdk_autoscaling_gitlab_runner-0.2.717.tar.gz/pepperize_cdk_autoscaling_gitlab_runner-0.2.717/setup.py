import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "pepperize.cdk-autoscaling-gitlab-runner",
    "version": "0.2.717",
    "description": "AWS CDK GitLab Runner autoscaling on EC2 instances using docker+machine executor.",
    "license": "MIT",
    "url": "https://github.com/pepperize/cdk-autoscaling-gitlab-runner.git",
    "long_description_content_type": "text/markdown",
    "author": "Patrick Florek<patrick.florek@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/pepperize/cdk-autoscaling-gitlab-runner.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "pepperize_cdk_autoscaling_gitlab_runner",
        "pepperize_cdk_autoscaling_gitlab_runner._jsii"
    ],
    "package_data": {
        "pepperize_cdk_autoscaling_gitlab_runner._jsii": [
            "cdk-autoscaling-gitlab-runner@0.2.717.jsii.tgz"
        ],
        "pepperize_cdk_autoscaling_gitlab_runner": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.8.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.112.0, <2.0.0",
        "pepperize.cdk-private-bucket>=0.0.351, <0.0.352",
        "pepperize.cdk-security-group>=0.0.439, <0.0.440",
        "pepperize.cdk-vpc>=0.0.558, <0.0.559",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
