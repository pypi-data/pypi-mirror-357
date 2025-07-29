#!/bin/bash
# Chrome Custom Devices - One-Command Installer
# Usage: curl -sSL https://raw.githubusercontent.com/user/repo/main/quick-install.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Symbols
SUCCESS="✅"
ERROR="❌" 
WARNING="⚠️"
INFO="ℹ️"
SEARCH="🔍"
PACKAGE="📦"
ROCKET="🚀"
RESTART="🔄"
CELEBRATION="🎉"

echo -e "${ROCKET} Chrome Custom Devices - One-Command Installer"
echo "========================================================="
echo ""

# Function to print colored output
print_status() {
    local color=$1
    local symbol=$2
    local message=$3
    echo -e "${color}${symbol} ${message}${NC}"
}

# Function to print progress
print_progress() {
    print_status "$BLUE" "$INFO" "$1"
}

print_success() {
    print_status "$GREEN" "$SUCCESS" "$1"
}

print_error() {
    print_status "$RED" "$ERROR" "$1"
}

print_warning() {
    print_status "$YELLOW" "$WARNING" "$1"
}

# Detect operating system
detect_os() {
    case "$(uname -s)" in
        Darwin*)
            echo "darwin"
            ;;
        Linux*)
            echo "linux"
            ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*)
            echo "windows"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Get Chrome paths based on OS
get_chrome_paths() {
    local os=$1
    case $os in
        "darwin")
            echo "$HOME/Library/Application Support/Google/Chrome"
            echo "$HOME/Library/Application Support/Google/Chrome Beta"
            echo "$HOME/Library/Application Support/Google/Chrome Dev"
            echo "$HOME/Library/Application Support/Google/Chrome Canary"
            echo "$HOME/Library/Application Support/Arc/User Data"
            ;;
        "linux")
            echo "$HOME/.config/google-chrome"
            echo "$HOME/.config/google-chrome-beta"
            echo "$HOME/.config/google-chrome-unstable"
            echo "$HOME/.config/chromium"
            ;;
        "windows")
            echo "$LOCALAPPDATA/Google/Chrome/User Data"
            echo "$LOCALAPPDATA/Google/Chrome Beta/User Data"
            echo "$LOCALAPPDATA/Google/Chrome Dev/User Data"
            echo "$LOCALAPPDATA/Google/Chrome SxS/User Data"
            ;;
    esac
}

# Check if Chrome is running
is_chrome_running() {
    local os=$1
    case $os in
        "darwin")
            pgrep -f "Google Chrome" >/dev/null 2>&1
            ;;
        "linux")
            pgrep -f "chrome|chromium" >/dev/null 2>&1
            ;;
        "windows")
            tasklist //FI "IMAGENAME eq chrome.exe" 2>/dev/null | grep -q "chrome.exe"
            ;;
        *)
            return 1
            ;;
    esac
}

# Find all Chrome profiles
find_chrome_profiles() {
    local os=$1
    local profiles=()
    
    while IFS= read -r chrome_path; do
        if [[ -d "$chrome_path" ]]; then
            # Check Default profile
            if [[ -f "$chrome_path/Default/Preferences" ]]; then
                profiles+=("$chrome_path/Default/Preferences|Default")
            fi
            
            # Check numbered profiles
            for profile_dir in "$chrome_path"/Profile\ *; do
                if [[ -d "$profile_dir" && -f "$profile_dir/Preferences" ]]; then
                    local profile_name=$(basename "$profile_dir")
                    profiles+=("$profile_dir/Preferences|$profile_name")
                fi
            done
        fi
    done < <(get_chrome_paths "$os")
    
    printf '%s\n' "${profiles[@]}"
}

# Create device JSON data
create_device_data() {
    cat << 'EOF'
[
    {
        "title": "Apple MacBook 12-inch",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 2304, "height": 1310},
            "horizontal": {"width": 1310, "height": 2304}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "Apple MacBook Pro 13-inch",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 2560, "height": 1470},
            "horizontal": {"width": 1470, "height": 2560}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "Apple MacBook Pro 15-inch",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 2880, "height": 1670},
            "horizontal": {"width": 1670, "height": 2880}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "iMac 24 - 2021",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 2048, "height": 1152},
            "horizontal": {"width": 1152, "height": 2048}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook PRO 16 - 2021",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1728, "height": 1117},
            "horizontal": {"width": 1117, "height": 1728}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook Air 13 - 2020",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1280, "height": 800},
            "horizontal": {"width": 800, "height": 1280}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook Pro 16 - 2019",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1536, "height": 960},
            "horizontal": {"width": 960, "height": 1536}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook Pro 13 - 2018",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1280, "height": 800},
            "horizontal": {"width": 800, "height": 1280}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook Air 13 - 2018",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1280, "height": 800},
            "horizontal": {"width": 800, "height": 1280}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook Pro 15 - 2018",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1440, "height": 900},
            "horizontal": {"width": 900, "height": 1440}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook Pro 13 Pro - 2017",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1440, "height": 900},
            "horizontal": {"width": 900, "height": 1440}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook Pro 15 Pro - 2017",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1280, "height": 800},
            "horizontal": {"width": 800, "height": 1280}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook Pro 13 Pro - 2016",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1280, "height": 800},
            "horizontal": {"width": 800, "height": 1280}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook Pro 15 Pro - 2016",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1440, "height": 900},
            "horizontal": {"width": 900, "height": 1440}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook Pro 13 Pro - 2015",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1280, "height": 800},
            "horizontal": {"width": 800, "height": 1280}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook Pro 15 Pro - 2015",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1440, "height": 900},
            "horizontal": {"width": 900, "height": 1440}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "MacBook Pro 15 Pro - 2014",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1440, "height": 900},
            "horizontal": {"width": 900, "height": 1440}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "Notebook with touch",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": ["touch"],
        "screen": {
            "device-pixel-ratio": 1,
            "vertical": {"width": 1280, "height": 950},
            "horizontal": {"width": 950, "height": 1280}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "Notebook with HiDPI screen",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 2,
            "vertical": {"width": 1440, "height": 900},
            "horizontal": {"width": 900, "height": 1440}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "Dell Latitude 3420 14",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 1,
            "vertical": {"width": 1440, "height": 809},
            "horizontal": {"width": 809, "height": 1440}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    },
    {
        "title": "Microsoft Surface Duo",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
        "capabilities": ["mobile", "touch"],
        "screen": {
            "device-pixel-ratio": 2.5,
            "vertical": {"width": 1114, "height": 705},
            "horizontal": {"width": 705, "height": 1114}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": true
        }
    },
    {
        "title": "Generic notebook",
        "type": "unknown",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.1 Safari/605.1.15",
        "capabilities": [],
        "screen": {
            "device-pixel-ratio": 1,
            "vertical": {"width": 1280, "height": 800},
            "horizontal": {"width": 800, "height": 1280}
        },
        "modes": [
            {"title": "", "orientation": "vertical", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}},
            {"title": "", "orientation": "horizontal", "insets": {"left": 0, "top": 0, "right": 0, "bottom": 0}}
        ],
        "show-by-default": true,
        "dual-screen": false,
        "show": "Default",
        "user-agent-metadata": {
            "brands": [{"brand": "", "version": ""}],
            "fullVersionList": [{"brand": "", "version": ""}],
            "fullVersion": "",
            "platform": "",
            "platformVersion": "",
            "architecture": "",
            "model": "",
            "mobile": false
        }
    }
]
EOF
}

# Install devices to a specific profile
install_to_profile() {
    local preferences_path=$1
    local profile_name=$2
    local devices_json=$3
    
    # Create backup
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${preferences_path}.backup_${timestamp}"
    
    if ! cp "$preferences_path" "$backup_file" 2>/dev/null; then
        print_error "Failed to create backup for $profile_name"
        return 1
    fi
    
    # Create a temporary Python script to modify the JSON
    local temp_script=$(mktemp)
    cat > "$temp_script" << 'PYTHON_SCRIPT'
import json
import sys

def modify_preferences(preferences_path, devices_json_str):
    try:
        # Load current preferences
        with open(preferences_path, 'r', encoding='utf-8') as f:
            preferences = json.load(f)
        
        # Parse devices JSON
        devices = json.loads(devices_json_str)
        
        # Ensure devtools.preferences structure exists
        if "devtools" not in preferences:
            preferences["devtools"] = {}
        if "preferences" not in preferences["devtools"]:
            preferences["devtools"]["preferences"] = {}
        
        # Update with custom devices
        preferences["devtools"]["preferences"]["custom-emulated-device-list"] = devices
        
        # Write back to file
        with open(preferences_path, 'w', encoding='utf-8') as f:
            json.dump(preferences, f, separators=(',', ':'), ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    preferences_path = sys.argv[1]
    devices_json_str = sys.argv[2]
    success = modify_preferences(preferences_path, devices_json_str)
    sys.exit(0 if success else 1)
PYTHON_SCRIPT

    # Run the Python script
    if python3 "$temp_script" "$preferences_path" "$devices_json" 2>/dev/null; then
        rm -f "$temp_script"
        print_success "$profile_name"
        return 0
    else
        # Restore from backup on failure
        cp "$backup_file" "$preferences_path" 2>/dev/null
        rm -f "$temp_script"
        print_error "$profile_name (restored from backup)"
        return 1
    fi
}

# Main installation process
main() {
    local os=$(detect_os)
    
    if [[ "$os" == "unknown" ]]; then
        print_error "Unsupported operating system"
        exit 1
    fi
    
    print_progress "Detected OS: $os"
    
    # Check for Python 3
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python 3 is required but not installed"
        print_progress "Please install Python 3 and try again"
        exit 1
    fi
    
    print_success "Python 3 found: $(python3 --version)"
    
    # Check if Chrome is running
    if is_chrome_running "$os"; then
        print_warning "Chrome is currently running"
        print_progress "For best results, please close Chrome and run this script again"
        echo ""
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_progress "Installation cancelled"
            exit 0
        fi
    fi
    
    print_progress "${SEARCH} Scanning for Chrome profiles..."
    
    # Find all Chrome profiles
    local profiles=()
    while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            profiles+=("$line")
        fi
    done < <(find_chrome_profiles "$os")
    
    if [[ ${#profiles[@]} -eq 0 ]]; then
        print_error "No Chrome profiles found"
        print_progress "Please make sure Chrome is installed and has been run at least once"
        exit 1
    fi
    
    print_success "Found ${#profiles[@]} Chrome profile(s):"
    for profile in "${profiles[@]}"; do
        local profile_name="${profile##*|}"
        local chrome_variant=$(echo "$profile" | grep -o "Chrome[^/]*" | head -1 || echo "Chrome")
        echo "   • $chrome_variant $profile_name"
    done
    echo ""
    
    print_progress "${PACKAGE} Installing custom devices to all profiles..."
    
    # Get device data
    local devices_json=$(create_device_data)
    
    # Install to each profile
    local success_count=0
    local total_count=${#profiles[@]}
    
    for profile in "${profiles[@]}"; do
        IFS='|' read -r preferences_path profile_name <<< "$profile"
        local chrome_variant=$(echo "$preferences_path" | grep -o "Chrome[^/]*" | head -1 || echo "Chrome")
        
        if install_to_profile "$preferences_path" "$chrome_variant $profile_name" "$devices_json"; then
            ((success_count++))
        fi
    done
    
    echo ""
    if [[ $success_count -eq $total_count ]]; then
        print_success "${CELEBRATION} Successfully installed custom devices to all $total_count Chrome profiles!"
    elif [[ $success_count -gt 0 ]]; then
        print_warning "Installed to $success_count out of $total_count profiles"
    else
        print_error "Failed to install to any profiles"
        exit 1
    fi
    
    echo ""
    print_progress "${RESTART} Restart Chrome to see your new devices in DevTools > Settings > Devices"
    echo ""
    print_progress "Installed devices:"
    echo "   • Apple MacBook 12-inch"
    echo "   • Apple MacBook Pro 13-inch" 
    echo "   • Apple MacBook Pro 15-inch"
    echo "   • iMac 24 - 2021"
    echo "   • MacBook PRO 16 - 2021"
    echo "   • MacBook Air 13 - 2020"
    echo "   • MacBook Pro 16 - 2019"
    echo "   • MacBook Pro 13 - 2018"
    echo "   • MacBook Air 13 - 2018"
    echo "   • MacBook Pro 15 - 2018"
    echo "   • MacBook Pro 13 Pro - 2017"
    echo "   • MacBook Pro 15 Pro - 2017"
    echo "   • MacBook Pro 13 Pro - 2016"
    echo "   • MacBook Pro 15 Pro - 2016"
    echo "   • MacBook Pro 13 Pro - 2015"
    echo "   • MacBook Pro 15 Pro - 2015"
    echo "   • MacBook Pro 15 Pro - 2014"
    echo "   • Notebook with touch"
    echo "   • Notebook with HiDPI screen"
    echo "   • Dell Latitude 3420 14"
    echo "   • Microsoft Surface Duo"
    echo "   • Generic notebook"
}

# Run main function
main "$@"
