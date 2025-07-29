class ChromeCustomDevices < Formula
  desc "Add 22+ desktop device presets to Chrome DevTools with one command"
  homepage "https://github.com/hatimmakki/chrome-custom-devices"
  url "https://github.com/hatimmakki/chrome-custom-devices/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "TO_BE_UPDATED_AFTER_RELEASE"
  license "MIT"
  head "https://github.com/hatimmakki/chrome-custom-devices.git", branch: "main"

  depends_on "python@3.11"

  def install
    # Install Python modules
    system "python3", "-m", "pip", "install", "--target", libexec/"vendor", "."
    
    # Create wrapper script
    (bin/"chrome-devices").write <<~EOS
      #!/usr/bin/env python3
      import sys
      import os
      sys.path.insert(0, "#{libexec}/vendor")
      from chrome_devices_manager import main
      if __name__ == "__main__":
          main()
    EOS
    
    # Install bash script for direct access
    bin.install "quick-install.sh" => "chrome-devices-install"
    
    # Make scripts executable
    chmod 0755, bin/"chrome-devices"
    chmod 0755, bin/"chrome-devices-install"
  end

  test do
    # Test help command
    assert_match "Chrome Custom Devices Manager", shell_output("#{bin}/chrome-devices --help")
    
    # Test list profiles (should work even without Chrome installed)
    system "#{bin}/chrome-devices", "--list-profiles"
  end

  def caveats
    <<~EOS
      Chrome Custom Devices has been installed!

      Usage:
        chrome-devices --install-all     # Install to all Chrome profiles
        chrome-devices --list-profiles   # List available profiles
        chrome-devices-install           # Run the bash installer directly

      The tool adds 22+ desktop device presets including:
      • MacBook models (12", 13", 15", 16") from 2014-2021
      • iMac 24" - 2021
      • MacBook Air models  
      • Notebooks with touch and HiDPI screens
      • Dell Latitude, Microsoft Surface Duo

      Perfect for testing responsive designs on actual desktop resolutions!

      Restart Chrome after installation to see devices in DevTools > Settings > Devices
    EOS
  end
end
