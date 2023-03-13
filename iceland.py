import json
from typing import Any
from geopy.geocoders import Nominatim
import folium


class MapItems:

    def __init__(self, d=None):
        if d is None:
            self.d = dict()
        else:
            self.d = d

    def __getitem__(self, keys):

        if isinstance(keys, str):
            keys = [keys]

        result = self.d
        for key in keys:
            result = self.d[key]
        return result

    def __setitem__(self, keys, val):

        if isinstance(keys, str):
            keys = [keys]

        _d = self[keys[:-1]]

        key = keys[-1]
        # if key in _d.keys() and isinstance(_d[key], dict) and isinstance(val, dict):
        #     _d[key] = {**_d[key], **val}
        # else:
        _d[key] = val

    def to_json(self, filename: str) -> None:
        """Saves a json file"""
        with open(filename, 'w') as json_file:
            json.dump(self.d, json_file, indent=4)

    @classmethod
    def from_json(cls, filename: str) -> Any:
        """Loads a json file"""
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        return cls(d=data)


class Locator:

    def __init__(self):
        self.locator = Nominatim(user_agent="GetLoc")

    def get_coordinates(self, location: str, additional_info: str):
        """ Gets the latitude and longitude of a location. Additional information can be supplied, such as a country."""
        loc = self.locator.geocode(' '.join([location, additional_info]), language='nl')
        if loc is None:
            print(f"{location} not found!")
            return None, None
        else:
            return [loc.latitude, loc.longitude]


class MapMaker:

    def __init__(self, map_item_filename=None):

        if map_item_filename is not None:
            self.mi = MapItems.from_json(map_item_filename)
        else:
            self.mi = MapItems()

        self.base_map = None

    def create_map(self) -> None:
        self.base_map = folium.Map(location=self.mi['main']['coordinates'], control_scale=True, zoom_start=7)

    @staticmethod
    def create_icon(icon):
        if icon == 'bed':
            return folium.Icon(color="green", icon="bed", prefix='fa')
        elif icon == 'location':
            return folium.Icon(color='blue', icon='location-dot', prefix='fa')
        elif icon == 'landmark':
            return folium.Icon(color='red', icon='landmark', prefix='fa')
        else:
            raise ValueError(f"Icon {icon} not recognized!")

    def add_markers(self, locations: dict[str, dict], icon: str) -> None:
        for loc, info_dict in locations.items():
            assert "coordinates" in info_dict.keys(), f"{loc} is missing coordinates!"

            folium.Marker(
                location=info_dict["coordinates"],
                # popup="something",
                # popup=" ".join([loc, info_dict['info']]),
                popup=folium.Popup(" ".join([loc, info_dict['info']]), parse_html=True),
                icon=self.create_icon(icon)
            ).add_to(self.base_map)

    def save_map(self, filename):
        self.base_map.save(filename)

    def main(self):
        self.create_map()
        self.add_markers(self.mi['landmarks'], icon='landmark')


if __name__ == "__main__":
    mm = MapMaker(map_item_filename="iceland_map_items.json")

    mm.main()

    mm.save_map("IcelandMap.html")
