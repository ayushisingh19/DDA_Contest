#!/usr/bin/env python
"""Update Hello World problem with minimal starter code"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_auth.settings')
django.setup()

from accounts.models import Problem

def main():
    # Hello World minimal starter code templates
    stubs = {
        'python': '''def hello_world():
    """Return the classic Hello World greeting."""
    # Write your code here
    # Hint: Return "Hello, World!"
    pass''',
        
        'java': '''public class Solution {
    public static String helloWorld() {
        // Write your code here
        // Hint: Return "Hello, World!"
        return "";
    }
}''',
        
        'cpp': '''#include <iostream>
#include <string>
using namespace std;

string hello_world() {
    // Write your code here
    // Hint: Return "Hello, World!"
    return "";
}''',
        
        'csharp': '''using System;

public class Solution {
    public static string HelloWorld() {
        // Write your code here
        // Hint: Return "Hello, World!"
        return "";
    }
}''',
        
        'javascript': '''function hello_world() {
    // Write your code here
    // Hint: Return "Hello, World!"
}''',
        
        'typescript': '''function hello_world(): string {
    // Write your code here
    // Hint: Return "Hello, World!"
    return "";
}'''
    }
    
    try:
        # Get Hello World problem
        problem = Problem.objects.get(id=7)
        print(f'Found: {problem.title}')
        
        # Update with better settings
        problem.function_name = 'hello_world'
        problem.function_params = []  # No params for classic Hello World
        problem.return_type = 'str'   # Return string
        problem.default_stub = stubs
        problem.save()
        
        print('✅ Successfully updated Hello World!')
        print(f'Function: {problem.function_name}() -> {problem.return_type}')
        print(f'Languages: {list(stubs.keys())}')
        
        # Show sample Python starter code
        print('\n📝 Python starter code:')
        print(stubs['python'])
        
    except Problem.DoesNotExist:
        print('❌ Hello World problem (ID: 7) not found!')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    main()