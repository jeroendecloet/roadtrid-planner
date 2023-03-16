import sys
import json
from typing import Any, Union
from geopy.geocoders import Nominatim
import folium


class MapItems:

    def __init__(self, d=None, filename=None):
        if d is None:
            self.d = dict()
        else:
            self.d = d

        self.filename = filename

    def __getitem__(self, keys: Union[list, str]) -> dict:

        if isinstance(keys, str):
            keys = [keys]

        result = self.d
        for key in keys:
            result = result[key]
        return result

    def __setitem__(self, keys: Union[list, str], val: Any) -> None:

        if isinstance(keys, str):
            keys = [keys]

        _d = self[keys[:-1]]

        key = keys[-1]
        # if key in _d.keys() and isinstance(_d[key], dict) and isinstance(val, dict):
        #     _d[key] = {**_d[key], **val}
        # else:
        _d[key] = val

    def to_json(self, filename: str = None) -> None:
        """Saves a json file"""
        if filename is None:
            if self.filename is None:
                raise ValueError("No filename is given, so cannot save MapItems!")
            else:
                filename = self.filename

        with open(filename, 'w') as json_file:
            json.dump(self.d, json_file, indent=4, sort_keys=True)

    @classmethod
    def from_json(cls, filename: str) -> Any:
        """Loads a json file"""
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        return cls(d=data, filename=filename)


class Locator:

    def __init__(self):
        self.locator = Nominatim(user_agent="GetLoc")

    def __call__(self, *args, **kwargs):
        return self.get_coordinates(*args, **kwargs)

    def get_coordinates(self, location: str, additional_info: str) -> list[Union[float, None]]:
        """ Gets the latitude and longitude of a location. Additional information can be supplied, such as a country."""
        _loc_query = ' '.join([location, additional_info])
        print(f"Getting location for {_loc_query}...")
        loc = self.locator.geocode(_loc_query, language='nl')
        if loc is None:
            print(f"{location} not found!")
            return [None, None]
        else:
            print("Success!")
            return [loc.latitude, loc.longitude]


class MapMaker:

    def __init__(self, map_item_filename=None):

        if map_item_filename is not None:
            self.mi = MapItems.from_json(map_item_filename)
        else:
            self.mi = MapItems()

        self.locator = Locator()

        self.base_map = None

    def create_map(self) -> None:
        self.base_map = folium.Map(location=self.mi['main']['coordinates'], control_scale=True, zoom_start=7)

    @staticmethod
    def create_icon(icon) -> folium.Icon:
        if 'hotel' in icon:
            return folium.Icon(color="green", icon="bed", prefix='fa')
        elif icon == 'location':
            return folium.Icon(color='blue', icon='location-dot', prefix='fa')
        elif 'landmark' in icon:
            return folium.Icon(color='red', icon='landmark', prefix='fa')
        elif icon == 'volcano':
            return folium.Icon(color='red', icon='volcano', prefix='fa')
        elif icon == 'waterfall':
            # _waterfall = folium.features.CustomIcon("icons/waterfall3.png", icon_size=(30, 40))
            return folium.Icon(color='red', icon="water", prefix='fa')
        elif icon == 'tree':
            return folium.Icon(color='red', icon='tree', prefix='fa')
        else:
            raise ValueError(f"Icon {icon} not recognized!")

    def _add_coordinates(self, keys: Union[list, str]) -> None:
        """ Adds coordinates to locations that do not have coordinates yet. """
        if isinstance(keys, str):
            keys = [keys]

        _added_coordinates = False
        for key in keys:
            assert key in self.mi.d.keys(), f"Key {key} not in MapItems!"
            for loc in self.mi[key]:
                if ("coordinates" not in self.mi[[key, loc]]) or (not self.mi[[key, loc, "coordinates"]]):
                    if "country" in self.mi["main"]:
                        self.mi[[key, loc]]["coordinates"] = self.locator(loc, self.mi[["main", "country"]])
                    else:
                        self.mi[[key, loc]]["coordinates"] = self.locator(loc)
                    _added_coordinates = True

        if _added_coordinates:
            # If any coordinates have been added; save the MapItems to JSON
            self.mi.to_json()

    def add_markers(self, locations: dict[str, dict], icon: str) -> None:
        for loc, info_dict in locations.items():
            assert "coordinates" in info_dict.keys(), f"{loc} is missing coordinates!"
            if icon == "landmarks":
                # popup = folium.Popup(" ".join([loc, info_dict['info']]), parse_html=True)

                _info = f"{info_dict['info']}<br>" if 'info' in info_dict else ''
                _website = f"""<a href="{info_dict['website']}" target="_blank">website</a><br>""" if 'website' in info_dict else ''
                _price = f"""Prijs: &euro; {info_dict['prijs']}<br> """ if 'prijs' in info_dict else ''
                _availability = "Beschikbaarheid: <ul>{availability}</ul>".format(availability=''.join([f"<li>{item}</li>" for item in info_dict['beschikbaarheid']])) if 'beschikbaarheid' in info_dict else ''
                html = """<b>{loc}</b><br>{website}{price}{info}{availability}
                """.format(
                    loc=loc,
                    website=_website,
                    price=_price,
                    info=_info,
                    availability=_availability
                )
                popup = folium.Popup(folium.IFrame(html, width=200, height=200))

            elif icon == "hotels":
                beschikbaarheid = ''.join([f"<li>{item}</li>" for item in info_dict['beschikbaarheid']])
                html = f"""<b>{loc}</b><br>
                    Prijs: &euro; {info_dict['prijs']}<br>
                    <a href="{info_dict['website']}" target="_blank">website</a><br>
                    Beschikbaarheid: <ul>{beschikbaarheid}</ul>
                    """
                popup = folium.Popup(folium.IFrame(html, width=200, height=200))
            else:
                raise ValueError

            folium.Marker(
                location=info_dict["coordinates"],
                popup=popup,
                icon=self.create_icon(info_dict['icon'] if 'icon' in info_dict.keys() else icon)
            ).add_to(self.base_map)

    def save_map(self, filename: str) -> None:
        self.base_map.save(filename)

    def main(self) -> None:
        self.create_map()

        items = ['landmarks', 'hotels']
        for item in items:
            self._add_coordinates([item])
            self.add_markers(self.mi[item], icon=item)


if __name__ == "__main__":
    json_file = sys.argv[1]

    # Initialize MapMaker object with JSON file
    mm = MapMaker(map_item_filename=json_file)

    # Create map
    mm.main()

    # Save map to HTML
    country = mm.mi.d['country'].capitalize()
    html_file = f"{country}Map.html"
    mm.save_map(html_file)
