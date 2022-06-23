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

from operator import imod
import cherrypy
import http.client

class ResultEndpoint:

    def __init__(self):
        self._result = None

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def index(self):
        print(cherrypy.request.json)


def test_streaming():
    endpoint = ResultEndpoint()

    cherrypy.tree.mount(endpoint, '/')

    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 9332
    cherrypy.engine.autoreload.on = False
    cherrypy.engine.start()
    cherrypy.engine.block()

def test_endpoint():
    connection = http.client.HTTPConnection('localhost', 9333, timeout=10)
    print(connection)
    while True:
        command = input('Press any key if you want to request a processing result. Otherwise press "q" to exit')
        if command == "q":
            break
        connection.request("GET", "/get_processing_result")
        response = connection.getresponse()
        print("Status: {} and reason: {}".format(response.status, response.reason))
        print(response.read())

    connection.close()

#test_streaming()
test_endpoint()
