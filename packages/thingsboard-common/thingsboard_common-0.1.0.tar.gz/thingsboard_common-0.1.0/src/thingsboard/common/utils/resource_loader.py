# -*- coding: utf-8 -*-

import os
import urllib.parse as urlparse  # pip install urllib3
import urllib3

from configobj import ConfigObj  # pip install configobj
from .path_helpers import prettify


class ResourceLoader(object):

    @classmethod
    def load_from_locations(cls, filename: str, locations: str or list[str]) -> ConfigObj:
        """Searches for a resource file in the given locations and loads them.
        """

        if isinstance(locations, str):
            locations = [locations, ]

        for location in locations:
            url = urlparse.urlparse(location)

            if url.scheme == 'home':
                base_path = os.path.expanduser('~') + url.path
                file_path = os.path.join(base_path, filename)
                file_path = prettify(file_path)

                if os.path.isfile(file_path):
                    properties = ConfigObj(file_path)
                    return properties
            elif url.scheme in ('file', 'path'):
                file_path = os.path.join(url.path, filename)
                if os.path.isfile(file_path):
                    properties = ConfigObj(file_path)
                    return properties
            elif url.scheme == 'http' or \
                    url.scheme == 'https':
                if not location.endswith('/'):
                    location += '/'
                file_path = location + filename
                try:
                    http = urllib3.PoolManager()
                    r = http.request('GET', file_path)
                    file_content = r.data
                    properties = ConfigObj(file_content)
                    return properties
                except NameError:
                    pass
        return ConfigObj()

    @classmethod
    def find_first_occurrence(cls, filename: str, locations: str or list[str]) -> tuple[str or None, int]:
        """ Searches for a file in given locations.

        Returns the first location where the file was found by returning the path and the location
        index where the file was found.
        """

        if isinstance(locations, str):
            locations = [locations, ]

        for index, location in enumerate(locations):
            url = urlparse.urlparse(location)

            if url.scheme == 'home':
                base_path = os.path.expanduser('~') + url.path
                file_path = os.path.join(base_path, filename)
                file_path = prettify(file_path)

                if os.path.isfile(file_path):
                    return prettify(base_path), index
            elif url.scheme in ('file', 'path'):
                file_path = os.path.join(url.path, filename)
                if os.path.isfile(file_path):
                    return prettify(url.path), index
        return None, -1
