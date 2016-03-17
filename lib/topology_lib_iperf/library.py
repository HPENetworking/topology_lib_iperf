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
topology_lib_iperf communication library implementation.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from topology.libraries.utils import stateprovider

from .parser import parse_pid, parse_iperf_server, parse_iperf_client


class IperfServerState(object):
    """
    State object for the iperf server.
    """

    def __init__(self):
        self.server_pids = {}


class IperfClientState(object):
    """
    State object for the iperf client.
    """

    def __init__(self):
        self.client_pids = {}


@stateprovider(IperfServerState)
def server_start(
                 enode, state, port, interval=1,
                 udp=False, instance_id=1, shell=None
                 ):
    """
    Start iperf server.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param int port: iperf port to be open.
    :param int interval: interval for iperf server to check.
    :param bool udp: If it is UDP or TCP. Default is False for TCP.
    :param int instance_id: Number of iperf server instance.
     Default is 1.
    :param str shell: Shell name to execute commands.
     If ``None``, use the Engine Node default shell.
    """
    assert port

    cmd = [
        'iperf -s -p {port} -i {interval}'.format(**locals())
    ]

    if udp is True:
        cmd.append('-u')

    cmd.append('2>&1 > /tmp/iperf_server-{}.log &'.format(instance_id))

    state.server_pids[instance_id] = parse_pid(
        enode(' '.join(cmd), shell=shell)
    )


@stateprovider(IperfServerState)
def server_stop(enode, state, instance_id=1, shell=None):
    """
    Stop iperf server.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param int instance_id: Number of iperf server instance.
     Default is 1.
    :param str shell: Shell name to execute commands.
     If ``None``, use the Engine Node default shell.
    :return: A dictionary as returned by
     :func:`topology_lib_iperf.parser.parse_iperf_server`.
    """

    enode('kill {pid}'.format(
        pid=state.server_pids[instance_id]
    ), shell=shell)
    del state.server_pids[instance_id]

    return parse_iperf_server(
        enode(
            'cat /tmp/iperf_server-{}.log'.format(instance_id),
            shell=shell
        )
    )


@stateprovider(IperfClientState)
def client_start(
        enode, state, server, port,
        interval=1, time=10, udp=None,
        bandwidth=None, instance_id=1,
        shell=None):
    """
    Use iperf client.

    All parameters left as ``None`` are ignored and thus no configuration
    action is taken for that parameter (left "as-is").
    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param server_ip: Server's IP address in the form ``'192.168.1.10'``.
    :param int port: iperf port to be open.
    :param int interval: interval for iperf server to check.
    :param int time: the time iperf client will be running.
    :param bool udp: If it is UDP or TCP. Default is False for TCP.
    :param str bandwidth: Bandwidth for iperf to use in bits/sec.
     When used automatically switches to UDP regardless of udp setting.
     Default is 1Mb/sec.
    :param int instance_id: Number of iperf client instance.
     Default is 1.
    :param str shell: Shell name to execute commands.
     If ``None``, use the Engine Node default shell.
    """

    assert server
    assert port

    cmd = [
        'iperf -c {server} -p {port} -i {interval} -t {time}'.format(
            **locals()
        )
    ]

    if udp is True:
        cmd.append('-u')
    
    if bandwidth is not None:
        cmd.append('-b {}'.format(bandwidth))

    cmd.append('2>&1 > /tmp/iperf_client-{}.log &'.format(instance_id))

    state.client_pids[instance_id] = parse_pid(
        enode(' '.join(cmd), shell=shell)
    )


@stateprovider(IperfClientState)
def client_stop(enode, state, instance_id=1, shell=None):
    """
    Stop iperf client.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param int instance_id: Number of iperf client instance.
     Default is 1.
    :param str shell: Shell name to execute commands.
     If ``None``, use the Engine Node default shell.
    :return: A dictionary as returned by
     :func:`topology_lib_iperf.parser.parse_iperf_client`.
    """

    pid_check = enode(
        'ps -a | grep {pid}'.format(pid=state.client_pids[instance_id]),
        shell=shell
    )
    if 'Done' not in str(pid_check):
        enode('kill {pid}'.format(pid=state.client_pids[instance_id]),
              shell=shell)

    del state.client_pids[instance_id]

    return parse_iperf_client(
        enode(
            'cat /tmp/iperf_client-{}.log'.format(instance_id),
            shell=shell
        )
    )


__all__ = [
    'server_start',
    'server_stop',
    'client_start',
    'client_stop'
]
