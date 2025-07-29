# coord2loc

Convert latitude and longitude coordinates into localities like countries and states.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/coord2loc.svg)](https://badge.fury.io/py/coord2loc)

## Overview

`coord2loc` is a Python library that allows you to convert geographic coordinates (latitude and longitude) into human-readable locations, such as countries and administrative regions (states, provinces, etc.). It uses polygon data from geoBoundaries.org to accurately map coordinates to their corresponding locations.

## Installation

You can install all locations by selecting the `all` extra:

```bash
pip install coord2loc[all]
```

Alternatively, you can install specific regions with their respective extras:

```bash
pip install coord2loc[can]  # Canada
pip install coord2loc[usa]  # United States
```

## Usage

### Basic Usage

```python
from coord2loc import Coordinate, locate

# Create a coordinate (New York City)
coordinate = Coordinate(latitude=40.7128, longitude=-74.0060)

# Locate the coordinate
location = locate(coordinate)

# Print the result
print(f"Country: {location.country}")
print(f"Administrative Region: {location.administrative_region}")
# Output:
# Country: USA
# Administrative Region: New York
```

### Handling Unknown Locations

By default, the `locate` function returns `None` for coordinates that cannot be found (e.g., in oceans):

```python
from coord2loc import Coordinate, locate

# Coordinate in the Atlantic Ocean
coordinate = Coordinate(latitude=30.0, longitude=-40.0)

# Locate the coordinate
location = locate(coordinate)

# Check if location was found
if location is None:
    print("Location not found")
else:
    print(f"Country: {location.country}")
    print(f"Administrative Region: {location.administrative_region}")
# Output:
# Location not found
```

### Configuring Behavior with Options

You can customize the behavior of the `locate` function using the `Options` class:

```python
from coord2loc import Coordinate, Options, locate, CoordinateNotFound

# Create a coordinate in the ocean
coordinate = Coordinate(latitude=30.0, longitude=-40.0)

# Configure to raise an exception when location is not found
options = Options(raise_on_not_found=True)

try:
    location = locate(coordinate, options)
    print(f"Country: {location.country}")
    print(f"Administrative Region: {location.administrative_region}")
except CoordinateNotFound as e:
    print(f"Error: {e}")
# Output:
# Error: Coordinate (30.0, -40.0) could not be located
```

## API Reference

### Classes

#### `Coordinate`

A named tuple representing a geographic coordinate.

- `latitude` (float): The latitude value (-90 to 90)
- `longitude` (float): The longitude value (-180 to 180)

#### `Location`

A named tuple representing a location.

- `country` (str): The country name
- `administrative_region` (str): The administrative region (state, province, etc.)

#### `Options`

A named tuple for configuring the behavior of the `locate` function.

- `raise_on_invalid` (bool, default=True): Whether to raise an exception for invalid coordinates
- `raise_on_not_found` (bool, default=False): Whether to raise an exception when a location cannot be found

### Functions

#### `locate(coordinate, options=Options())`

Locates a coordinate and returns the corresponding location.

- `coordinate` (Coordinate): The coordinate to locate
- `options` (Options, optional): Configuration options
- Returns: A `Location` object if found, otherwise `None` (unless `raise_on_not_found` is `True`)

### Exceptions

#### `InvalidCoordinate`

Raised when a coordinate is invalid (outside the valid range).

#### `CoordinateNotFound`

Raised when a coordinate cannot be located (when `raise_on_not_found` is `True`).


## Attribution

- [geoBoundaries.org](https://www.geoboundaries.org/index.html)
  ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)): This library embeds polygons derived from the
  [data](./boundaries) made available by geoBoundaries.
- [coord2state](https://github.com/AZHenley/coord2state)
  ([MIT](https://github.com/AZHenley/coord2state?tab=MIT-1-ov-file#readme)): This library is essentially a python port
  [Austin Henley](https://github.com/AZHenley)'s `coord2state` javascript library. Thank you Austin!
