import os
import tempfile

from typing import Optional, Tuple
from datetime import datetime, timedelta

class Logger:
    __logFilePath: Optional[str] = None
    __writeToFile: bool = False
    __dateFormat: str = "%d-%m-%Y"
    __timeFormat: str = "%H:%M:%S"
    __logDir: str = "Logs"
    __maxLogSize: int = 62914560
    __maxLogAgeDays: int = 30
    __autoDeleteLogFiles: bool = True

    def __init__(self, message: str, level: str = "info"):
        """
        :param message: The logging message
        :type message: str
        
        :param level: Message importance level (info, warn, crit, error, debug)
        :type level: str

        :raises ValueError: 
        - Invalid logging level is passed

        :raises PermissionError: 
        - There are no write permissions to the log file

        :raises OSError: 
        - File system errors (for example, the disk is full)

        :raises Exception: 
        - In case of other unexpected errors
        
        Example usage:

        .. code-block:: python
            Log("Hello world!", "info")        # Information Message
            Log("Warning!", "warn")            # Warning Message
            Log("It's Error!!", "error")       # Eror Message
            Log("Critical Error!", "crit")     # Critical Error Message
            Log("System is connect", "debug")  # Debug Message

        Note: Even if an error occurs when writing to a file, the message will always 
            be output to the console.
        """

        level = level.upper()
        valid_levels = {"INFO", "WARN", "CRIT", "ERROR", "DEBUG"}

        if level not in valid_levels:
            raise ValueError(f"Invalid log level '{level}'. Valid levels are: {', '.join(valid_levels)}")

        timestamp = datetime.now().strftime(f"{Logger.__dateFormat}-{Logger.__timeFormat}")

                

        log_entry = f"{level} || {timestamp} || {message}"

        print(log_entry)

        if Logger.__writeToFile and Logger.__logFilePath:
            try:
                with open(Logger.__logFilePath, "a") as log_file:
                    log_file.write(log_entry + "\n")

                self._clean_old_logs()

            except (PermissionError, OSError) as e:
                error_time = datetime.now().strftime(f"{self.__dateFormat}-{self.__timeFormat}")
                print(f"ERROR || {error_time} || Failed to write to log file: {e}")
                raise

            except Exception as e:
                error_time = datetime.now().strftime(f"{self.__dateFormat}-{self.__timeFormat}")
                print(f"ERROR || {error_time} || Unexpected error: {e}")
                raise


    @classmethod
    def _clean_old_logs(cls) -> None:
        """Deletes old and large log files"""

        if cls.__autoDeleteLogFiles:

            if not os.path.exists(cls.__logDir):
                return

            now = datetime.now()
            max_age = timedelta(days=cls.__maxLogAgeDays)

            for filename in os.listdir(cls.__logDir):
                if filename.endswith(".log"):
                    filepath = os.path.join(cls.__logDir, filename)
                    try:
                        file_stat = os.stat(filepath)
                        file_size = file_stat.st_size
                        file_age = now - datetime.fromtimestamp(file_stat.st_ctime)

                        if file_size > cls.__maxLogSize or file_age > max_age:
                            os.remove(filepath)

                    except Exception as e:
                        print(f"Failed to process log file {filename}: {e}")


    @classmethod
    def setupLogging(cls, log_dir: str = "logs",
                     write_to_file: bool = True,
                     auto_delete_logs: bool = True,
                     max_log_size: int = 62914560,
                     max_log_age_days: int = 30) -> Tuple[bool, str]:
        
        """
        Configures the logging system
        
        :param log_dir: The path to the logs folder
        :type log_dir: str
        
        :param write_to_file: Enable writing to a file
        :type write_to_file: bool

        :param auto_delete_logs: Auto-delete old and large log files (1 month ago or 60 Mb)
        :type auto_delete_logs: bool
        
        :return: Tuple (success, error message)
        :rtype: Tuple[bool, str]

        :raises ValueError:
        - Incorrect date/time format was transmitted
        - log_dir contains invalid characters
    
        :raises PermissionError:
        - No rights to create a directory
        - No rights to write to the directory
            
        :raises OSError:
        - The directory cannot be created
        - The disk is full
        - File System errors
            
        :raises RuntimeError:
        - Failed to create a test file
        - Failed to initialize the log file
        
        Note: If errors occur, the logging system will continue to work.,
                    but the recording will only be done in the console.
        """
    
        try:
            with tempfile.NamedTemporaryFile(suffix=".log", delete=True) as temp_file:
                temp_file.write(b"test")

        except IOError as e:
            return False, f"File creation test failed: {e}"
        

        cls.__writeToFile = write_to_file
        cls.__logDir = log_dir
        cls.__autoDeleteLogFiles = auto_delete_logs
        cls.__maxLogAgeDays = max_log_age_days
        cls.__maxLogSize = max_log_size


        if write_to_file:
            try:
                os.makedirs(log_dir, exist_ok=True)
                timestamp = datetime.now().strftime(f"{cls.__dateFormat}-{cls.__timeFormat}".replace(":", "."))
                log_path = os.path.join(log_dir, f"{timestamp}.log")

                with open(log_path, "a", encoding="utf-8") as f:
                    f.write("Logging started\n")

                cls.__logFilePath = log_path
                return True, "Logging setup successfully"

            except Exception as e:
                cls.__writeToFile = False
                return False, f"Log file creation failed: {e}"
            
        return True, "Console logging only"