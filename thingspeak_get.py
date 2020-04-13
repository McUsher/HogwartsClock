import thingspeak
import threading
import logging

DEBUG_TEMP = -12

class ThingspeakData():

    def __init__(self):
        self.__setDefault()
    
    def __setDefault(self):
        self.api_key = None
        self.channel_id = None
        self.field_id = None
        self.max_data_age = None
        self.update_time_seconds = 0
    
    def update(self, json):
        try:
            self.api_key = json["apiKey"]
            self.channel_id = json["channelID"]
            self.field_id = json["fieldID"]
            self.update_time_seconds = 60 * json["updateMinutes"]
            self.max_data_age = 60 * json["maxDataAgeMinutes"]
        except Exception as e:
            logging.error(f"could not parse json, {e}")
            self.__setDefault()

    def get_channel(self):
        return thingspeak.Channel(api_key=self.api_key, timeout=10, id=self.channel_id)
    
    def __str__(self):
        return f"ThingSpeakData(field={self.field_id},update_time={self.update_time_seconds}, max_data_age={self.max_data_age}, api_key={self.api_key}, channel_id={self.channel_id})"
        

class ThingSpeakRetriever():
    """
    if updateTimeSecons set to 0 no temperature will be retrieved....
    """
    def __init__(self):
        self.data = ThingspeakData()
        self.update_time_seconds = 0
        self.current_value_string = "-"
        
    def update_data(self, json):
        self.data.update(json)
        logging.info(self.data)
        self.channel = self.data.get_channel()
        self.current_value_string = "-"
        self.update_time_seconds = self.data.update_time_seconds
        if(self.update_time_seconds <= 0):
            logging.warn("Warning! No temperature will be received... set update_time_seconds > 0")
        self.__update()
        
    def __update(self):
        try:
            if(self.update_time_seconds <= 0):
                self.__set_value(DEBUG_TEMP if self.update_time_seconds == -60 else None)
                return
            
            """ first check, if the data is recent...."""
            result = self.channel.get_last_data_age(self.data.field_id)
            last_update = eval(result)
            logging.info(last_update)
            if(last_update["last_data_age_units"] != "s"):
                """ last data age units is not seconds... cannot parse..."""
                self.__set_value(None, errorCode=1)
                self.__start_update_timer()
                return
            if(int(last_update["last_data_age"]) > self.data.max_data_age):
                """ last data is too old... """
                logging.warn(f"data too old -> {last_update}")
                self.__set_value(None, errorCode=2)
                self.__start_update_timer()
                return
            
            result = eval(self.channel.get_field_last(self.data.field_id))
            self.__set_value(float(result[f"field{self.data.field_id}"]))
        except Exception as e:
            logging.error(f"exeption in retrieving data, {e}")
            logging.error(result)
            self.__set_value(None, 3);
        finally:
            self.__start_update_timer()
            
    def __start_update_timer(self):
        if(self.update_time_seconds > 0):
            thread = threading.Timer(self.update_time_seconds, self.__update)
            thread.setDaemon(True)
            thread.start()

    def __set_value(self, temperature, errorCode=0):
        self.current_value = temperature if temperature else 0
        if(errorCode > 0):
            self.current_value_string = "E{}".format(errorCode)
        elif(temperature is None):
            self.current_value_string = "-"
        else:
            self.current_value_string = "{}".format(int(round(temperature, 0)))
        logging.info(f"CurrentValue.set={self.current_value_string}")
