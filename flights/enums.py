from enum import Enum

class BookingState(Enum):
    SEARCH = 'search'
    SELECTION = 'selection'
    SEATS = 'seats'
    PASSENGERS = 'passengers'
    PAYMENT = 'payment'
    CONFIRMATION = 'confirmation' 