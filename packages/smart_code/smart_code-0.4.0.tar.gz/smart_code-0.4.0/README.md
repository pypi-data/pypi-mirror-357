# smart_code

smart_code is a static analysis tool that detects inefficient Python code patterns (AST-based) and provides optimization suggestions. It covers Pandas/NumPy anti-patterns, algorithmic inefficiencies, and common Python pitfalls.

## Features

- **AST-Based Analysis**: Accurately detects code patterns without executing code.
- **Rich Pattern Library**: Covers a wide range of anti-patterns from Pandas usage to algorithmic mistakes.
- **Click-to-Navigate Output**: Terminal output is formatted as `file:line: message`, allowing you to jump directly to the code in modern IDEs (like VS Code or PyCharm).
- **Multi-language Support**: Suggestions can be displayed in English or Chinese.

## Usage

### Command-Line Interface

Analyze one or more Python files:
```bash
smart_code path/to/your_script.py [another_file.py ...]
```

To receive suggestions in English, use the `--lang en` flag:
```bash
smart_code path/to/your_script.py --lang en
```

The output will look like this, and you can typically `Ctrl+Click` or `Cmd+Click` the link to navigate:
```
path/to/your_script.py:15: [Line 15] Detected use of DataFrame.iterrows() to iterate over rows
☛ Suggestion：Use itertuples or vectorized operations instead
Complexity：O(n) vs O(n)
Hint：iterrows converts each row into a Series, which has poor performance
```

### Python API

You can also use `smart_code` programmatically in your own scripts.

```python
from smart_code.analyzer import CodeAnalyzer
from smart_code.suggest import format_issue

# Initialize the analyzer in a specific language ('zh' or 'en')
analyzer = CodeAnalyzer(lang='en')

issues = analyzer.analyze_file("script.py")

for issue in issues:
    # Format the output for printing
    formatted_message = format_issue(issue, lang='en')
    print(f"script.py:{issue['lineno']}: {formatted_message}")

# The raw issue dictionary is also available
# print(issues)
```
