import json
from accounts.models import Problem

# Hello World minimal starter code templates
stubs = {
    'python': 'def hello_world():\n    """Return the classic Hello World greeting."""\n    # Write your code here\n    # Hint: Return "Hello, World!"\n    pass',
    
    'java': 'public class Solution {\n    public static String helloWorld() {\n        // Write your code here\n        // Hint: Return "Hello, World!"\n        return "";\n    }\n}',
    
    'cpp': '#include <iostream>\n#include <string>\nusing namespace std;\n\nstring hello_world() {\n    // Write your code here\n    // Hint: Return "Hello, World!"\n    return "";\n}',
    
    'csharp': 'using System;\n\npublic class Solution {\n    public static string HelloWorld() {\n        // Write your code here\n        // Hint: Return "Hello, World!"\n        return "";\n    }\n}',
    
    'javascript': 'function hello_world() {\n    // Write your code here\n    // Hint: Return "Hello, World!"\n}',
    
    'typescript': 'function hello_world(): string {\n    // Write your code here\n    // Hint: Return "Hello, World!"\n    return "";\n}'
}

# Update Hello World problem
try:
    problem = Problem.objects.get(id=7)
    print(f'Found: {problem.title}')
    
    # Update with better settings
    problem.function_name = 'hello_world'
    problem.function_params = []  # No params for classic Hello World
    problem.return_type = 'str'
    problem.default_stub = stubs
    problem.save()
    
    print('✅ Updated Hello World with minimal starter code!')
    print(f'Languages: {list(stubs.keys())}')
    print('Function signature: hello_world() -> str')
    
except Exception as e:
    print(f'Error: {e}')