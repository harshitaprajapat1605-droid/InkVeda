import os

def convert_to_utf8(filename):
    try:
        # Try reading as UTF-16 LE (most common cause of 0xff 0xfe)
        with open(filename, 'r', encoding='utf-16') as f:
            content = f.read()
        
        # Write back as UTF-8
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully converted {filename} to UTF-8")
    except Exception as e:
        print(f"Failed to convert {filename}: {e}")

# Convert all datadump files
for f in ['datadump.json', 'datadump_accounts.json', 'datadump_fixed.json']:
    if os.path.exists(f):
        convert_to_utf8(f)
