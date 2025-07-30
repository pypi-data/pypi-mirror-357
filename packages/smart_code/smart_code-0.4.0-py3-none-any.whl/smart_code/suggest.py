# 定义多语言静态文本
MESSAGES = {
    'zh': {
        'suggestion_prefix': '☛ 优化建议',
        'complexity_prefix': '复杂度',
        'hint_prefix': '提示'
    },
    'en': {
        'suggestion_prefix': '☛ Suggestion',
        'complexity_prefix': 'Complexity',
        'hint_prefix': 'Hint'
    }
}

def format_issue(issue, lang='zh'):
    lang_msgs = MESSAGES.get(lang, MESSAGES['en'])  # 默认回退到英文
    
    parts = []
    parts.append(f"[Line {issue['lineno']}] {issue['description']}")
    
    if issue.get('suggestion'):
        parts.append(f"{lang_msgs['suggestion_prefix']}：{issue['suggestion']}")
    if issue.get('complexity'):
        parts.append(f"{lang_msgs['complexity_prefix']}：{issue['complexity']}")
    if issue.get('hint'):
        parts.append(f"{lang_msgs['hint_prefix']}：{issue['hint']}")
        
    return '\n'.join(parts)
