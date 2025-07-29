from typing import TypedDict
# TODO : select a data structure

class User_Dto_as_Dict(TypedDict):
    """
   Data Transfer Object (DTO) representing a user with optional settings.

   Attributes:
       Username (str): Username as a string.
       Email (str): User email.
       UserId (str): Unique identifier for the user (e.g., UID from Firebase).
       Settings (Optional[dict]): Optional dictionary containing user settings.
   """
    Username: str
    Email: str
    UserId: str
    Settings: list


 