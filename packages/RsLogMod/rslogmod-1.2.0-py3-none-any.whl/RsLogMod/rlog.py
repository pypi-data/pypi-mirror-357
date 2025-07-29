from .bin.rslogmod import Logger


def rlog(log_file_name: str = None, log_level: int = None, log_entry: str = None, verbose: bool = False):
    logger = Logger(log_name=log_file_name, log_level=log_level, log_entry=log_entry, verbose=verbose)
    logger.log()
