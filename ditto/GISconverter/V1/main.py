
import os,pathlib
import toml
from Generate_DSS_files import Generator


def Generate_opendss_files(setting_toml_file,mapper_toml_file):

    texts = ''
    f = open(setting_toml_file, "r")
    text = texts.join(f.readlines())
    settings_dict = toml.loads(text,_dict=dict)

    texts = ''
    f = open(mapper_toml_file, "r")
    text = texts.join(f.readlines())
    mapping_dict = toml.loads(text,_dict=dict)
    print(mapping_dict)
    Generator(settings_dict,mapping_dict)


if __name__ == '__main__':
    setting_toml_file = r'C:\Users\KDUWADI\Box\India Foundations\CIFF 5 Year Files\Trips in 2019\November 2019 trip\Auroville\Feeder_folder\scenario.toml'
    mapper_toml_file = r'C:\Users\KDUWADI\Box\India Foundations\CIFF 5 Year Files\Trips in 2019\November 2019 trip\Auroville\Feeder_folder\mapper.toml'
    Generate_opendss_files(setting_toml_file,mapper_toml_file)
    print('File generation complete !!!')



