# This file is part of Octopus Sensing Processing <https://octopus-sensing.nastaran-saffar.me/>
# Copyright © 2022 Nastaran Saffaryazdi <nsaffar@gmail.com>
#
# Octopus Sensing Processing is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# Octopus Sensing Processing is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Octopus Sensing
# Processing. If not, see <https://www.gnu.org/licenses/>.

import io
import random
import json
import pickle
import base64
import urllib.request
import logging
import time
# The data received from the server might be in numpy format.
# We need to import 'numpy' to unpickle it.
import numpy
import PIL.Image
from typing import Optional, List


def encode_image_to_base64(image_array):
    image_buffer = io.BytesIO()
    PIL.Image.fromarray(image_array) \
        .save(image_buffer, format="png")
    return str(base64.b64encode(image_buffer.getvalue()), "ascii")


class OctopusSensingClient:
    def __init__(self, host: str= "127.0.0.1", port: int=9330):
        self._host = host
        self._port = port

    def fetch(self, duration: int=3, device_list: Optional[List[str]]=None):
        if device_list is None:
            url = "http://{0}:{1}/?duration={2}".format(self._host, self._port, duration)
        else:
            device_list_str = ""
            for item in device_list:
                device_list_str += (item + ",")
            device_list_str = device_list_str[:-1]
            url = "http://{0}:{1}/?duration={2}&device_list={3}".format(self._host,
                                                                        self._port,
                                                                        duration,
                                                                        device_list_str)
        try:
            serialized_data = self.__request_data(url, retries=60)
        except Exception as error:
            raise error
        
        raw_data = pickle.loads(serialized_data)
        data = {}

        if "eeg" in raw_data:
            data["eeg"] = self._restructure_eeg(raw_data["eeg"])

        if "shimmer" in raw_data:
            gsr_records, ppg_records, = self._restructure_shimmer(
                raw_data["shimmer"])
            data["gsr"] = gsr_records
            data["ppg"] = ppg_records

        if "camera" in raw_data:
            # The type of data is a list of numpy-array. Each item is a frame
            data["camera"] = raw_data["camera"]

        return data

    def __request_data(self, url, retries=60):
            try:
                request = urllib.request.Request(url,
                                                headers={"Accept": "application/pickle"},
                                                method='GET')
                with urllib.request.urlopen(request) as response:
                    if response.getcode() != 200:
                        raise RuntimeError("Getting data failed. Got HTTP status: {0} {1}".format(response.status,
                                                                                                  response.reason))
                        
                    serialized_data = response.read()
                    return serialized_data
            except Exception as err:
                if retries == 0:
                    logging.error(f"Failed to get the data: {err}")
                    raise
                else:
                    logging.error(f"Getting data failed. Re-trying [{retries}]. Error: {err}")
                    time.sleep(1)
                    return self.__request_data(request, retries=retries - 1)


    def _restructure_eeg(self, data):
        channels = 8
        if len(data[0]) >= 16:
            channels = 16

        result = []

        for _ in range(channels):
            result.append([])

        for record in data:
            for i, channel_data in enumerate(record[1:channels+1]):
                result[i].append(channel_data)

        return result

    def _restructure_shimmer(self, data):
        gsr_records = []
        ppg_records = []

        for record in data:
            gsr_records.append(record[5])
            ppg_records.append(record[6])

        return (gsr_records, ppg_records)


    
class MockClient:

    def fetch(self):
        # Three seconds of random data
        eeg_data = []
        for _ in range(16):
            eeg_data.append(self._three_seconds_random_data())

        random_frame_data = numpy.random.randint(
            low=1, high=255, size=(640, 480, 3), dtype=numpy.uint8)
        random_frame = encode_image_to_base64(random_frame_data)

        return json.dumps({"eeg": eeg_data,
                           "gsr": self._three_seconds_random_data(),
                           "ppg": self._three_seconds_random_data(),
                           "camera": random_frame})

    def _three_seconds_random_data(self):
        return [round(random.uniform(0.01, 0.9), 5) for _ in range(3 * 128)]
