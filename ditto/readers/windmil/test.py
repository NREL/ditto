from ditto.readers.windmil.read import Reader
from ditto.writers.opendss.write import Writer
from ditto.store import Store

m=Store()
windmil_reader=Reader()
windmil_reader.parse(m)
OpenDSS_writer=Writer()
OpenDSS_writer.write(m)


