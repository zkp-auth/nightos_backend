class BookingConflictError(Exception):
    """
    Raised when a booking conflicts with an existing venue or DJ schedule.
    """
    pass