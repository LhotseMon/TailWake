"""Tailscale status integration."""
import subprocess
import json
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TailscaleInfo:
    """Tailscale connection information."""
    online: bool = False
    ip: str = ""
    hostname: str = ""
    last_handshake: str = ""


def get_tailscale_ip() -> Optional[str]:
    """Get Tailscale IPv4 address.

    Returns:
        IPv4 address string, or None if unavailable.
    """
    try:
        result = subprocess.run(
            ["tailscale", "ip", "-4"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            ip = result.stdout.strip()
            if ip:
                return ip
        return None
    except FileNotFoundError:
        logger.warning("tailscale CLI not found")
        return None
    except subprocess.TimeoutExpired:
        logger.error("tailscale ip command timed out")
        return None
    except Exception as e:
        logger.error(f"Failed to get Tailscale IP: {e}")
        return None


def get_tailscale_status() -> TailscaleInfo:
    """Get full Tailscale status.

    Returns:
        TailscaleInfo object with connection details.
    """
    info = TailscaleInfo()

    try:
        result = subprocess.run(
            ["tailscale", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            logger.warning("tailscale status command failed")
            return info

        data = json.loads(result.stdout)

        # Check if connected
        backend_state = data.get("BackendState", "")
        info.online = backend_state == "Running"

        if info.online:
            # Get self node info
            self_node = data.get("Self", {})
            info.hostname = self_node.get("HostName", "")

            # Get Tailscale IPs
            for addr in self_node.get("TailscaleIPs", []):
                if ":" not in addr:  # IPv4
                    info.ip = addr
                    break

            # Get last handshake (from peer info)
            peer = data.get("Peer", {})
            if peer:
                first_peer = next(iter(peer.values()), {})
                info.last_handshake = first_peer.get("LastHandshake", "")

    except FileNotFoundError:
        logger.warning("tailscale CLI not found")
    except json.JSONDecodeError:
        logger.error("Failed to parse tailscale status JSON")
    except subprocess.TimeoutExpired:
        logger.error("tailscale status command timed out")
    except Exception as e:
        logger.error(f"Failed to get Tailscale status: {e}")

    return info


def is_tailscale_installed() -> bool:
    """Check if Tailscale CLI is available."""
    try:
        result = subprocess.run(
            ["tailscale", "version"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False