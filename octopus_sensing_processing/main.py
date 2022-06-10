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

import time
import argparse

from octopus_sensing_processing.octopus_sensing_client import OctopusSensingClient

# def get_args():
#     arg_parser = argparse.ArgumentParser()
#     arg_parser.add_argument("-f", "--fake",
#                             help="start a fake server that generates random data",
#                             action="store_true")
#     return arg_parser.parse_args()


def main():
    # args = get_args()

    client = OctopusSensingClient()

    while True:
        data = client.fetch(duration=2, device_list=["camera", "audio"])
        time.sleep(1)
        
if __name__ == '__main__':
    main()
