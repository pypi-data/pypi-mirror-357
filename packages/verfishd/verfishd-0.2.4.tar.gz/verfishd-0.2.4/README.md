<div align="center">
  <img src="https://raw.githubusercontent.com/marine-data-science/verfishd/main/images/logo/square_logo.png" alt="Logo of VerFishD">
</div>

**VerFishD** is a library for simulating vertical fish distribution under the influence of physical stimuli.

![PyPI - Version](https://img.shields.io/pypi/v/verfishd)
![Tests - Status](https://github.com/marine-data-science/verfishd/actions/workflows/pytest.yml/badge.svg)

## Concept

VerFishD uses `PhysicalFactor` objects to influence fish movement. You can implement this base class to define your own physical factors, such as temperature, light, oxygen, etc. The next step is to load a `StimuliProfile`, which represents a collection of specific stimulus values. The migration speed function determines the final vertical movement of the fish. The sign of this function determines the movement direction, while the absolute value indicates the percentage of fish that will move. These values are combined to simulate the vertical distribution of fish over time.

## Installation

VerFishD is available on PyPI and can be installed using Poetry or pip:

```bash
poetry add verfishd
```

or with pip:

```bash
pip install verfishd
```

## Usage

Here is a simple example of how to use VerFishD:

```python
# Define a custom PhysicalFactor
class Temperature(PhysicalFactor):
    """
    A class representing a temperature factor.

    Parameters
    ----------
    weight : float
        The weight is used to scale the factor's contribution to the evaluation function E.
    """

    def __init__(self, weight: float):
        super().__init__("temperature", weight)

    def _calculate(self, value: float) -> float:
        match value:
            case _ if value > 5:
                return 0.0
            case _ if value < 4:
                return -1.0
            case _:
                return value - 5.0


# Create a Stimuli Profile including depth and temperature
stimule_dataframe = pd.DataFrame({
    'depth': [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
    'temperature': [7.0, 6.0, 5.0, 5.4, 4.0, 3.9]
})
stimuli = StimuliProfile(stimule_dataframe)

# Create the temperature factor
temperature_factor = Temperature(1.0)

# Define a very simple migration speed function
migration_speed = lambda x: x

# Create the model
model = VerFishDModel('Example', stimuli, migration_speed, [temperature_factor])

# Simulate the model for 30 steps
model.simulate(800)

model.plot()

plt.show()
```

This example defines a temperature factor, creates a stimuli profile with temperature data over depth, initializes the model with this profile and factor, runs a simulation over 800 time steps, and finally plots the results.

## Features

- **Modularity**: Implement custom physical factors that influence fish movement.
- **Flexibility**: Load different stimuli profiles to simulate various environmental conditions.
- **Visualization**: Plot functions to display simulation results.

## Example Plot

![Example plot of the simulation](https://raw.githubusercontent.com/marine-data-science/verfishd/main/images/example_plot.png)

## Running Tests

To run tests, use:

```bash
pytest
```

## Ideas for the future
- [ ] Combine multiple Stimuli Profiles to do a simulation for a whole day
- [ ] Algorithm to determine if simulation can end?


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
