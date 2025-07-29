#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

console.log('📦 Chrome Custom Devices - Post-install setup');
console.log('===============================================\n');

try {
    // Make the bin script executable
    const binPath = path.join(__dirname, '..', 'bin', 'chrome-devices');
    execSync(`chmod +x "${binPath}"`, { stdio: 'inherit' });
    
    console.log('✅ Package installed successfully!');
    console.log('\n🎯 Usage:');
    console.log('   chrome-devices              # Install devices to Chrome');
    console.log('   chrome-devices --help       # Show help\n');
    
    console.log('🚀 Ready to enhance your Chrome DevTools with desktop devices!');
    
} catch (error) {
    console.warn('⚠️  Post-install setup had minor issues, but the package should still work.');
}
