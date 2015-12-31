# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Parse iperf commands with output to a Python dictionary.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from re import search
from logging import getLogger


log = getLogger(__name__)


def parse_pid(response):
    """
    Parse PID shell output using a regular expression.

    :param str response: Output of a shell forking a subprocess.
    """
    assert response

    pid_regex = r'\[\d*\]\s+(?P<pid>\d+)'

    regex_result = search(pid_regex, response)
    if not regex_result:
        log.debug('Failed to parse pid from:\n{}'.format(response))
        raise Exception('PID regular expression didn\'t match.')

    return int(regex_result.groupdict()['pid'])


def parse_iperf_server(raw_output):
    """
    Parse the iperf server output command raw output.

    :param str raw_output: bash raw result string.
    :rtype: dict
    :return: All iperf server connection and traffic parsed \
        in the form:

     ::

        {
            'server':'127.0.0.1'
            'server_port':'5100'
            'client':'127.0.0.1'
            'client_port':'37545'
            'traffic': {
            '0': {
                'transfer':'2.72 GBytes',
                'bandwidth':'23.4 Gbits/sec'
            },
            '1':{
                'transfer':'2.87 GBytes',
                'bandwidth':'24.6 Gbits/sec'
                }
            }
        }
    """

    result = {}

    base_info_re = '\[\s*[0-9]+\] local (?P<server>.*) port ' \
        '(?P<server_port>\d+) connected with (?P<client>.*) port ' \
        '(?P<client_port>.*)'

    base_result = search(base_info_re, raw_output)
    if base_result:
        base_result = base_result.groupdict()

    result.update(base_result)

    traffic_re = (
        r'sec  (?P<transfer>[.\d]+ .*?)  (?P<bandwidth>[.\d]+ .+)'
    )

    cont = 0

    result['traffic'] = {}
    for raw_line in raw_output.splitlines():
        traffic_reg_result = search(traffic_re, raw_line)
        if traffic_reg_result:
            traffic_reg_result = traffic_reg_result.groupdict()
            result['traffic'][str(cont)] = traffic_reg_result
            cont += 1

    return result


def parse_iperf_client(raw_output):
    """
    Parse the iperf client output command raw output.

    :param str raw_output: bash raw result string.
    :rtype: dict
    :return: All iperf server connection and traffic parsed \
        in the form:

     ::

        {
            'server':'127.0.0.1'
            'server_port':'5100'
            'client':'127.0.0.1'
            'client_port':'37545'
            'traffic': {
                '0': {
                    'transfer':'2.72 GBytes',
                    'bandwidth':'23.4 Gbits/sec'
                },
                '1':{
                    'transfer':'2.87 GBytes',
                    'bandwidth':'24.6 Gbits/sec'
                }
            }
        }
    """

    result = {}

    base_info_re = '\[\s*[0-9]+\] local (?P<client>.*) port ' \
        '(?P<client_port>\d+) connected with (?P<server>.*) port ' \
        '(?P<server_port>.*)'

    base_result = search(base_info_re, raw_output)
    if base_result:
        base_result = base_result.groupdict()

    result.update(base_result)

    traffic_re = (
        r'sec  (?P<transfer>[.\d]+ .*?)  (?P<bandwidth>[.\d]+ .+)'
    )

    cont = 0

    result['traffic'] = {}
    for raw_line in raw_output.splitlines():
        traffic_result = search(traffic_re, raw_line)
        if traffic_result:
            traffic_result = traffic_result.groupdict()
            result['traffic'][str(cont)] = traffic_result
            cont += 1

    return result


__all__ = [
    'parse_iperf_server',
    'parse_iperf_client'
]
