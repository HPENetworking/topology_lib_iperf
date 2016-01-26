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

from .parser import parse_pid, parse_iperf_server, parse_iperf_client


class ServerState(object):
    """
    State object for the iperf server.

    :param int server_pid: Process id of the running iperf server.
    """
    def __init__(self, server_pid=None):
        self.server_pid = server_pid


class ClientState(object):
    """
    State object for the iperf client.

    :param int client_pid: Process id of the running iperf client.
    """
    def __init__(self, client_pid=None):
        self.client_pid = client_pid


def checkstate(stateclass, statename):
    def decorator(func):
        def replacement(enode, *args, **kwargs):

            state = getattr(enode, statename, None)
            if state is None:
                state = stateclass()
                setattr(enode, statename, state)

            return func(enode, state, *args, **kwargs)

        replacement.__name__ = func.__name__
        replacement.__doc__ = func.__doc__

        return replacement
    return decorator


@checkstate(ServerState, '_iperf_server_state')
def iperf_server_start(enode, state, port, interval=1, udp=False):
    """
    Start iperf server.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param int port: iperf port to be open
    :param int interval: interval for iperf server to check
    :param bool udp: If it is UDP or TCP. Default is False for TCP.
    """
    assert port

    cmd = [
        'iperf -s -p {port} -i {interval}'.format(**locals())
    ]

    if udp is True:
        cmd.append('-u')

    cmd.append('2>&1 > /tmp/iperf_server.log &')

    state.server_pid = parse_pid(enode(' '.join(cmd), shell='bash'))


@checkstate(ServerState, '_iperf_server_state')
def iperf_server_stop(enode, state):
    """
    Stop iperf server.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :return: A dictionary as returned by
     :func:`topology_lib_iperf.parser.parse_iperf_server`.
    """

    enode('kill {pid}'.format(pid=state.server_pid), shell='bash')
    state.server_pid = None

    return parse_iperf_server(
        enode('cat /tmp/iperf_server.log', shell='bash')
    )


@checkstate(ClientState, '_iperf_client_state')
def iperf_client_start(
        enode, state, server, port,
        interval=1, time=10, udp=None):
    """
    Use iperf client.

    All parameters left as ``None`` are ignored and thus no configuration
    action is taken for that parameter (left "as-is").
    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param server_ip: Server's IP address in the form ``'192.168.1.10'``
    :param int port: iperf port to be open
    :param int interval: interval for iperf server to check
    :param int time: the time iperf client will be running
    :param bool udp: If it is UDP or TCP. Default is False for TCP.
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

    cmd.append('2>&1 > /tmp/iperf_client.log &')

    state.client_pid = parse_pid(enode(' '.join(cmd), shell='bash'))


@checkstate(ClientState, '_iperf_client_state')
def iperf_client_stop(enode, state):
    """
    Stop iperf client.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :return: A dictionary as returned by
     :func:`topology_lib_iperf.parser.parse_iperf_client`.
    """

    pid_check = enode(
        'ps -a | grep {pid}'.format(pid=state.client_pid), shell='bash'
    )
    if 'Done' not in str(pid_check):
        enode('kill {pid}'.format(pid=state.client_pid), shell='bash')

    state.client_pid = None

    return parse_iperf_client(
        enode('cat /tmp/iperf_client.log', shell='bash')
    )


__all__ = [
    'iperf_server_start',
    'iperf_server_stop',
    'iperf_client_start',
    'iperf_client_stop'
]
