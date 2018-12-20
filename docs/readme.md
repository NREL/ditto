# Introduction

DiTTo implements a many-to-one-to-many architecture, meaning that a distribution system is represented in a core structure whithin DiTTo and that parsers need to be developped to link this core representation to existing formats.

These parsers can be classified in:

- ```readers``` which read from an existing format such as ```OpenDSS``` and build the core representation with the input data
- ```writers``` which ouptut the core representation to a given existing format.

The main strength of this approach compared to classic one-to-one mappings lies in its modularity. When implementing a new reader for a given format, the capability to export to all supported formats comes for free.

## Readers

### Available

Here is a list of the available readers and their status:

| Readers  | Version assumed |       Implementation stage        |
| :------: | :-------------: | :-------------------------------: |
| OpenDSS  |      todo       |         tested and stable         |
|   CYME   |      todo       |         tested and stable         |
| GridlabD |      todo       |    stable, needs more testing     |
| Synergi  |      todo       |             untested              |
|   DEW    |      todo       | untested, still under development |
| WindMill |      Todo       | Untested, still under development |

There are two slightly different readers available: ```CSV``` and ```JSON``` which are not distribution system modeling formats but data representation formats. The readers can be used to load objects into DiTTo from basic ```CSV``` or ```JSON``` formats. They can be extremely useful for dumping a DiTTo model as is on disk and reload it later, or to apply specific modifications to existing DiTTo models (see more on TODO).

### Planned

Here is a list of readers we wish to implement in a near future. All contributions are welcome!

- CIM
- Ephasor

## Writers

### Available

Here is a list of the available writers and their status:

| Writers  | Version assumed |       Implementation stage        |
| :------: | :-------------: | :-------------------------------: |
| OpenDSS  |      todo       |         tested and stable         |
|   CYME   |      todo       |         tested and stable         |
| Ephasor  |      todo       |             Untested              |
| GridlabD |      todo       | Untested, still under development |

As for ```readers``` the JSON writer enables one to save a raw DiTTo model to disk.

### Planned

Here is a list of the writers we wish to implement in a near future. All contributions are welcome!

- WindMill
- Synergi
- DEW
- CIM
- CSV


