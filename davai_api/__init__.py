#!/usr/bin/env python3
# -*- coding:Utf-8 -*-
"""
Python utilities for the Davai API.
"""
from __future__ import print_function, absolute_import, unicode_literals, division

import os
import re
import configparser
import socket

davai_home = os.path.join(os.environ['HOME'], '.davairc')
this_repo = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
davai_api_name = os.path.basename(this_repo)

# config
general_config_file = os.path.join(this_repo, 'conf', 'general.ini')
general_config = configparser.ConfigParser()
general_config.read(general_config_file)
user_config_file = os.path.join(davai_home, 'user_config.ini')
user_config = configparser.ConfigParser()
if os.path.exists(user_config_file):
    user_config.read(user_config_file)

# defaults
def set_defaults():
    """Set defaults, actual defaults or from user config if present"""
    defaults = {}
    # local repository
    local_repo = os.path.join(davai_home, davai_api_name)
    if 'davai' in user_config.sections():
        local_repo = user_config['davai'].get('local_repo', local_repo)
    defaults['local_repo'] = os.path.abspath(os.path.expanduser(local_repo))
    # XP directory
    XP_directory = os.path.join(davai_home, 'experiments')
    if 'davai' in user_config.sections():
        XP_directory = user_config['davai'].get('XP_directory', XP_directory)
    defaults['XP_directory'] = os.path.abspath(os.path.expanduser(XP_directory))
    # logs directory
    _workdir = os.environ.get('WORKDIR', None)
    if _workdir:
        logs_directory = os.path.join(_workdir, 'davai', 'logs')
    else:
        logs_directory = os.path.join(davai_home, 'logs')
    if 'davai' in user_config.sections():
        logs_directory = user_config['davai'].get('logs_directory', logs_directory)
    defaults['logs_directory'] = os.path.abspath(os.path.expanduser(logs_directory))
    # usecase
    usecase = 'NRV'
    if 'davai' in user_config.sections():
        usecase = user_config['davai'].get('usecase', usecase)
    defaults['usecase'] = usecase
    return defaults

def possible_defaults_in_user_config():
    """Possible parameters which defaults that can be set in section [davai] of ~/.davairc/user_config.py"""
    print(list(defaults.keys()))

defaults = set_defaults()


def guess_host():
    """
    Guess host from (by order of resolution):
      - $DAVAI_HOST
      - resolution from socket.gethostname() through:
        * $HOME/.davairc/user_config.ini
        * {davai_api install}/conf/general.ini
    """
    socket_hostname = socket.gethostname()
    host = os.environ.get('DAVAI_HOST', None)
    if not host:
        for config in (user_config, general_config):
            if 'hosts' in config.sections():
                for h, pattern in config['hosts'].items():
                    if re.match(pattern, socket_hostname):
                        host = h[:-len('_re_pattern')]  # h is '{host}_re_pattern'
                        break
                if host:
                    break
    if not host:
        raise ValueError("Couldn't find host in $DAVAI_HOST, " +
                         "nor guess from hostname ({}) and keys '{host}_re_pattern' " +
                         "in section 'hosts' of config files: ('{}', '{}')".format(
            socket_hostname, user_config_file, general_config_file))
    return host
