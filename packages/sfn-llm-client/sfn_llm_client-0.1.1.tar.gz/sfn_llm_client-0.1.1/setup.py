from setuptools import setup, find_packages

# To Load the README file to use as the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sfn_llm_client",
    version="0.1.1",  # You can dynamically fetch the version if needed
    description="SDK for using LLM clients",
    long_description=long_description,  # Using README.md as long description
    long_description_content_type="text/markdown",  # README file format
    author="Rajesh Darak",
    author_email="rajesh@stepfuction.ai",
    url="https://github.com/iamrajeshdaraksfn/llm-client-sdk.git",
    classifiers=[
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires='>=3.9',
    packages=find_packages(),
    install_requires=[
        "aiohttp >=3.0.0,<4.0.0",
        "dataclasses_json >= 0.5.0",
        "openai >=1.54.3",
        "tiktoken >=0.3.3",
        "anthropic >= 0.39.0",
        "snowflake-connector-python >=3.12.3",
        "snowflake-ml-python==1.7.0",
        "snowflake-snowpark-python==1.23.0",
        "transformers >= 4.46.2",
    ],
    extras_require={
        'test': [
            "pytest",
            "pytest-aiohttp",
            "pytest-asyncio",
            "pytest-mock",
            "aioresponses",
        ],
        'openai': [
            "openai >=1.54.3",
            "tiktoken >=0.3.3",
        ],
        'huggingface': [
            "transformers >= 4.0.0",
        ],
        'anthropic': [
            "anthropic >= 0.39.0",
        ],
        'arctic': [
            "snowflake-connector-python >=3.12.3",
            "snowflake-ml-python==1.7.0",
            "snowflake-snowpark-python==1.23.0",
            "transformers >= 4.46.2",
        ],
        'google': [
            "google-generativeai >= 0.1.0",
        ],
        'api': [
            "sfn_llm_client[openai,huggingface,anthropic,google,cortex]",
        ],
        'local': [
            "transformers >= 4.0.0",
        ],
        'sync': [
            "async_to_sync >= 0.2.0",
        ],
        'all': [
            "sfn_llm_client[api,local,sync]",
        ],
    },
    package_data={
        "sfn_llm_client": ["README.md"],  # Any other non-Python files can be listed here
    },
)