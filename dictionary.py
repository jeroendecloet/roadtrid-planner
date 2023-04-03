from enum import Enum


class BaseLanguage(Enum):
    @classmethod
    def get_names_values(cls):
        return {x.name: x.value for x in cls}


class English(BaseLanguage):

    # Popup
    website = "website"
    price = "price"
    free = "free"
    availability = "availability"


class Nederlands(BaseLanguage):

    # Popup
    website = "website"
    price = "prijs"
    free = "gratis"
    availability = "beschikbaarheid"

