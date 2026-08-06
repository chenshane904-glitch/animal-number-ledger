import json

with open('play_groups.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

print("0尾对应的号码:", config.get("0尾"))
print("3尾对应的号码:", config.get("3尾"))
