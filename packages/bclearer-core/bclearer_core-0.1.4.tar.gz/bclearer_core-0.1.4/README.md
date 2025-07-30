# bclearer core

The `bclearer_core` package is the foundational component of the bclearer framework, providing essential utilities and services required for the data pipeline architecture in semantic engineering. It encompasses core functionalities that are utilized across the entire framework, ensuring consistency and extensibility.

## Overview

The `bclearer_core` library offers a collection of modules responsible for handling common tasks and configurations that are integral to the bclearer framework. These components form the backbone of the system and enable efficient management of knowledge, configurations, constants, and stages within the pipeline.

## Structure

The package consists of several key modules:

- **ckids**: Manages unique identifiers within the bclearer framework, ensuring consistency and traceability across components.
- **common_knowledge**: Contains shared knowledge and common utilities that are used across the framework.
- **configuration_managers**: Responsible for managing and handling various configurations for bclearer applications and processes.
- **configurations**: Defines standard configuration structures and utilities for the framework.
- **constants**: Stores and manages global constants used throughout the bclearer framework.
- **nf**: Manages foundational operations, providing core support for various tasks.
- **substages**: Handles the different substages of the data pipeline, offering utilities to manage transitions and execution within stages.

## Installation

To install this package, use pip:

```bash
pip install bclearer_core
```

Or, clone this repository and install it locally:

```bash
git clone <repository-url>
cd bclearer_core
pip install .
```

## Usage

To use the core functionalities, import the desired module. For example:

```python
from bclearer_core import configurations

# Example usage
config = configurations.load_configuration(config_path="path/to/config.yaml")
print(config)
```

## Contributions

Contributions are highly appreciated! Feel free to submit issues, pull requests, or feature requests to enhance the core functionality.
