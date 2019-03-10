import json
import os

class Config:
    @staticmethod
    def _loadConfig():
        """ Loads the configuration file and returns it """
        current_path = os.path.dirname(os.path.abspath(__file__))
        config_file = open(current_path+"/../settings.json")
        return config_file

    @classmethod
    def _trimArray(cls, array):
        """ Removes empty items in an array  """
        if len(array) > 0:
            if(array[0] == ""):
                array.pop(0)
            if array[-1] == "":
                array.pop(-1)

    @classmethod
    def get(cls, property_path, optional = False):
        """ Reads a part of the configuration provided with a property path """
        try:
            config_file = cls._loadConfig()
            config_json = json.loads(config_file.read())
        except:
            print("There is something wrong in your settings.json! Invalid JSON format. Maybe you have set a , wrong?")
            exit(1)

        try:
            property_path_array = property_path.split("/")
            searched_object = config_json
            cls._trimArray(property_path_array)
            i = 0
            while len(property_path_array) > i:
                searched_object = searched_object[property_path_array[i]]
                i += 1
            return searched_object
        except:
            if optional == False:
                print("You have missed to specify "+property_path+" in the settings.json")
            return False