"""
Device definitions for Chrome DevTools custom devices.
Each device includes specifications for width, height, DPR, and device type.
"""

# Device specifications from user requirements
DEVICES = [
    {
        "name": "Apple MacBook 12-inch",
        "width": 2304,
        "height": 1310,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "Apple MacBook Pro 13-inch",
        "width": 2560,
        "height": 1470,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "Apple MacBook Pro 15-inch",
        "width": 2880,
        "height": 1670,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "iMac 24 - 2021",
        "width": 2048,
        "height": 1152,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook PRO 16 - 2021",
        "width": 1728,
        "height": 1117,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Air 13 - 2020",
        "width": 1280,
        "height": 800,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 16 - 2019",
        "width": 1536,
        "height": 960,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 13 - 2018",
        "width": 1280,
        "height": 800,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Air 13 - 2018",
        "width": 1280,
        "height": 800,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 15 - 2018",
        "width": 1440,
        "height": 900,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 13 Pro - 2017",
        "width": 1440,
        "height": 900,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 15 Pro - 2017",
        "width": 1280,
        "height": 800,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 13 Pro - 2016",
        "width": 1280,
        "height": 800,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 15 Pro - 2016",
        "width": 1440,
        "height": 900,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 13 Pro - 2015",
        "width": 1280,
        "height": 800,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 15 Pro - 2015",
        "width": 1440,
        "height": 900,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "MacBook Pro 15 Pro - 2014",
        "width": 1440,
        "height": 900,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "Notebook with touch",
        "width": 1280,
        "height": 950,
        "dpr": 1,
        "type": "desktop",
        "touch": True
    },
    {
        "name": "Notebook with HiDPI screen",
        "width": 1440,
        "height": 900,
        "dpr": 2,
        "type": "desktop"
    },
    {
        "name": "Dell Latitude 3420 14",
        "width": 1440,
        "height": 809,
        "dpr": 1,
        "type": "desktop"
    },
    {
        "name": "Microsoft Surface Duo",
        "width": 1114,
        "height": 705,
        "dpr": 2.5,
        "type": "mobile",
        "touch": True
    },
    {
        "name": "Generic notebook",
        "width": 1280,
        "height": 800,
        "dpr": 1,
        "type": "desktop"
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
