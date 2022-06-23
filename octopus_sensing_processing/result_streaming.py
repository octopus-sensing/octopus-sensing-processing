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

import json
import urllib.request
import logging
import time

# The data received from the processor might is in numpy format.
# We need to import 'numpy' to unpickle it.

class ResultStreaming:

    def __init__(self, url: str= "http://127.0.0.1:9332/"):

        self._url = url

    def push_processing_result(self, result):
        result_json = json.dumps(result).encode('utf-8')

        self.__post_data(self._url, result_json, retries=60)
        
    def __post_data(self, result_json, retries=3):
            try:
                request = urllib.request.Request(self._url,
                                                headers={"Content-Type": "application/json"},
                                                method='POST',
                                                data=result_json)
                with urllib.request.urlopen(request) as response:
                    if response.getcode() != 200:
                        raise RuntimeError("Posting data failed. Got HTTP status: {0} {1}".format(response.status,
                                                                                                  response.reason))

                    serialized_data = response.read()
                    return serialized_data
            except Exception as err:
                if retries == 0:
                    logging.error(f"Failed to post the data: {err}")
                    raise
                else:
                    logging.error(f"Posting data failed. Re-trying [{retries}]. Error: {err}")
                    time.sleep(1)
                    self.__post_data(self._url, result_json, retries=retries - 1)
