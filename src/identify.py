#!/usr/bin/env python3
"""Sentry Mini - basic device identification scaffolding.
Identifies a device from its MAC OUI (vendor) and DHCP hostname (type/model).
"""
import sys

LEASES = "/var/lib/NetworkManager/dnsmasq-wlan0.leases"

OUI_VENDORS = {
    "b8:fb:b3": "TP-Link",
    "ac:84:c6": "TP-Link",
    "50:c7:bf": "TP-Link",
    "fc:a6:67": "Amazon",
    "44:65:0d": "Amazon",
    "f0:ef:86": "Google",
    "d8:6c:63": "Google",
    "b4:e6:2d": "Espressif (DIY/maker)",
    "dc:a6:32": "Raspberry Pi",
}

def vendor_from_mac(mac):
    prefix = mac.lower()[0:8]
    return OUI_VENDORS.get(prefix, "Unknown vendor")

def type_from_hostname(hostname):
    if not hostname or hostname == "*":
        return "unknown"
    h = hostname.lower()
    if h.startswith("l5") or h.startswith("l9") or "bulb" in h or "kl" in h:
        return "smart bulb"
    if "plug" in h or h.startswith("hs") or h.startswith("p1"):
        return "smart plug"
    if "cam" in h or h.startswith("c2") or "tapo_c" in h:
        return "camera"
    if "echo" in h or "alexa" in h:
        return "voice assistant"
    if "print" in h:
        return "printer"
    return "unknown type"

def identify(mac, hostname):
    return {
        "mac": mac,
        "hostname": hostname,
        "vendor": vendor_from_mac(mac),
        "type": type_from_hostname(hostname),
    }

def read_leases():
    devices = []
    try:
        with open(LEASES) as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 4:
                    devices.append((parts[1], parts[3]))
    except PermissionError:
        print("Permission denied reading leases. Run with: sudo python3 identify.py")
        sys.exit(1)
    except FileNotFoundError:
        print("No leases file found - is a device connected to SentryMini?")
        sys.exit(1)
    return devices

def main():
    if len(sys.argv) == 3:
        results = [identify(sys.argv[1], sys.argv[2])]
    else:
        results = [identify(mac, host) for mac, host in read_leases()]

    if not results:
        print("No devices found on the audit network.")
        return

    print("\n=== Sentry Mini - Device Identification ===\n")
    for r in results:
        print(f"  MAC address : {r['mac']}")
        print(f"  Hostname    : {r['hostname']}")
        print(f"  Vendor      : {r['vendor']}  (from MAC OUI)")
        print(f"  Device type : {r['type']}  (from hostname)")
        print("  " + "-" * 40)
    print()

if __name__ == "__main__":
    main()
EOF
