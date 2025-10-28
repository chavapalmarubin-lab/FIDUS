"""
MT5 Bridge Unicode Log Fix Script
Removes all Unicode characters from log messages to prevent crashes
"""

import re
import sys
from pathlib import Path

def remove_unicode_from_file(file_path):
    """Remove Unicode emoji and special characters from Python file"""
    
    print(f"Processing: {file_path}")
    
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    original_content = content
    
    # Unicode replacements
    replacements = {
        # Checkmarks and crosses
        '✅': '[OK]',
        '✓': '[OK]',
        '❌': '[FAIL]',
        '✗': '[FAIL]',
        '⚠️': '[WARN]',
        '⚠': '[WARN]',
        
        # Arrows and symbols
        '→': '->',
        '←': '<-',
        '↑': '^',
        '↓': 'v',
        '⇒': '=>',
        '⏳': '[WAIT]',
        '⏰': '[TIME]',
        
        # Status symbols
        '🔍': '[SEARCH]',
        '🔧': '[FIX]',
        '🔄': '[SYNC]',
        '🔌': '[DISCONNECT]',
        '🔗': '[CONNECT]',
        '📡': '[API]',
        '📊': '[DATA]',
        '📈': '[UP]',
        '📉': '[DOWN]',
        '💾': '[SAVE]',
        '🚀': '[START]',
        '🎯': '[TARGET]',
        '🎉': '[SUCCESS]',
        '⚡': '[FAST]',
        '🔥': '[HOT]',
        '💡': '[INFO]',
        '📝': '[NOTE]',
        '📋': '[LIST]',
        '🚨': '[ALERT]',
        '💰': '$',
        '📬': '[EMAIL]',
        '🏆': '[WIN]',
        
        # Other common Unicode
        '•': '*',
        '…': '...',
        '–': '-',
        '—': '--',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
    }
    
    # Apply replacements
    for unicode_char, ascii_replacement in replacements.items():
        if unicode_char in content:
            count = content.count(unicode_char)
            content = content.replace(unicode_char, ascii_replacement)
            print(f"  Replaced {count} instances of '{unicode_char}' with '{ascii_replacement}'")
    
    # Remove any remaining non-ASCII characters in strings
    # This regex finds string literals and removes non-ASCII from them
    def replace_in_strings(match):
        string_content = match.group(0)
        # Keep the quotes, clean the content
        quote = string_content[0]
        inner = string_content[1:-1]
        # Remove or replace any remaining non-ASCII
        cleaned = ''.join(char if ord(char) < 128 else '?' for char in inner)
        return f'{quote}{cleaned}{quote}'
    
    # Apply to single and double quoted strings
    content = re.sub(r'"[^"]*"', replace_in_strings, content)
    content = re.sub(r"'[^']*'", replace_in_strings, content)
    
    if content != original_content:
        # Backup original
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"  Backup saved to: {backup_path}")
        
        # Write cleaned version
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  [OK] File cleaned and saved")
        return True
    else:
        print(f"  No Unicode characters found")
        return False

def main():
    """Main function"""
    print("=" * 70)
    print("MT5 BRIDGE UNICODE LOG FIX")
    print("=" * 70)
    print()
    
    # File to fix
    bridge_file = Path(r"C:\mt5_bridge_service\mt5_bridge_api_service.py")
    
    if not bridge_file.exists():
        print(f"[FAIL] File not found: {bridge_file}")
        print()
        print("Please update the path to your MT5 Bridge service file")
        return 1
    
    print(f"Target file: {bridge_file}")
    print()
    
    # Fix the file
    success = remove_unicode_from_file(bridge_file)
    
    print()
    print("=" * 70)
    if success:
        print("UNICODE FIX COMPLETE")
        print()
        print("Next steps:")
        print("1. Stop the current MT5 Bridge service")
        print("2. Start it again: python mt5_bridge_api_service.py")
        print("3. Verify it starts without Unicode errors")
        print("4. Configure Task Scheduler for auto-start")
    else:
        print("NO CHANGES NEEDED")
        print("File appears to be clean already")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
