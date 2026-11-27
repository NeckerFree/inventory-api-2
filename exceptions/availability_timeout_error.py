#file: exceptions/availability_timeout_error.py
class AvailabilityTimeOutError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)