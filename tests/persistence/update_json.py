from ditto.store import Store
from ditto.writers.json.write import Writer
from ditto.readers.cyme.read import Reader as Reader_cyme
from ditto.readers.opendss.read import Reader as Reader_opendss
import os

def update_persistence_jsons():
    test_list = os.walk('data')
    for (dirpath, dirname, files) in test_list:
        if files !=[]:
            reader_type = dirpath.split('\\')[2]
            m = Store()
            if reader_type == 'opendss':
                reader = Reader_opendss(master_file = os.path.join('..',dirpath,'master.dss'), buscoordinates_file = os.path.join('..',dirpath,'buscoord.dss'))
            elif reader_type == 'cyme':
                reader = Reader_cyme(data_folder_path=os.path.join('..',dirpath),load_filename="load.txt", network_filename="network.txt", equipment_filename="equipment.txt")
            else:
                #Update with other tests if they get added to the persistence tests
                continue
            reader.parse(m)
            m.set_names()
            print("Writing "+dirpath)
            w = Writer(output_path=dirpath, log_path=dirpath)
            w.write(m)

if __name__ == '__main__':
    update_persistence_jsons()
