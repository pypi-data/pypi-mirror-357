# This file makes the upnp_forwarder directory a Python package.

from .core import add_port_mapping, delete_port_mapping, get_local_ip, UPnPError
