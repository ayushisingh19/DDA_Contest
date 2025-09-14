"""
Hello World Starter Code Generator for DDT Coding Platform

This module provides optimized starter code templates specifically for 
Hello World problems with clean, minimal templates and helpful hints.
"""

def generate_hello_world_stub(language, function_name="hello_world", has_params=False):
    """
    Generate Hello World starter code for specific language.
    
    Args:
        language: Programming language (python, java, cpp, csharp, javascript, typescript)
        function_name: Name of the function (default: hello_world)
        has_params: Whether function takes parameters (default: False)
        
    Returns:
        str: Clean starter code template
    """
    language = language.lower().strip()
    
    # Language mapping
    generators = {
        'python': _python_stub,
        'py': _python_stub,
        'python3': _python_stub,
        'java': _java_stub,
        'cpp': _cpp_stub,
        'c++': _cpp_stub,
        'csharp': _csharp_stub,
        'c#': _csharp_stub,
        'cs': _csharp_stub,
        'javascript': _javascript_stub,
        'js': _javascript_stub,
        'typescript': _typescript_stub,
        'ts': _typescript_stub,
    }
    
    generator = generators.get(language, _fallback_stub)
    return generator(function_name, has_params)


def _python_stub(function_name, has_params):
    if has_params:
        return f'''def {function_name}(name):
    """Return a personalized greeting message."""
    # Write your code here
    # Hint: Use f"Hello, {{name}}!" or similar
    pass'''
    else:
        return f'''def {function_name}():
    """Return the classic Hello World greeting."""
    # Write your code here
    # Hint: Return "Hello, World!"
    pass'''


def _java_stub(function_name, has_params):
    java_name = _to_camel_case(function_name)
    
    if has_params:
        return f'''public class Solution {{
    public static String {java_name}(String name) {{
        // Write your code here
        // Hint: Return "Hello, " + name + "!"
        return "";
    }}
}}'''
    else:
        return f'''public class Solution {{
    public static String {java_name}() {{
        // Write your code here
        // Hint: Return "Hello, World!"
        return "";
    }}
}}'''


def _cpp_stub(function_name, has_params):
    if has_params:
        return f'''#include <iostream>
#include <string>
using namespace std;

string {function_name}(string name) {{
    // Write your code here
    // Hint: Return "Hello, " + name + "!"
    return "";
}}'''
    else:
        return f'''#include <iostream>
#include <string>
using namespace std;

string {function_name}() {{
    // Write your code here
    // Hint: Return "Hello, World!"
    return "";
}}'''


def _csharp_stub(function_name, has_params):
    csharp_name = _to_pascal_case(function_name)
    
    if has_params:
        return f'''using System;

public class Solution {{
    public static string {csharp_name}(string name) {{
        // Write your code here
        // Hint: Return $"Hello, {{name}}!"
        return "";
    }}
}}'''
    else:
        return f'''using System;

public class Solution {{
    public static string {csharp_name}() {{
        // Write your code here
        // Hint: Return "Hello, World!"
        return "";
    }}
}}'''


def _javascript_stub(function_name, has_params):
    if has_params:
        return f'''function {function_name}(name) {{
    // Write your code here
    // Hint: Return `Hello, ${{name}}!`
}}'''
    else:
        return f'''function {function_name}() {{
    // Write your code here
    // Hint: Return "Hello, World!"
}}'''


def _typescript_stub(function_name, has_params):
    if has_params:
        return f'''function {function_name}(name: string): string {{
    // Write your code here
    // Hint: Return `Hello, ${{name}}!`
    return "";
}}'''
    else:
        return f'''function {function_name}(): string {{
    // Write your code here
    // Hint: Return "Hello, World!"
    return "";
}}'''


def _fallback_stub(function_name, has_params):
    param_info = "with name parameter" if has_params else "no parameters"
    return f'''// {function_name} ({param_info})
// Write your code here
// For Hello World: Return "Hello, World!" or personalized greeting'''


def _to_camel_case(snake_str):
    """Convert snake_case to camelCase"""
    if not snake_str:
        return snake_str
    components = snake_str.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def _to_pascal_case(snake_str):
    """Convert snake_case to PascalCase"""
    if not snake_str:
        return snake_str
    return ''.join(word.capitalize() for word in snake_str.split('_'))


# Quick test function
def demo_all_languages():
    """Demo function to show all language templates"""
    languages = ['python', 'java', 'cpp', 'csharp', 'javascript', 'typescript']
    
    print("🌟 HELLO WORLD STARTER CODE TEMPLATES")
    print("=" * 60)
    
    for lang in languages:
        print(f"\\n📝 {lang.upper()}")
        print("-" * 30)
        stub = generate_hello_world_stub(lang)
        print(stub)
        print()


if __name__ == "__main__":
    demo_all_languages()