import os

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content = content.replace("toast.message", "toast?.message")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_file('src/pages/EventBudgetPage.tsx')
fix_file('src/pages/EventDashboardPage.tsx')
