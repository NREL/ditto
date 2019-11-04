import os, pathlib
from GIS_Reader import Reader
from DSS_Writer import Writer
import pickle


class Generator:

    def __init__(self, settings,mapper):

        self.__settings = settings
        self.__create_scenario_dict()
        self.__pathlist()
        self.mapper = mapper
        self.__generatedssfiles()
       
        
    
    def __create_scenario_dict(self):
        scenario_dict = {}
        scenario_dict['Base'] = {'PPV_customers': 0, 'PPV_capacity': 0}
        for i in range(self.__settings['PV_capacity_step']):
            for j  in range(self.__settings['PV_customers_step']):
                customer = 100*(j+1)/(self.__settings['PV_customers_step'])
                capacity = 100*(i+1)/(self.__settings['PV_capacity_step'])
                scenario_dict[str(customer) + '%-customer-'+str(capacity)+'%-PV'] = {'PPV_customers': customer , 'PPV_capacity':capacity }

        self.__scenariodict = scenario_dict
    
    def __pathlist(self):
        self.__rootpath = self.__settings['Project path']
        self.__GISdata = os.path.join(self.__rootpath,'GIS_Feeder_Data')
        self.__exportDSSpath = os.path.join(self.__rootpath,'Exported_DSS_files')

    
    def __modify_name(self,name):
        if ' ' in name:
            name = name.replace(' ', '-')
        return name


    def __generatedssfiles(self):

        list_of_folders = os.listdir(self.__GISdata)
        print(list_of_folders)
        for i in range(len(list_of_folders)): 
            path = os.path.join(self.__GISdata,list_of_folders[i])
            list_of_files = os.listdir(path)
            this_network = Reader(list_of_files,path, list_of_folders[i],self.mapper)
            path_toexport = self.__exportDSSpath + '/' + self.__modify_name(list_of_folders[i])+'__DSS_files'
            if os.path.exists(path_toexport) !=True:  os.mkdir(path_toexport)
            for keys,values in self.__scenariodict.items():
                print('----------------------'+ keys+ 'Scenario' + '--------------------')
                print('-----------------------------------------------------------------------------')

                if values['PPV_capacity'] in [0,100] and values['PPV_customers'] in [0,100]:
                    Writer(this_network, path_toexport +'/'+keys, list_of_folders[i], values['PPV_customers'],values['PPV_capacity'],self.__rootpath,self.mapper)
                
                else:
                    for j in range(self.__settings['number_of_monte_carlo_run']):
                        Writer(this_network, path_toexport +'/'+keys, list_of_folders[i], values['PPV_customers'],values['PPV_capacity'],self.__rootpath,self.mapper)



