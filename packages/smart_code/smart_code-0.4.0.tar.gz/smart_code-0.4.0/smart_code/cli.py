import argparse
from smart_code.analyzer import CodeAnalyzer
from smart_code.suggest import format_issue

def main():
    parser = argparse.ArgumentParser(description='smart_code 0.2.0')
    parser.add_argument('files', nargs='+', help='Python files to analyze')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    parser.add_argument('--lang', choices=['zh', 'en'], default='zh', help='Language for suggestions (zh/en)')
    args = parser.parse_args()
    
    analyzer = CodeAnalyzer(lang=args.lang)
    all_issues = []
    
    for file in args.files:
        issues = analyzer.analyze_file(file)
        if args.json:
            all_issues.extend(issues)
        else:
            for issue in issues:
                # 输出格式：文件名:行号: 描述... 便于跳转
                print(f'{file}:{issue["lineno"]}: {format_issue(issue, lang=args.lang)}')
                
    if args.json:
        import json
        print(json.dumps(all_issues, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
