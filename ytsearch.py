# Copyright 2018 goppacode (Michael Rosenthal)
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from collections import namedtuple
import youtube_dl

SearchResult = namedtuple('SearchResult', [
    "location",
    "name",
    "artist",
    "album",
])

class Searcher:
    @staticmethod
    def search(query, autogenerated=True):
        ydl_url = Searcher.construct_ydl_url(query, autogenerated)
        with youtube_dl.YoutubeDL() as ydl:
            ydl_result = ydl.extract_info(ydl_url, download=False)
            return Searcher.extract_result(ydl_result)

    @staticmethod
    def construct_ydl_url(query, autogenerated):
        if(autogenerated):
            query = '{} "Auto-generated by YouTube"'.format(query)
        return 'ytsearch1:{}'.format(query)

    @staticmethod
    def extract_result(ydl_result):
        # get the first search result if there is one
        entry = next(iter(ydl_result["entries"]), None)
        if entry is None:
            return None
        
        url = entry["webpage_url"]
        title = entry["title"]
        description = entry["description"].split("\n\n")
        
        name = title
        artist = None
        album = None

        # if we know how to read the description extract the info from it
        if Searcher.is_description_autogenerated(description, title):
            name, artist = description[1].split(" \u00B7 ", 1)
            album = description[2]

        return SearchResult(location=url, name=name, artist=artist, album=album)

    @staticmethod
    def is_description_autogenerated(description, title):
        """
        Auto-generated YouTube uploads have a very particular structure that is checked here.
        """
        return (len(description) > 3 and
                description[0].startswith("Provided to YouTube by ") and
                description[1].startswith(title + " \u00B7 ") and
                description[-1].strip() == "Auto-generated by YouTube."
        )