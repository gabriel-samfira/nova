# Copyright 2014 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Microversions Test Extension"""

from nova.api.openstack import extensions
from nova.api.openstack import wsgi


ALIAS = 'test-microversions'


class MicroversionsController(wsgi.Controller):

    @wsgi.Controller.api_version("2.1")
    def index(self, req):
        data = {'param': 'val'}
        return data

    @wsgi.Controller.api_version("2.2")  # noqa
    def index(self, req):
        data = {'param': 'val2'}
        return data


# We have a second example controller here to help check
# for accidental dependencies between API controllers
# due to base class changes
class MicroversionsController2(wsgi.Controller):

    @wsgi.Controller.api_version("2.2", "2.5")
    def index(self, req):
        data = {'param': 'controller2_val1'}
        return data

    @wsgi.Controller.api_version("2.5", "3.1")  # noqa
    @wsgi.response(202)
    def index(self, req):
        data = {'param': 'controller2_val2'}
        return data


class Microversions(extensions.V3APIExtensionBase):
    """Basic Microversions Extension."""

    name = "Microversions"
    alias = ALIAS
    version = 1

    def get_resources(self):
        res1 = extensions.ResourceExtension('microversions',
                                            MicroversionsController())
        res2 = extensions.ResourceExtension('microversions2',
                                            MicroversionsController2())
        return [res1, res2]

    def get_controller_extensions(self):
        return []
