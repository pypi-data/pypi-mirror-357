"""
Device definitions for Chrome DevTools custom devices.
Each device includes specifications for width, height, DPR, and device type.
"""

# Device specifications with proper viewport dimensions (not screen resolution)
# Based on actual browser viewport sizes accounting for browser UI
DEVICES = [
    {
        "name": "MacBook Air 13\" (2020)",
        "width": 1280,
        "height": 715,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Air 15\" (2023)",
        "width": 1440,
        "height": 820,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 14\" (2021)",
        "width": 1512,
        "height": 865,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 16\" (2021)",
        "width": 1728,
        "height": 1000,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 16\" (2019)",
        "width": 1536,
        "height": 960,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 15\" (2018)",
        "width": 1440,
        "height": 900,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 13\" (2020)",
        "width": 1280,
        "height": 800,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "iMac 24\" (2021)",
        "width": 2240,
        "height": 1156,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "iMac 27\" (2020)",
        "width": 2560,
        "height": 1336,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "Studio Display",
        "width": 2560,
        "height": 1336,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "Studio Display (Half)",
        "width": 1278,
        "height": 1336,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "Pro Display XDR",
        "width": 3008,
        "height": 1588,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook 12\" (2017)",
        "width": 1152,
        "height": 720,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 15\" (2016)",
        "width": 1440,
        "height": 900,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 13\" (2016)",
        "width": 1280,
        "height": 800,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Air 13\" (2018)",
        "width": 1280,
        "height": 800,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "Generic Laptop (1080p)",
        "width": 1366,
        "height": 768,
        "dpr": 1,
        "type": "desktop"
    },
    {
        "name": "Generic Laptop (1440p)",
        "width": 1600,
        "height": 900,
        "dpr": 1,
        "type": "desktop"
    },
    {
        "name": "Touchscreen Laptop",
        "width": 1280,
        "height": 720,
        "dpr": 1.5,
        "type": "desktop",
        "touch": True
    },
    {
        "name": "HiDPI Laptop",
        "width": 1440,
        "height": 900,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "Dell XPS 13",
        "width": 1920,
        "height": 1080,
        "dpr": 1.5,
        "type": "desktop"
    },
    {
        "name": "Surface Laptop",
        "width": 1504,
        "height": 1000,
        "dpr": 1.5,
        "type": "desktop",
        "touch": True
    }
]

# User agent strings for different device types
USER_AGENTS = {
    "desktop": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
    "mobile": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "tablet": "Mozilla/5.0 (iPad; CPU OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
}

def get_device_capabilities(device):
    """
    Determine device capabilities based on device type and properties.
    
    Args:
        device (dict): Device specification
        
    Returns:
        list: List of capabilities (e.g., ["mobile", "touch"])
    """
    capabilities = []
    
    if device["type"] == "mobile":
        capabilities.append("mobile")
        capabilities.append("touch")
    elif device["type"] == "tablet":
        capabilities.append("touch")
    elif device.get("touch", False):
        capabilities.append("touch")
    
    return capabilities

def get_user_agent(device):
    """
    Get appropriate user agent string for device type.
    
    Args:
        device (dict): Device specification
        
    Returns:
        str: User agent string
    """
    device_type = device["type"]
    return USER_AGENTS.get(device_type, USER_AGENTS["desktop"])

def is_mobile_device(device):
    """
    Check if device should be treated as mobile.
    
    Args:
        device (dict): Device specification
        
    Returns:
        bool: True if mobile device
    """
    return device["type"] in ["mobile", "tablet"]
