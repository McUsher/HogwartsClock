import thingspeak
import threading

DEBUG_TEMP = 88

class ThingSpeakRetriever():
    """
    if updateTimeSecons set to 0 no temperature will be retrieved....
    """

    def __init__(self):
        self.channel = thingspeak.Channel(api_key="9CVMW3DUPBI66IYE", timeout=10, id=938251)
        self.updateTimeSeconds = 0
        self.currentTemp = "-"
        self.__update()
        
    def set_update_time(self, minutes):
        self.updateTimeSeconds = minutes * 60
        if(self.updateTimeSeconds <= 0):
            print("Warning! No temperature will be received... set updateTimeSeconds > 0")
        self.__update()
        
    def __update(self):
        try:
            if(self.updateTimeSeconds <= 0):
                self.__setTemp(DEBUG_TEMP if self.updateTimeSeconds == -60 else None)
                return
            
            """ first check, if the data is recent...."""
            result = self.channel.get_last_data_age(1)
            lastUpdate = eval(result)
            
            if(lastUpdate["last_data_age_units"] != "s"):
                """ last data age units is not seconds... cannot parse..."""
                self.__setTemp(None, errorCode=1)
                self.__setUpdateTemperature()
                return
            if(int(lastUpdate["last_data_age"]) > 30 * 60):
                """ last data is too old... """
                self.__setTemp(None, errorCode=2)
                self.__setUpdateTemperature()
                return
            
            result = eval(self.channel.get_field_last(1))
            self.__setTemp(float(result["field1"]))
        except:
            print ("CATCH")
            self.__setTemp(None, 3);
        finally:
            self.__setUpdateTemperature()
            
    def __setUpdateTemperature(self):
        if(self.updateTimeSeconds > 0):
            thread = threading.Timer(self.updateTimeSeconds, self.__update)
            thread.setDaemon(True)
            thread.start()

    def __setTemp(self, temperature, errorCode=0):
        if(errorCode > 0):
            self.currentTemp = "E{}".format(errorCode)
        elif(temperature is None):
            self.currentTemp = "-"
        else:
            self.currentTemp = "{}".format(int(round(temperature, 0)))
        print("CurrentTemp.set:{}".format(self.currentTemp))
