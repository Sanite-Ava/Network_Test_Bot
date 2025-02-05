import json

with open('config.json', 'r', encoding='utf-8') as f:
    config_data = json.load(f)

BOT_TOKEN = config_data.get('TELEGRAM_BOT_TOKEN')
ADMIN_USERS = config_data.get('ADMIN_USERS', [])
AUTHORIZED_USERS = config_data.get('AUTHORIZED_USERS', [])
SERVERS = config_data.get('SERVERS', [])

def save_config():
    config_data['AUTHORIZED_USERS'] = AUTHORIZED_USERS
    config_data['SERVERS'] = SERVERS
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
