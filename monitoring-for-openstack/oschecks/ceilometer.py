#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Openstack Monitoring script for Sensu / Nagios
#
# Copyright © 2013-2014 eNovance <licensing@enovance.com>
#
# Author: Mehdi Abaakouk <mehdi.abaakouk@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import re

from oschecks import utils
from ceilometerclient.openstack.common.apiclient import exceptions


def _check_ceilometer_api():
    ceilometer = utils.Ceilometer()
    ceilometer.add_argument('-w', dest='warning', type=int, default=5,
                            help='Warning timeout for Ceilometer APIs calls')
    ceilometer.add_argument('-c', dest='critical', type=int, default=10,
                            help='Critical timeout for Ceilometer APIs calls')
    options, client = ceilometer.setup()

    def meters_list():
        try:
            return client.meters.list()
        except exceptions.Gone as ex:
            msg = json.loads(ex.response.content)
            utils.warning(re.sub(r'\s\s*', ' ', msg['error_message']))
        except Exception as ex:
            utils.critical(str(ex))

    elapsed, meters = utils.timeit(meters_list)
    if not meters:
        utils.critical("Unable to contact Ceilometer API.")

    if elapsed > options.critical:
        utils.critical("Get meters took more than %d seconds, "
                       "it's too long.|response_time=%d" %
                       (options.critical, elapsed))
    elif elapsed > options.warning:
        utils.warning("Get meters took more than %d seconds, "
                      "it's too long.|response_time=%d" %
                      (options.warning, elapsed))
    else:
        utils.ok("Get meters, Ceilometer API is working: "
                 "list %d meters in %d seconds.|response_time=%d" %
                 (len(meters), elapsed, elapsed))


def check_ceilometer_api():
    utils.safe_run(_check_ceilometer_api)
