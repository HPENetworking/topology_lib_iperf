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
Test the iperf parsing module.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from topology_lib_iperf.parser import (parse_iperf_server, parse_iperf_client)

from deepdiff import DeepDiff


def test_server_stop():

    raw = """\
------------------------------------------------------------
Server listening on TCP port 5100
TCP window size: 85.3 KByte (default)
------------------------------------------------------------
[  4] local 127.0.0.1 port 5100 connected with 127.0.0.1 port 38040
[ ID] Interval       Transfer     Bandwidth
[  4]  0.0- 1.0 sec  1.84 GBytes  15.8 Gbits/sec
[  4]  1.0- 2.0 sec  1.82 GBytes  15.6 Gbits/sec
    """
    result = parse_iperf_server(raw)

    expected = {
        'server': '127.0.0.1',
        'server_port': '5100',
        'client': '127.0.0.1',
        'client_port': '38040',
        'traffic': {
            '0': {
                'transfer': '1.84 GBytes',
                'bandwidth': '15.8 Gbits/sec'
            },
            '1': {
                'transfer': '1.82 GBytes',
                'bandwidth': '15.6 Gbits/sec'
            }
        }
    }

    dic_diff = DeepDiff(result, expected)
    assert not dic_diff


def test_client_stop():

    raw = """\
------------------------------------------------------------
Client connecting to 127.0.0.1, TCP port 5100
TCP window size: 2.50 MByte (default)
------------------------------------------------------------
[  3] local 127.0.0.1 port 38040 connected with 127.0.0.1 port 5100
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0- 1.0 sec  1.84 GBytes  15.8 Gbits/sec
[  3]  1.0- 2.0 sec  1.82 GBytes  15.6 Gbits/sec
    """
    result = parse_iperf_client(raw)

    expected = {
        'client': '127.0.0.1',
        'client_port': '38040',
        'server': '127.0.0.1',
        'server_port': '5100',
        'traffic': {
            '0': {
                'transfer': '1.84 GBytes',
                'bandwidth': '15.8 Gbits/sec'
            },
            '1': {
                'transfer': '1.82 GBytes',
                'bandwidth': '15.6 Gbits/sec'
            }
        }
    }

    dic_diff = DeepDiff(result, expected)
    assert not dic_diff
