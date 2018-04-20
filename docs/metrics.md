# Metrics documentation

DiTTo has the capability to extract metrics from a system once parsed in the core representation. This enables the user to compute metrics when doing a conversion from one format to another.

The advantage compared to computing metrics on a given format is that no conversion is needed prior to the caculation.

## List of available metrics

Here is the list of implemented metrics with their description. The list is organized in different sections to ease the search.

### Realistic electrical design and equipment parameters (MV)

|              Metric name              | Type  | Unit  |                      Metric description                      |                   Comments                   |
| :-----------------------------------: | :---: | :---: | :----------------------------------------------------------: | :------------------------------------------: |
|           *mv_length_miles*           | Float | miles |          The total length of medium voltage lines.           |          Needs the nominal voltages          |
|         *Length_mv3ph_miles*          | Float | miles |      The total length of medium voltage, 3 phase lines.      |          Needs the nominal voltages          |
|        *Length_OH_mv3ph_miles*        | Float | miles | The total length of medium voltage, overhead, 3 phase lines. |  Needs the nominal voltages and line_type.   |
|         *Length_mv2ph_miles*          | Float | miles |      The total length of medium voltage, 2 phase lines.      |          Needs the nominal voltages          |
|        *Length_OH_mv2ph_miles*        | Float | miles | The total length of medium voltage, overhead, 2 phase lines. |  Needs the nominal voltages and line_type.   |
|         *Length_mv1ph_miles*          | Float | miles |      The total length of medium voltage, 1 phase lines.      |          Needs the nominal voltages          |
|        *Length_OH_mv1ph_miles*        | Float | miles | The total length of medium voltage, overhead, 1 phase lines. |  Needs the nominal voltages and line_type.   |
|    *percentage_overhead_MV_lines*     | Float |   -   |       Percentage of MV lines that are overhead lines.        |  Needs the nominal voltages and line_type.   |
| *ratio_MV_line_length_to_nb_customer* | Float | miles |     mv_length_miles devided by the number of customers.      | Needs nominal voltages and load information. |
|        *furtherest_node_miles*        | Float | miles | Maximum distance between the substation and any node of the network. |                                              |
|    *nominal_medium_voltage_class*     | Float | Volts |              Nominal voltage of medium voltage.              |                                              |

### Realistic electrical design and equipment parameters (LV)

|              Metric name              | Type  | Unit  |                      Metric description                      |                   Comments                   |
| :-----------------------------------: | :---: | :---: | :----------------------------------------------------------: | :------------------------------------------: |
|           *lv_length_miles*           | Float | miles |            The total length of low voltage lines.            |          Needs the nominal voltages          |
|         *Length_lv3ph_miles*          | Float | miles |       The total length of low voltage, 3 phase lines.        |          Needs the nominal voltages          |
|        *Length_OH_lv3ph_miles*        | Float | miles |  The total length of low voltage, overhead, 3 phase lines.   |  Needs the nominal voltages and line_type.   |
|         *Length_lv1ph_miles*          | Float | miles |       The total length of low voltage, 1 phase lines.        |          Needs the nominal voltages          |
|        *Length_OH_lv1ph_miles*        | Float | miles |  The total length of low voltage, overhead, 1 phase lines.   |  Needs the nominal voltages and line_type.   |
|    *maximum_length_of_secondaries*    | Float | miles | The maximum length between a distribution transformer and a low voltage customer. |          Needs the nominal voltages          |
|         *Length_lv2ph_miles*          | Float | miles |       The total length of low voltage, 2 phase lines.        |          Needs the nominal voltages          |
|        *Length_OH_lv2ph_miles*        | Float | miles |  The total length of low voltage, overhead, 2 phase lines.   |  Needs the nominal voltages and line_type.   |
|    *percentage_overhead_LV_lines*     | Float |   -   |       Percentage of LV lines that are overhead lines.        |  Needs the nominal voltages and line_type.   |
| *ratio_LV_line_length_to_nb_customer* | Float | miles |     lv_length_miles devided by the number of customers.      | Needs nominal voltages and load information. |

### Voltage control schemes

|           Metric name            |  Type   | Unit  |                      Metric description                      |                     Comments                     |
| :------------------------------: | :-----: | :---: | :----------------------------------------------------------: | :----------------------------------------------: |
|        *No_of_Regulators*        | Integer |   -   |               The number of regulator objects.               |                                                  |
|      *Nb_of_CapacitorBanks*      | Integer |   -   |                The number of capacitor banks.                |                                                  |
|         *No_of_Boosters*         | Integer |   -   |                   The number of boosters.                    | Boosters are not currently implemented in DiTTo. |
| *average_regulator_sub_distance* |  Float  | miles | Mean distance between the substation and regulator objects.  |       If no regulator, this metric is Nan.       |
| *average_capacitor_sub_distance* |  Float  | miles | Mean distance between the substation and capacitor bank objects. |       If no capacitor, this metric is Nan.       |

### Basic protection

|           Metric name           |  Type   | Unit  |                     Metric description                     |              Comments              |
| :-----------------------------: | :-----: | :---: | :--------------------------------------------------------: | :--------------------------------: |
|          *No_of_Fuses*          | Integer |   -   |                      Number of Fuses.                      |                                    |
|        *No_of_Reclosers*        | Integer |   -   |                    Number of Reclosers.                    |                                    |
|     *No_of_Sectionalizers*      | Integer |   -   |                 Number of Sectionalizers.                  |                                    |
|  *sectionalizers_per_recloser*  |  Float  |   -   |    *No_of_Sectionalizers* divided by *No_of_Reclosers*.    | If no recloser, this metric is Nan |
| *average_recloser_sub_distance* |  Float  | miles | Mean distance between the substation and recloser objects. | If no recloser, this metric is Nan |
|        *No_of_Breakers*         | Integer |   -   |                    Number of Breakers.                     |                                    |

### Reconfiguration Options

|              Metric name              |  Type   | Unit |                      Metric description                      |                           Comments                           |
| :-----------------------------------: | :-----: | :--: | :----------------------------------------------------------: | :----------------------------------------------------------: |
|           *No_of_Switches*            | Integer |  -   |                     Number of switches.                      |                                                              |
|         *No_of_Interruptors*          | Integer |  -   |                   Number of interruptors.                    |                                                              |
| *number_of_links_to_adjacent_feeders* | Integer |  -   | Number of links between the current feeder and other feeders. | This metrics only works when computing metrics per feeder on a system with multiple feeders. |
|       *nb_loops_within_feeder*        | Integer |  -   |              Number of loops within the feeder.              |                                                              |

### Transformers

|                  Metric name                  |  Type   | Unit |                      Metric description                      |                          Comments                           |
| :-------------------------------------------: | :-----: | :--: | :----------------------------------------------------------: | :---------------------------------------------------------: |
|       *nb_of_distribution_transformers*       | Integer |  -   |             Number of distribution transformers.             |                                                             |
|      *number_of_overloaded_transformer*       | Integer |  -   | Number of distribution transformers where its secondary KVA rating is smaller than the sum of downstream load KVA. |                                                             |
| *distribution_transformer_total_capacity_MVA* |  Float  | MVA  | Sum of distribution transformer total capacity (sum of ratings accross the windings) |                                                             |
|                 *nb_1ph_Xfrm*                 | Integer |  -   |              Number of one phase transformers.               |                                                             |
|                 *nb_3ph_Xfrm*                 | Integer |  -   |             Number of three phase transformers.              |                                                             |
|             *Ratio_1phto3ph_Xfrm*             |  Float  |  -   |            *nb_1ph_Xfrm* divided by *nb_3ph_Xfrm*            | if there is no three phase transformer, this metric is Nan. |

### Substations

|        Metric name        |  Type  | Unit |       Metric description        | Comments |
| :-----------------------: | :----: | :--: | :-----------------------------: | :------: |
|     *Substation_Name*     | String |  -   |   The name of the substation.   |          |
| *Substation_Capacity_MVA* | Float  | MVA  | The capacity of the substation. |          |

### Load specification

|            Metric name            |  Type   |       Unit       |                      Metric description                      |          Comments          |
| :-------------------------------: | :-----: | :--------------: | :----------------------------------------------------------: | :------------------------: |
|         *Total_Demand_kW*         |  Float  |      Watts       |                  Total active power demand.                  |                            |
|      *total_demand_phase_A*       |  Float  |      Watts       |            Total active power demand on phase A.             |                            |
|      *total_demand_phase_B*       |  Float  |      Watts       |            Total active power demand on phase B.             |                            |
|      *total_demand_phase_C*       |  Float  |      Watts       |            Total active power demand on phase C.             |                            |
|    *Total_Reactive_Power_kVar*    |  Float  |       Vars       |                 Total reactive power demand.                 |                            |
|   *lv_ph_A_load_kw_percentage*    |  Float  |        -         |  Percentage of low voltage active power demand on phase A.   |                            |
|   *lv_ph_B_load_kw_percentage*    |  Float  |        -         |  Percentage of low voltage active power demand on phase B.   |                            |
|   *lv_ph_C_load_kw_percentage*    |  Float  |        -         |  Percentage of low voltage active power demand on phase C.   |                            |
|         *No_Loads_LV_1ph*         | Integer |        -         |             Number of low voltage, 1 phase loads             |                            |
|         *No_Loads_LV_3ph*         | Integer |        -         |             Number of low voltage, 3 phase loads             |                            |
|         *No_Loads_MV_3ph*         | Integer |        -         |           Number of medium voltage, 3 phase loads            |                            |
|        *No_Loads_per_Xfrm*        |  Float  |        -         |    Average number of loads per distribution transformer.     |                            |
|    *average_load_power_factor*    |  Float  |        -         |               Average power factor for loads.                |                            |
| *average_imbalance_load_by_phase* |  Float  |      Watts       |                             TODO                             |                            |
|         *No_of_Customers*         | Integer |        -         |                     Number of customers.                     | Need customer information. |
|        *customer_density*         |  Float  | per square miles | *No_of_Customers* divided by the convex Hull surface of the feeder. |                            |
|          *load_density*           |  Float  | per square miles | *Total_Demand_kW* divided by the convex Hull surface of the feeder. |                            |
|           *var_density*           |  Float  | per square miles | *Total_Reactive_Power_kVar* divided by the convex Hull surface of the feeder. |                            |

### Graph Topology

|    Metric name     | Type  | Unit |   Metric description   | Comments |
| :----------------: | :---: | :--: | :--------------------: | :------: |
|    *Avg_Degree*    | Float |  -   |      Mean degree.      |          |
| *Char_Path_Length* | Float |  -   |  Average path length.  |          |
|  *Graph_Diameter*  | Float |  -   | Diameter of the graph. |          |



## How to compute the metrics

### Easy situation: compute metrics on a single feeder

#### Method 1: Command Line Interface

Not implemented yet.

#### Method 2: Using a Python script

##### Step 1: Read the model into DiTTo

We assume that we have a model in OpenDSS representing a single feeder, and that we want to compute all the available metrics on it. The first step is to read in the model (more information on reading capabilities in ```cli-examples.md```)

```python
from ditto.model.store import Store 
from ditto.readers.opendss.read import Reader

model = Store() #Create a Store object

#Initialize the reader with the master and coordinate files of our system
dss_reader = Reader(master_file='./OpenDSS/master.dss', 
                    buscoordinates_file='./OpenDSS/buscoords.dss')

#Parse...
dss_reader.parse(model)
```

##### Step 2: Modify the model (optional)

This step is optional but most of the time needed. In our example, since we are reading from OpenDSS, we do not have information on the nominal voltages for ```Nodes``` and ```Lines```. Since a lot of metrics are divided according to low voltage (LV) and medium voltage (MV), we need to add this information.

In this situation, we have the nominal voltage of the source as well as the nominal voltage of the transformers (primary and secondary). We can use the following approach that will go from the source down to the customers and set the nominal voltages of the equipments:

```python
from ditto.modify.system_structure import system_structure_modifier

#Create a system_structure_modifier object
#We can specify the name of the source and its voltage
#Otherwise, the source and its voltage will be search in the model
modifier = system_structure_modifier(model)

#Set the nominal voltages of all nodes in the system
modifier.set_nominal_voltages_recur()

#Use the nodes voltages to set the nominal voltages of the lines
modifier.set_nominal_voltages_recur_line()
```

 This example only shows one of the modification possibilities. More information on modifications and post-processing can be found in ```modifications.md```.

##### Step 3: Compute the metrics

This step of the process creates a ```network_analyzer``` object with the modified model and compute the metrics on it:

```python
from ditto.metrics.network_analysis import network_analyzer

#Instanciate the network_analyzer object
#WARNING: In case the model was modified, we need to use modifier.model
#If we did not do any changes, then simply pass model
#Again, the name of the source can be provided to avoid the search
network_analyst = network_analyzer(modifier.model)

#Compute all the metrics
network_analyst.compute_all_metrics()
```

In this example, we have a single feeder so we call the ```compute_all_metrics()``` method. It is also possible to compute metrics per feeder when we have a system with multiple feeders using the ```compute_all_metrics_per_feeder()``` method. The process might be a bit more complicated since the network has to be properly partitioned. More information for this process is available in the section "Advanced: Compute metrics for multiple feeders".

##### Step 4: View/export the results

The final step of the process is obviously to have a look at the metrics. There are mainly two ways to do so. The first method is simply to look at the ```results``` attribute of the ```network_analyzer```:

```python
print(network_analyst.results)
```

This prints a dictionary where the keys are the feeder names (in our case we have only one key since we have only one feeder), and the values are dictionaries holding the metrics:

```json
{'name_of_feeder1': {'name_of_metric1': value1,
                     'name_of_metric2': value2,
                     ...
                    }
'name_of_feeder2': {'name_of_metric1': value1,
                    'name_of_metric2': value2,
                     ...
                    }
 ...
}
```

Getting a the value of a specific metric for a given feeder:

```python
print(network_analyst.results['name_of_feeder1']['name_of_metric2'])
```

The second method is to export the metrics first and look at the export. The metrics can be exported to Excel using:

```python
#Provide the path to the file
network_analyst.export('./output/metrics.xlsx')
```

Note that this will not export distribution metrics. To export everything in ```network_analyst.results```, use the JSON export method:

```python
network_analyst.export_json('./output/metrics.json')
```



### Advanced: compute metrics for multiple feeders

#### Method 1: Command Line Interface

Not implemented yet.

#### Method 2: Using a Python script

TODO