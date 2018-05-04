# Examples

This folders has some conversion examples of larger test systems.

### Example 1: IEEE 8500

#### OpenDSS ---> Cyme

To run this example, open a terminal and run:

```bash
$ python ieee_8500_opendss_to_cyme.py
```

Alternatively, you can use the CLI and the configuration file ```ieee_8500_opendss_to_cyme.json```. Open a terminal and run:

```bash
$ ditto convert --from dss --input ieee_8500_to_cyme.json --to cyme --output .
```


### Example 2: EPRI J1 Feeder

#### OpenDSS —> Cyme

To run this example, open a terminal and run:

```bash
$ python epri_j1_opendss_to_cyme.py
```

Alternatively, you can use the CLI and the configuration file ```epri_j1_opendss_to_cyme.json```. Open a terminal and run:

```bash
ditto convert --from dss --input epri_j1_opendss_to_cyme.json --to cyme --output .
```


