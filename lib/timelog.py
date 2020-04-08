import logging
import time


class Timelog():
    """
        helper to log time passed....
        uses logging.DEBUG
    """
    def __init__(self, idx, formatT=None, loglevel=logging.DEBUG):
        """
            format can be 's', 'ms', 'us', 'ns'
             None = 'ms'  
        """
        
        self.id = idx
        self.start = time.time_ns()
        self.format = formatT if formatT else "ms"
        self.loglevel = loglevel
        
    def out(self, comment, reset=True):
        passed = time.time_ns()-self.start
        if self.format == "s":
            timepassed =  "{}s".format(int(passed/1000000000))
        elif self.format == "ms":
            timepassed =  "{}ms".format(int(passed/1000000))
        elif self.format == "us":
            timepassed =  "{}us".format(int(passed/1000))
        elif self.format == "ns":
            timepassed =  "{}ns".format(int(passed/1))
            
        outstr = f"Time for {self.id} | {comment}: {timepassed}"
        logging.log(self.loglevel, outstr)
        if reset:
            self.start = time.time_ns()
        
        
    
        