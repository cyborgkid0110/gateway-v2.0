import logging

class Log():
    def __init__(self, name):
        self.__name = name

       # Loggers
        self.__logger = logging.getLogger(self.__name)
        self.__logger.setLevel(logging.DEBUG)

        # Formatters
        self.__formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%d/%m/%Y %H:%M:%S %p")

        # Handlers
        self.__fileHandler = logging.FileHandler("gateway.log") 
        self.__fileHandler.setLevel(logging.DEBUG)
        self.__fileHandler.setFormatter(self.__formatter)

        self.__logger.addHandler(self.__fileHandler)
    
    def debug(self, mes):
        """Use for debug process"""
        self.__logger.debug(mes)

    def info(self, mes):
        """Use for watching logics flow"""
        self.__logger.info(mes)

    def error(self, mes):
        """Use when there is an exception happened but not tracing back"""
        self.__logger.error(mes)

    def exception(self, mes):
        """Use when there is an exception happened"""
        self.__logger.exception(mes)

if __name__=="__main__":
    pass