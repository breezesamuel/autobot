import json

try:
    with open('/opt/bingdashan/data/db.json', 'r') as f:
        db = json.load(f)
    
    leads = db.get('leads', [])
    print(f'Total leads: {len(leads)}')
    
    emails = [l.get('email', '') for l in leads if l.get('email')]
    print(f'With email: {len(emails)}')
    
    if emails:
        print('\nEmail list:')
        for e in emails[:20]:
            print(f'  - {e}')
    
    # Check for other contact methods
    phones = [l.get('phone', '') for l in leads if l.get('phone')]
    print(f'\nWith phone: {len(phones)}')
    
    wechat = [l.get('wechat', '') for l in leads if l.get('wechat')]
    print(f'With WeChat: {len(wechat)}')
    
    # Show all lead fields
    if leads:
        print('\nSample lead fields:', list(leads[0].keys()))
        
except Exception as e:
    print(f'Error: {e}')
