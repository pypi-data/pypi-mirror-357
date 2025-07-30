import miniupnpc
import socket
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UPnPError(Exception):
    """Custom exception for UPnP related errors."""
    pass

def get_local_ip():
    """Get the local IP address of the machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a public server (doesn't actually send data)
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
        logger.info(f"Successfully retrieved local IP address: {local_ip}")
        return local_ip
    except Exception as e:
        logger.error(f"Failed to get local IP address: {e}")
        raise UPnPError(f"Failed to get local IP address: {e}")
    finally:
        s.close()

def discover_igd():
    """Discovers the Internet Gateway Device (router) on the network."""
    try:
        logger.info("Discovering UPnP devices...")
        upnp = miniupnpc.UPnP()
        # As per miniupnpc Python examples, discover() takes no arguments
        ndevices = upnp.discover()

        if ndevices > 0:
            logger.info(f"Found {ndevices} UPnP devices.")
            try:
                upnp.selectigd()
                logger.info("Selected IGD.")
                return upnp
            except Exception as e:
                logger.error(f"Failed to select IGD: {e}")
                raise UPnPError(f"Failed to select IGD: {e}")
        else:
            logger.warning("No UPnP devices found.")
            return None
    except Exception as e:
        logger.error(f"An error occurred during UPnP discovery: {e}")
        raise UPnPError(f"An error occurred during UPnP discovery: {e}")

def add_port_mapping(local_port, external_port, protocol, description, lease_duration=3600):
    """Adds a UPnP port mapping."""
    upnp = discover_igd()
    if not upnp:
        raise UPnPError("Could not discover IGD to add port mapping.")

    try:
        external_ip = upnp.externalipaddress()
        logger.info(f"External IP address: {external_ip}")

        local_ip = get_local_ip()
        logger.info(f"Local IP address: {local_ip}")

        logger.info(f"Attempting to add port mapping: {local_ip}:{local_port} -> {external_ip}:{external_port} ({protocol}) with lease duration {lease_duration}s")
        success = upnp.addportmapping(
            external_port,
            protocol,
            local_ip,
            local_port,
            description,
            '', # remote host, empty string means any host
            lease_duration # lease duration in seconds
        )

        if success:
            logger.info("Port mapping added successfully.")
            return True
        else:
            logger.warning("Failed to add port mapping.")
            return False

    except Exception as e:
        logger.error(f"An error occurred while adding port mapping: {e}")
        raise UPnPError(f"An error occurred while adding port mapping: {e}")

def delete_port_mapping(external_port, protocol):
    """Deletes a UPnP port mapping."""
    upnp = discover_igd()
    if not upnp:
        raise UPnPError("Could not discover IGD to delete port mapping.")

    try:
        logger.info(f"Attempting to delete port mapping: {external_port} ({protocol})")
        success = upnp.deleteportmapping(external_port, protocol)

        if success:
            logger.info("Port mapping deleted successfully.")
            return True
        else:
            logger.warning("Failed to delete port mapping.")
            return False

    except Exception as e:
        logger.error(f"An error occurred while deleting port mapping: {e}")
        raise UPnPError(f"An error occurred while deleting port mapping: {e}")

# Removed the __main__ block as this is now a package module.
