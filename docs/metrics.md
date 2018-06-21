# Metrics documentation

DiTTo has the capability to extract metrics from a system once parsed in the core representation. This enables the user to compute metrics when doing a conversion from one format to another.

The advantage compared to computing metrics on a given format is that no conversion is needed prior to the caculation.

## List of available metrics

Here is the list of implemented metrics with their description. The list is organized in different sections to ease the search.

### Realistic electrical design and equipment parameters (MV)

|              Metric name              | Type  | Unit  |                      Metric description                      |                   Comments                   |
| :-----------------------------------: | :---: | :---: | :----------------------------------------------------------: | :------------------------------------------: |
|           *mv_len_mi*           | Float | miles |          The total length of medium voltage lines.           |          Needs the nominal voltages          |
|         *mv_3ph_len_mi*          | Float | miles |      The total length of medium voltage, 3 phase lines.      |          Needs the nominal voltages          |
|        *mv_oh_3ph_len_mi*        | Float | miles | The total length of medium voltage, overhead, 3 phase lines. |  Needs the nominal voltages and line_type.   |
|         *mv_2ph_len_mi*          | Float | miles |      The total length of medium voltage, 2 phase lines.      |          Needs the nominal voltages          |
|        *mv_oh_2ph_len_mi*        | Float | miles | The total length of medium voltage, overhead, 2 phase lines. |  Needs the nominal voltages and line_type.   |
|         *mv_1ph_len_mi*          | Float | miles |      The total length of medium voltage, 1 phase lines.      |          Needs the nominal voltages          |
|        *mv_oh_1ph_len_mi*        | Float | miles | The total length of medium voltage, overhead, 1 phase lines. |  Needs the nominal voltages and line_type.   |
| *perct_mv_oh_len* | Float |   -   |       Percentage of MV lines that are overhead lines.        |  Needs the nominal voltages and line_type.   |
| *ratio_mv_len_to_num_cust* | Float | miles |     mv_length_miles devided by the number of customers.      | Needs nominal voltages and load information. |
|        *max_sub_node_distance_mi*        | Float | miles | Maximum distance between the substation and any node of the network. |                                              |
|    *nominal_medium_voltage_class*     | Float | Volts |              Nominal voltage of medium voltage.              |                                              |

### Realistic electrical design and equipment parameters (LV)

|              Metric name              | Type  | Unit  |                      Metric description                      |                   Comments                   |
| :-----------------------------------: | :---: | :---: | :----------------------------------------------------------: | :------------------------------------------: |
|           *lv_len_mi*           | Float | miles |            The total length of low voltage lines.            |          Needs the nominal voltages          |
|         *lv_3ph_len_mi*          | Float | miles |       The total length of low voltage, 3 phase lines.        |          Needs the nominal voltages          |
|        *lv_oh_3ph_len_mi*        | Float | miles |  The total length of low voltage, overhead, 3 phase lines.   |  Needs the nominal voltages and line_type.   |
|         *lv_1ph_len_mi*          | Float | miles |       The total length of low voltage, 1 phase lines.        |          Needs the nominal voltages          |
|        *lv_oh_1ph_len_mi*        | Float | miles |  The total length of low voltage, overhead, 1 phase lines.   |  Needs the nominal voltages and line_type.   |
|    *max_lv_line:*    | Float | miles | The maximum length between a distribution transformer and a low voltage customer. |          Needs the nominal voltages          |
|         *lv_2ph_len_mi*          | Float | miles |       The total length of low voltage, 2 phase lines.        |          Needs the nominal voltages          |
|        *lv_oh_2ph_len_mi*        | Float | miles |  The total length of low voltage, overhead, 2 phase lines.   |  Needs the nominal voltages and line_type.   |
| *perct_lv_oh_len* | Float |   -   |       Percentage of LV lines that are overhead lines.        |  Needs the nominal voltages and line_type.   |
| *ratio_lv_len_to_num_cust* | Float | miles |     lv_length_miles devided by the number of customers.      | Needs nominal voltages and load information. |

### Voltage control schemes

|           Metric name            |  Type   | Unit  |                      Metric description                      |                     Comments                     |
| :------------------------------: | :-----: | :---: | :----------------------------------------------------------: | :----------------------------------------------: |
|        *num_regulators*        | Integer |   -   |               The number of regulator objects.               |                                                  |
|      *num_capacitors*      | Integer |   -   |                The number of capacitor banks.                |                                                  |
|         *num_boosters*         | Integer |   -   |                   The number of boosters.                    | Boosters are not currently implemented in DiTTo. |
| *avg_regulator_sub_distance_mi* |  Float  | miles | Mean distance between the substation and regulator objects.  |       If no regulator, this metric is Nan.       |
| *avg_capacitor_sub_distance_mi* |  Float  | miles | Mean distance between the substation and capacitor bank objects. |       If no capacitor, this metric is Nan.       |

### Basic protection

|           Metric name           |  Type   | Unit  |                     Metric description                     |              Comments              |
| :-----------------------------: | :-----: | :---: | :--------------------------------------------------------: | :--------------------------------: |
|          *num_fuses*          | Integer |   -   |                      Number of Fuses.                      |                                    |
|        *num_reclosers*        | Integer |   -   |                    Number of Reclosers.                    |                                    |
|     *num_sectionalizers*      | Integer |   -   |                 Number of Sectionalizers.                  |                                    |
|  *num_sectionalizers_per_recloser*  |  Float  |   -   |    *No_of_Sectionalizers* divided by *No_of_Reclosers*.    | If no recloser, this metric is Nan |
| *avg_recloser_sub_distance_mi* |  Float  | miles | Mean distance between the substation and recloser objects. | If no recloser, this metric is Nan |
|        *num_breakers*         | Integer |   -   |                    Number of Breakers.                     |                                    |

### Reconfiguration Options

|              Metric name              |  Type   | Unit |                      Metric description                      |                           Comments                           |
| :-----------------------------------: | :-----: | :--: | :----------------------------------------------------------: | :----------------------------------------------------------: |
|           *num_switches*            | Integer |  -   |                     Number of switches.                      |                                                              |
|         *num_interruptors*          | Integer |  -   |                   Number of interruptors.                    |                                                              |
| *num_links_adjacent_feeders* | Integer |  -   | Number of links between the current feeder and other feeders. | This metrics only works when computing metrics per feeder on a system with multiple feeders. |
|       *num_loops*        | Integer |  -   |              Number of loops within the feeder.              |                                                              |

### Transformers

|                  Metric name                  |  Type   | Unit |                      Metric description                      |                          Comments                           |
| :-------------------------------------------: | :-----: | :--: | :----------------------------------------------------------: | :---------------------------------------------------------: |
|       *num_distribution_transformers*       | Integer |  -   |             Number of distribution transformers.             |                                                             |
|      *num_overloaded_transformers*       | Integer |  -   | Number of distribution transformers where its secondary KVA rating is smaller than the sum of downstream load KVA. |                                                             |
| *sum_distribution_transformer_mva* |  Float  | MVA  | Sum of distribution transformer total capacity (sum of ratings accross the windings) |                                                             |
|                 *num_1ph_transformers*                 | Integer |  -   |              Number of one phase transformers.               |                                                             |
|                 *num_3ph_transformers*                 | Integer |  -   |             Number of three phase transformers.              |                                                             |
|             *ratio_1ph_to_3ph_transformers*             |  Float  |  -   |            *nb_1ph_Xfrm* divided by *nb_3ph_Xfrm*            | if there is no three phase transformer, this metric is Nan. |

### Substations

|        Metric name        |  Type  | Unit |       Metric description        | Comments |
| :-----------------------: | :----: | :--: | :-----------------------------: | :------: |
|     *substation_name*     | String |  -   |   The name of the substation.   |          |
| *sub_capacity_mva* | Float  | MVA  | The capacity of the substation. |          |

### Load specification

|            Metric name            |  Type   |       Unit       |                      Metric description                      |          Comments          |
| :-------------------------------: | :-----: | :--------------: | :----------------------------------------------------------: | :------------------------: |
|         *sum_load_kw*         |  Float  |      Watts       |                  Total active power demand.                  |                            |
|      *sum_load_pha_kw*       |  Float  |      Watts       |            Total active power demand on phase A.             |                            |
|      *sum_load_phb_kw*       |  Float  |      Watts       |            Total active power demand on phase B.             |                            |
|      *sum_load_phc_kw*       |  Float  |      Watts       |            Total active power demand on phase C.             |                            |
|    *sum_load_kvar*    |  Float  |       Vars       |                 Total reactive power demand.                 |                            |
|   *perct_lv_pha_load_kw*    |  Float  |        -         |  Percentage of low voltage active power demand on phase A.   |                            |
|   *perct_lv_phb_load_kw*    |  Float  |        -         |  Percentage of low voltage active power demand on phase B.   |                            |
|   *perct_lv_phc_load_kw*    |  Float  |        -         |  Percentage of low voltage active power demand on phase C.   |                            |
|         *num_lv_1ph_loads*         | Integer |        -         |             Number of low voltage, 1 phase loads             |                            |
|         *num_lv_3ph_loads*         | Integer |        -         |             Number of low voltage, 3 phase loads             |                            |
|         *num_mv_3ph_loads*         | Integer |        -         |           Number of medium voltage, 3 phase loads            |                            |
|        *avg_num_load_per_transformer*        |  Float  |        -         |    Average number of loads per distribution transformer.     |                            |
|    *avg_load_pf*    |  Float  |        -         |               Average power factor for loads.                |                            |
| *avg_load_imbalance_by_phase* |  Float  |      Watts       |                             TODO                             |                            |
|         *num_customers*         | Integer |        -         |                     Number of customers.                     | Need customer information. |
|        *customer_density*         |  Float  | per square miles | *No_of_Customers* divided by the convex Hull surface of the feeder. |                            |
|          *load_density_kw*           |  Float  | per square miles | *Total_Demand_kW* divided by the convex Hull surface of the feeder. |                            |
|           *load_density_kvar*           |  Float  | per square miles | *Total_Reactive_Power_kVar* divided by the convex Hull surface of the feeder. |                            |

### Graph Topology

|    Metric name     | Type  | Unit |   Metric description   | Comments |
| :----------------: | :---: | :--: | :--------------------: | :------: |
|    *avg_degree*    | Float |  -   |      Mean degree.      |          |
| *Char_path_Length* | Float |  -   |  Average path length.  |          |
|  *diameter*  | Float |  -   | Diameter of the graph. |          |



## How to compute the metrics

### Easy situation: compute metrics on a single feeder

#### Method 1: Command Line Interface

Not implemented yet.

#### Method 2: Using a Python script

##### Step 1: Read the model into DiTTo

We assume that we have a model in OpenDSS representing a single feeder, and that we want to compute all the available metrics on it. The first step is to read in the model (more information on reading capabilities in `cli-examples.md`)

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

 This example only shows one of the modification possibilities. More information on modifications and post-processing can be found in `modifications.md`

##### Step 3: Compute the metrics

This step of the process creates a `NetworkAnalyzer` object with the modified model and compute the metrics on it:

```python
from ditto.metrics.network_analysis import NetworkAnalyzer

#Instanciate the NetworkAnalyzer object
#WARNING: In case the model was modified, we need to use modifier.model
#If we did not do any changes, then simply pass model
#Again, the name of the source can be provided to avoid the search
network_analyst = NetworkAnalyzer(modifier.model)

#Compute all the metrics
network_analyst.compute_all_metrics()
```

In this example, we have a single feeder so we call the `compute_all_metrics()` method. It is also possible to compute metrics per feeder when we have a system with multiple feeders using the `compute_all_metrics_per_feeder()` method. The process might be a bit more complicated since the network has to be properly partitioned. More information for this process is available in the section "Advanced: Compute metrics for multiple feeders".

##### Step 4: View/export the results

The final step of the process is obviously to have a look at the metrics. There are mainly two ways to do so. The first method is simply to look at the `results` attribute of the `NetworkAnalyzer`:

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

Note that this will not export distribution metrics. To export everything in `network_analyst.results` use the JSON export method:

```python
network_analyst.export_json('./output/metrics.json')
```



### Advanced: compute metrics for multiple feeders

#### Method 1: Command Line Interface

Not implemented yet.

#### Method 2: Using a Python script

It is also possible to extract metrics when we have a system composed of multiple feeders. In this situation, we might want to:

-  compute the metrics on the whole system
- compute the metrics for all feeders

The first point is straightforward, just proceed as for the single feeder case.

##### Step 1 and 2: Read and modify as before

For computing metrics per feeder, we first read the model into DiTTo and apply, if needed, modifications to it (exactly as for the single feeder case):

```python
from ditto.model.store import Store
from ditto.readers.opendss.read import Reader
from ditto.modify.system_structure import system_structure_modifier

model = Store() #Create a Store object

#Initialize the reader with the master and coordinate files of our system
dss_reader = Reader(master_file='./OpenDSS/master.dss',
                    buscoordinates_file='./OpenDSS/buscoords.dss')

#Parse...
dss_reader.parse(model)

#Create a system_structure_modifier object
#We can specify the name of the source and its voltage
#Otherwise, the source and its voltage will be search in the model
modifier = system_structure_modifier(model)

#Set the nominal voltages of all nodes in the system
modifier.set_nominal_voltages_recur()

#Use the nodes voltages to set the nominal voltages of the lines
modifier.set_nominal_voltages_recur_line()
```

##### Step 3: Create a network analyzer

We then create a `NetworkAnalyzer` object as for the single feeder case:

```python
from ditto.metrics.network_analysis import NetworkAnalyzer

#Instanciate the NetworkAnalyzer object
network_analyst = NetworkAnalyzer(modifier.model)
```

##### Step 4: Provide information on the feeder compositions

Now, we need to provide feeder information to the `NetworkAnalyzer` using the `add_feeder_information()` method wich takes the following inputs:

- `feeder_names` List of names for the feeders
- `feeder_nodes` List of lists which contains all nodes in the feeders. Thats is, `feeder_nodes[2]`is the full list of nodes belonging to `feeder_names[2]`
- `substations` List of the substation names.
- `feeder_types` This could be a list of strings to tag each feeder with a type (`industrial` `rural` or a single string to tag all feeders with the same type.

Example:

```python
#Fake feeder information
feeder_names = ['feeder_1', 'feeder_2', 'feeder_3']
feeder_nodes = [ ['A','B','C'], ['D','E','F','G','H'], ['I','J','K','L']]
substations = ['sub_1', 'sub2', 'sub3']
feeder_types = ['industrial', 'rural', 'urban']

#Add the feeder information to the network analyzer
network_analyst.add_feeder_information(feeder_names, feeder_nodes, substations, feeder_types)
```

This means that you currently have to generate the 4 arguments yourself. Algorithms to automatically split a given network into multiple feeders are currently tested yet but none has been released yet.

##### Step 5: Split the network and compute the metrics

Once this is done, we simply have to call the following methods:

```python
#Split the network representation into multiple subnetworks
network_analyst.split_network_into_feeders()

#Loop over the DiTTo objects and set the feeder_name attribute
network_analyst.tag_objects()

#Set the names
network_analyst.model.set_names()

#Compute the metrics per feeders
network_analyst.compute_all_metrics_per_feeder()
```

#### Step 6: Export the metrics

This works exactly as for the single feeder case.
