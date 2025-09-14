#!/usr/bin/env python3
"""
Enhanced Generate Stub Implementation for Hello World Problem

This module creates optimized starter code templates specifically for 
"Hello World" problems with proper function signatures and helpful comments.
"""

def generate_stub(problem, language):
    """
    Generate language-appropriate starter code for Hello World problem.
    
    Args:
        problem: Problem object with title, function_name, function_params, etc.
        language: Programming language (python, java, cpp, csharp, etc.)
        
    Returns:
        str: Language-specific starter code template
    """
    # Normalize language name
    language = language.lower().strip()
    
    # Extract problem metadata
    title = getattr(problem, 'title', 'Hello World')
    function_name = getattr(problem, 'function_name', 'hello_world')
    params = getattr(problem, 'function_params', [])
    return_type = getattr(problem, 'return_type', 'str')
    
    # For Hello World specifically, optimize the function signature
    if 'hello' in title.lower() and 'world' in title.lower():
        # Hello World problems typically don't need complex inputs
        if not params or params == ['input_data']:
            params = []  # Most Hello World problems just output "Hello, World!"
        return_type = 'str'  # Hello World returns a string
    
    # Language-specific generators
    generators = {
        'python': generate_python_stub,
        'py': generate_python_stub,
        'python3': generate_python_stub,
        'java': generate_java_stub,
        'cpp': generate_cpp_stub,
        'c++': generate_cpp_stub,
        'cxx': generate_cpp_stub,
        'csharp': generate_csharp_stub,
        'c#': generate_csharp_stub,
        'cs': generate_csharp_stub,
        'javascript': generate_javascript_stub,
        'js': generate_javascript_stub,
        'typescript': generate_typescript_stub,
        'ts': generate_typescript_stub,
    }
    
    generator = generators.get(language, generate_fallback_stub)
    return generator(function_name, params, return_type, title)


def generate_python_stub(function_name, params, return_type, title):
    """Generate Python starter code for Hello World"""
    param_str = ", ".join(params) if params else ""
    
    if not params:  # No parameters - simple Hello World
        return f'''def {function_name}() -> str:
    """
    {title} - Return the classic greeting message.
    
    Returns:
        str: The Hello World greeting
    """
    # Write your code here
    # Hint: Return "Hello, World!" string
    pass'''
    
    else:  # With parameters - dynamic greeting
        param_docs = "\\n        ".join([f"{param}: Input parameter" for param in params])
        return f'''def {function_name}({param_str}) -> str:
    """
    {title} - Create a personalized greeting message.
    
    Args:
        {param_docs}
    
    Returns:
        str: Formatted greeting message
    """
    # Write your code here
    # Hint: Create a greeting using the input parameter(s)
    pass'''


def generate_java_stub(function_name, params, return_type, title):
    """Generate Java starter code for Hello World"""
    # Convert to camelCase for Java
    java_function_name = to_camel_case(function_name)
    
    if not params:  # No parameters
        return f'''public class Solution {{
    /**
     * {title} - Return the classic greeting message.
     * 
     * @return String The Hello World greeting
     */
    public static String {java_function_name}() {{
        // Write your code here
        // Hint: Return "Hello, World!" string
        return "";
    }}
}}'''
    
    else:  # With parameters
        java_params = ", ".join([f"String {param}" for param in params])
        param_docs = "\\n     * ".join([f"@param {param} Input parameter" for param in params])
        
        return f'''public class Solution {{
    /**
     * {title} - Create a personalized greeting message.
     * 
     * {param_docs}
     * @return String Formatted greeting message
     */
    public static String {java_function_name}({java_params}) {{
        // Write your code here
        // Hint: Create a greeting using the input parameter(s)
        return "";
    }}
}}'''


def generate_cpp_stub(function_name, params, return_type, title):
    """Generate C++ starter code for Hello World"""
    if not params:  # No parameters
        return f'''#include <iostream>
#include <string>
using namespace std;

/**
 * {title} - Return the classic greeting message.
 * 
 * @return string The Hello World greeting
 */
string {function_name}() {{
    // Write your code here
    // Hint: Return "Hello, World!" string
    return "";
}}'''
    
    else:  # With parameters
        cpp_params = ", ".join([f"string {param}" for param in params])
        param_docs = "\\n * ".join([f"@param {param} Input parameter" for param in params])
        
        return f'''#include <iostream>
#include <string>
using namespace std;

/**
 * {title} - Create a personalized greeting message.
 * 
 * {param_docs}
 * @return string Formatted greeting message
 */
string {function_name}({cpp_params}) {{
    // Write your code here
    // Hint: Create a greeting using the input parameter(s)
    return "";
}}'''


def generate_csharp_stub(function_name, params, return_type, title):
    """Generate C# starter code for Hello World"""
    # Convert to PascalCase for C#
    csharp_function_name = to_pascal_case(function_name)
    
    if not params:  # No parameters
        return f'''using System;

public class Solution {{
    /// <summary>
    /// {title} - Return the classic greeting message.
    /// </summary>
    /// <returns>The Hello World greeting</returns>
    public static string {csharp_function_name}() {{
        // Write your code here
        // Hint: Return "Hello, World!" string
        return "";
    }}
}}'''
    
    else:  # With parameters
        csharp_params = ", ".join([f"string {param}" for param in params])
        param_docs = "\\n    /// ".join([f"<param name=\"{param}\">Input parameter</param>" for param in params])
        
        return f'''using System;

public class Solution {{
    /// <summary>
    /// {title} - Create a personalized greeting message.
    /// </summary>
    /// {param_docs}
    /// <returns>Formatted greeting message</returns>
    public static string {csharp_function_name}({csharp_params}) {{
        // Write your code here
        // Hint: Create a greeting using the input parameter(s)
        return "";
    }}
}}'''


def generate_javascript_stub(function_name, params, return_type, title):
    """Generate JavaScript starter code for Hello World"""
    param_str = ", ".join(params) if params else ""
    
    if not params:  # No parameters
        return f'''/**
 * {title} - Return the classic greeting message.
 * 
 * @returns {{string}} The Hello World greeting
 */
function {function_name}() {{
    // Write your code here
    // Hint: Return "Hello, World!" string
}}'''
    
    else:  # With parameters
        param_docs = "\\n * ".join([f"@param {{{param}}} Input parameter" for param in params])
        
        return f'''/**
 * {title} - Create a personalized greeting message.
 * 
 * {param_docs}
 * @returns {{string}} Formatted greeting message
 */
function {function_name}({param_str}) {{
    // Write your code here
    // Hint: Create a greeting using the input parameter(s)
}}'''


def generate_typescript_stub(function_name, params, return_type, title):
    """Generate TypeScript starter code for Hello World"""
    if not params:  # No parameters
        return f'''/**
 * {title} - Return the classic greeting message.
 * 
 * @returns The Hello World greeting
 */
function {function_name}(): string {{
    // Write your code here
    // Hint: Return "Hello, World!" string
    return "";
}}'''
    
    else:  # With parameters
        ts_params = ", ".join([f"{param}: string" for param in params])
        param_docs = "\\n * ".join([f"@param {param} Input parameter" for param in params])
        
        return f'''/**
 * {title} - Create a personalized greeting message.
 * 
 * {param_docs}
 * @returns Formatted greeting message
 */
function {function_name}({ts_params}): string {{
    // Write your code here
    // Hint: Create a greeting using the input parameter(s)
    return "";
}}'''


def generate_fallback_stub(function_name, params, return_type, title):
    """Generate generic fallback starter code"""
    param_str = ", ".join(params) if params else "no parameters"
    
    return f'''/*
 * {title}
 * 
 * Function: {function_name}
 * Parameters: {param_str}
 * Return type: {return_type}
 * 
 * Instructions:
 * - Implement the {function_name} function
 * - For Hello World: typically return "Hello, World!" string
 * - Use appropriate syntax for your programming language
 */

// Write your code here'''


def to_camel_case(snake_str):
    """Convert snake_case to camelCase"""
    if not snake_str:
        return snake_str
    components = snake_str.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def to_pascal_case(snake_str):
    """Convert snake_case to PascalCase"""
    if not snake_str:
        return snake_str
    return ''.join(word.capitalize() for word in snake_str.split('_'))


# Example usage and testing
if __name__ == "__main__":
    # Mock problem object for testing
    class MockProblem:
        def __init__(self, title="Hello World", function_name="hello_world", 
                     function_params=None, return_type="str"):
            self.title = title
            self.function_name = function_name
            self.function_params = function_params or []
            self.return_type = return_type
    
    # Test cases
    print("=== HELLO WORLD STARTER CODE TEMPLATES ===\\n")
    
    # Case 1: Simple Hello World (no parameters)
    simple_problem = MockProblem()
    
    print("1. SIMPLE HELLO WORLD (No Parameters)")
    print("=" * 50)
    
    languages = ['python', 'java', 'cpp', 'csharp', 'javascript', 'typescript']
    
    for lang in languages:
        print(f"\\n--- {lang.upper()} ---")
        stub = generate_stub(simple_problem, lang)
        print(stub)
        print()
    
    # Case 2: Parameterized Hello World
    param_problem = MockProblem(
        title="Hello World with Name",
        function_name="hello_world",
        function_params=["name"],
        return_type="str"
    )
    
    print("\\n\\n2. PARAMETERIZED HELLO WORLD")
    print("=" * 50)
    
    for lang in ['python', 'java']:
        print(f"\\n--- {lang.upper()} ---")
        stub = generate_stub(param_problem, lang)
        print(stub)
        print()
    
    # Case 3: Fallback example
    print("\\n\\n3. FALLBACK EXAMPLE")
    print("=" * 30)
    fallback_stub = generate_stub(simple_problem, 'unknown_language')
    print(fallback_stub)