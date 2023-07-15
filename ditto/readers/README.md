# Readers design pattern

## 1. Inherit from `AbstractReader`
The `AbstractReader.parse` method can optionally be overridden. The base class `parse` method calls:
1. `parse_nodes`
2. `parse_lines`
3. `parse_transformers`
4. `parse_loads`
5. `parse_regulators`
6. `parse_capacitors`
7. `parse_dg`
8. `if hasattr(self, "DSS_file_names")` then `parse_default_values`

Each of these parse methods takes a single input argument, an instance of `Store`, commonly 
called `model`.

The `model` stores instances of the DiTTo power system objects defined in ditto/models/.

## 2. Each `parse_x` method:
1. Define maps of header names to integer column location
2. Loop through network.txt/equipment.txt/load.txt
    - use `parser_helper` for each line and each CYME object to get dictionaries of object values
    - returns a dictionary of dictionaries, where each sub-dictionary contains the values of the desired attributes of a CYME object.
    - TODO example output
    - these dictionaries are stored in `self.settings`, which is emptied at the beginning of each `parse_x` method.
3. Loop through the parsed objects to create DiTTo model components