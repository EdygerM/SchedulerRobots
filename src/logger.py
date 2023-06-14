import logging


def setup_logging(log_level, log_format, log_file, log_mode) -> None:
    """
    Set up logging based on the provided parameters.

    This method configures the logging module with the specified log level, log format, log file, and log mode.

    Args:
        log_level (str): The desired log level.
        log_format (str): The format of log messages.
        log_file (str): The file to write logs to.
        log_mode (str): The mode to open the log file in.

    Returns:
        None
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        filename=log_file,
        filemode=log_mode
    )
