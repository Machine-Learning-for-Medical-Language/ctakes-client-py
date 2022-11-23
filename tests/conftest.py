"""
Shared test configuration

This file gets automatically processed by pytest.

We use it here to skip integration tests if the cTAKE & cNLP servers aren't running.
Though you can pass --run-integration to force them to be attempted anyway.
"""

import pathlib
import socket

import pytest


def is_port_open(port: int) -> bool:
    try:
        socket.socket().connect(('localhost', port))
        return True
    except ConnectionRefusedError:
        return False


ctakes_port = 8080
cnlp_port = 8000
servers_are_running = is_port_open(ctakes_port) and is_port_open(cnlp_port)


def pytest_addoption(parser):
    parser.addoption('--run-integration', action='store_true', default=False, help='run integration tests')


def pytest_collection_modifyitems(config, items):
    if config.getoption('--run-integration') or servers_are_running:
        return

    print('Skipping integration tests')
    skip_integration = pytest.mark.skip(reason='needs cTAKES server to run')
    root = pathlib.Path(config.rootdir)
    for item in items:
        rel_path = pathlib.Path(item.fspath).relative_to(root)
        # Skip anything in the integration folder
        if str(rel_path).startswith('tests/integration/'):
            item.add_marker(skip_integration)
