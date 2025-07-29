# buildupp - Structural build-up at rest in cementitious materials

The **buildupp** package supports investigations of structural build-up at rest in cementitious materials. It provides tools for analyzing coupled calorimetry and rheometry measurements ([Michel et al. 2024](https://www.sciencedirect.com/science/article/pii/S0008884624002461)), and is easily extensible for the study of blended cements. Material properties are centralized and variations in physical properties such as particle size distributions (PSD) are efficiently tracked.

## Repository Structure

The repository is structured as follows:

### `buildupp/` Directory
This directory contains the core logic for the package:
- `blend.py`: Implements the logic for material blending, focusing on different powder compositions.
- `experiment.py`: Defines the `Experiment` class that models hydration experiments based on given inputs and system measurements.
- `config.py`: Handles the loading and management of user-specific settings (e.g., paths, material databases, default experimental setup).
- `hydration.py`: Provides methods for thermodynamic analysis of the hydration of cementitious materials.
- `utils.py`: A collection of utility functions to support various tasks like data handling and file parsing.

### `config/` Directory
This directory contains all the configuration files that define physical properties, paths, and material data:
- `chemistry_database.ini`: Contains chemical properties (e.g., molar mass, density, formation enthalpy) for various cementitious compounds.
- `data.py`: A file that defines the default data frames for experiment analysis.
- `paths.ini`: Defines the root paths for the data directories used in the experiments.
- `physical_properties.ini`: Contains physical properties like density, SSA (specific surface area), and PSD (particle size distribution) file paths for various materials.
- `systems_measured.py`: Stores predefined experimental data, including different cementitious systems (e.g., OPC, LS, MK).
- `user_functions.py`: Allows the user to define custom functions to read PSD data. The current default function is for **Horiba Partica LA-950 Laser Scattering PSD Analyzer** but can be extended for other setups.

## Key Features

- **Customizable PSD Data Import:** The package allows you to define your own functions to read PSD data files, adapting to different measurement instruments.
- **Material Database:** Includes predefined chemical and physical properties for various materials used in cementitious systems (e.g., OPC, LS, MK).
- **Simulation of Hydration Reactions:** Through the `Experiment` class, you can perform structural build-up investigations from coupled calorimetry and rheometry measurements.
- **Flexible Configuration:** User-specific settings can be customized through configuration files like `paths.ini`. Material properties  are kept track of in `chemical_database.ini`.

## Installation

`buildupp` can be installed with pip

```bash
pip install buildupp
```

## Usage

To start using the package, you can first configure your paths and material properties by modifying the relevant configuration files:

1. **Set Up Paths:**
    Open the `config/paths.ini` file and define the root directories for your data. Make sure the correct paths are specified for each user.

2. **Define Material Properties:**
    Modify `config/physical_properties.ini` to define the physical properties for the materials in your study. Each material can have properties such as `density_gpcm3`, `ssa_bet_m2pg`, and `psd` file paths.

3. **Define User Functions (if needed):**
    If you need to read PSD files from an instrument not covered by the default `read_psd_csv`, you can define your custom function in `config/user_functions.py`.

4. **Analyze an Experiment:**
    You can use the `Experiment` class from `experiment.py` to analyze coupled calorimetry/rheometry data. Here's an example of creating an experiment object:

    ```python
    from buildupp.experiment import Experiment
    from buildupp.config import Config
    
    # Load configuration
    config = Config(config_dir='./config')

    # Define experiment inputs (can also use default)
    exp_inputs = {
        'db_entry': config.systems_measured['opc'][0]['db_entry']
    }

    # Create the experiment object
    experiment = Experiment(exp_inputs=exp_inputs, config=config)

    # Plot experimental results (example)
    exp.plot_GtildeDVproductsperVgrain(ax=ax, c=c.opc, type=type, label='PC')
    ```

    Alternatively, you can directly use the default `config` from buildupp.PROJECT_ROOT

    ```python
    from buildupp import config, Experiment

    # leveraging config
    s = config.systems_measured
    c = config.colors
    desktop_path = config.desktop_directory

    # generate figure
    fig, ax = plt.subplots()
    type = 'semilogy'

    # plot all PC measurements
    for i, e in enumerate(s.opc):
        exp = Experiment(e)
        if i == 0:
            exp.plot_GtildeDVproductsperSgrain(ax=ax, c=c.opc, type=type, label='PC')
        else:
            exp.plot_GtildeDVproductsperSgrain(ax=ax, c=c.opc, type=type)
    ```

## License

Copyright &copy; 2024 ETH Zurich (Luca Michel)

**buildupp** is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

**buildupp** is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with **buildupp**.  If not, see <https://www.gnu.org/licenses/>.