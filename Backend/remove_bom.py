with open('datadump.json', 'rb') as f:
    content = f.read()

if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]
    with open('datadump.json', 'wb') as f:
        f.write(content)
    print("BOM removed successfully.")
else:
    print("No BOM found.")
