"""
Starter Code (Function Stub) Generator

This module generates language-specific starter code templates for programming problems.
It supports Python, Java, C++, C#, and provides a generic fallback.
"""

from typing import List, Optional


class StubGenerator:
    """Generates starter code stubs for different programming languages"""

    @staticmethod
    def generate_stub(
        language: str,
        function_name: Optional[str] = None,
        params: Optional[List[str]] = None,
        return_type: Optional[str] = None,
        problem_title: Optional[str] = None,
    ) -> str:
        """
        Generate a starter code stub for the given language and function signature.

        Args:
            language: Programming language (python, java, cpp, csharp, etc.)
            function_name: Name of the function to implement
            params: List of parameter names
            return_type: Expected return type
            problem_title: Problem title for comments

        Returns:
            Generated starter code stub as a string
        """
        # Normalize language name
        language = language.lower().strip()

        # Set defaults
        if not function_name:
            function_name = "solution"
        if not params:
            params = []
        if not return_type:
            return_type = "int"  # Default return type

        # Generate comment with problem title
        title_comment = f" - {problem_title}" if problem_title else ""

        # Route to appropriate generator
        generators = {
            "python": StubGenerator._generate_python_stub,
            "python3": StubGenerator._generate_python_stub,
            "py": StubGenerator._generate_python_stub,
            "java": StubGenerator._generate_java_stub,
            "cpp": StubGenerator._generate_cpp_stub,
            "c++": StubGenerator._generate_cpp_stub,
            "cxx": StubGenerator._generate_cpp_stub,
            "csharp": StubGenerator._generate_csharp_stub,
            "c#": StubGenerator._generate_csharp_stub,
            "cs": StubGenerator._generate_csharp_stub,
            "javascript": StubGenerator._generate_javascript_stub,
            "js": StubGenerator._generate_javascript_stub,
            "typescript": StubGenerator._generate_typescript_stub,
            "ts": StubGenerator._generate_typescript_stub,
        }

        generator = generators.get(language, StubGenerator._generate_fallback_stub)
        return generator(function_name, params, return_type, title_comment)

    @staticmethod
    def _generate_python_stub(
        function_name: str, params: List[str], return_type: str, title_comment: str
    ) -> str:
        """Generate Python starter code"""
        param_str = ", ".join(params) if params else ""

        # Convert return type to Python type hint
        python_return_type = StubGenerator._convert_to_python_type(return_type)
        type_hint = f" -> {python_return_type}" if python_return_type != "None" else ""

        return f'''def {function_name}({param_str}){type_hint}:
    """
    TODO: Implement this function{title_comment}
    
    Args:
        {chr(10).join(f"{param}: TODO - describe parameter" for param in params) if params else "No parameters"}
    
    Returns:
        {python_return_type}: TODO - describe return value
    """
    # Write your code here
    pass'''

    @staticmethod
    def _generate_java_stub(
        function_name: str, params: List[str], return_type: str, title_comment: str
    ) -> str:
        """Generate Java starter code"""
        java_return_type = StubGenerator._convert_to_java_type(return_type)

        # Generate parameters with int type (default for competitive programming)
        java_params = []
        for param in params:
            param_type = "int"  # Default type for simplicity
            java_params.append(f"{param_type} {param}")
        param_str = ", ".join(java_params)

        # Capitalize function name for Java convention
        java_function_name = StubGenerator._to_camel_case(function_name)

        default_return = StubGenerator._get_java_default_return(java_return_type)

        # Generate param documentation
        param_docs = ""
        if params:
            param_docs = "\n".join(
                [f"     * @param {param} TODO - describe parameter" for param in params]
            )
        else:
            param_docs = "     * No parameters"

        return f"""public class Solution {{
    /**
     * TODO: Implement this method{title_comment}
     * 
{param_docs}
     * @return {java_return_type} TODO - describe return value
     */
    public static {java_return_type} {java_function_name}({param_str}) {{
        // Write your code here
        {default_return}
    }}
}}"""

    @staticmethod
    def _generate_cpp_stub(
        function_name: str, params: List[str], return_type: str, title_comment: str
    ) -> str:
        """Generate C++ starter code"""
        cpp_return_type = StubGenerator._convert_to_cpp_type(return_type)

        # Generate parameters with int type (default)
        cpp_params = []
        for param in params:
            param_type = "int"  # Default type
            cpp_params.append(f"{param_type} {param}")
        param_str = ", ".join(cpp_params)

        default_return = StubGenerator._get_cpp_default_return(cpp_return_type)

        # Generate param documentation
        param_docs = ""
        if params:
            param_docs = "\n".join(
                [f" * @param {param} TODO - describe parameter" for param in params]
            )
        else:
            param_docs = " * No parameters"

        return f"""#include <iostream>
#include <vector>
#include <string>
using namespace std;

/**
 * TODO: Implement this function{title_comment}
 * 
{param_docs}
 * @return {cpp_return_type} TODO - describe return value
 */
{cpp_return_type} {function_name}({param_str}) {{
    // Write your code here
    {default_return}
}}"""

    @staticmethod
    def _generate_csharp_stub(
        function_name: str, params: List[str], return_type: str, title_comment: str
    ) -> str:
        """Generate C# starter code"""
        csharp_return_type = StubGenerator._convert_to_csharp_type(return_type)

        # Generate parameters with int type (default)
        csharp_params = []
        for param in params:
            param_type = "int"  # Default type
            csharp_params.append(f"{param_type} {param}")
        param_str = ", ".join(csharp_params)

        # Capitalize function name for C# convention
        csharp_function_name = StubGenerator._to_pascal_case(function_name)

        default_return = StubGenerator._get_csharp_default_return(csharp_return_type)

        # Generate param documentation
        param_docs = ""
        if params:
            param_docs = "\n".join(
                [
                    f'    /// <param name="{param}">TODO - describe parameter</param>'
                    for param in params
                ]
            )

        return f"""using System;
using System.Collections.Generic;

public class Solution {{
    /// <summary>
    /// TODO: Implement this method{title_comment}
    /// </summary>
{param_docs}
    /// <returns>{csharp_return_type} TODO - describe return value</returns>
    public {csharp_return_type} {csharp_function_name}({param_str}) {{
        // Write your code here
        {default_return}
    }}
}}"""

    @staticmethod
    def _generate_javascript_stub(
        function_name: str, params: List[str], return_type: str, title_comment: str
    ) -> str:
        """Generate JavaScript starter code"""
        param_str = ", ".join(params) if params else ""

        # Generate param documentation
        param_docs = ""
        if params:
            param_docs = "\n".join(
                [
                    f" * @param {{{param}}} - TODO: describe parameter"
                    for param in params
                ]
            )
        else:
            param_docs = " * No parameters"

        return f"""/**
 * TODO: Implement this function{title_comment}
 * 
{param_docs}
 * @returns {{*}} TODO - describe return value
 */
function {function_name}({param_str}) {{
    // Write your code here
}}"""

    @staticmethod
    def _generate_typescript_stub(
        function_name: str, params: List[str], return_type: str, title_comment: str
    ) -> str:
        """Generate TypeScript starter code"""
        ts_return_type = StubGenerator._convert_to_typescript_type(return_type)

        # Generate typed parameters
        ts_params = []
        for param in params:
            param_type = "number"  # Default type
            ts_params.append(f"{param}: {param_type}")
        param_str = ", ".join(ts_params)

        # Generate param documentation
        param_docs = ""
        if params:
            param_docs = "\n".join(
                [
                    f" * @param {{{param}}} - TODO: describe parameter"
                    for param in params
                ]
            )
        else:
            param_docs = " * No parameters"

        return f"""/**
 * TODO: Implement this function{title_comment}
 * 
{param_docs}
 * @returns {{{ts_return_type}}} TODO - describe return value
 */
function {function_name}({param_str}): {ts_return_type} {{
    // Write your code here
    return 0; // Replace with actual implementation
}}"""

    @staticmethod
    def _generate_fallback_stub(
        function_name: str, params: List[str], return_type: str, title_comment: str
    ) -> str:
        """Generate generic fallback starter code"""
        param_str = ", ".join(params) if params else ""

        return f"""/*
 * TODO: Implement function '{function_name}'{title_comment}
 * 
 * Parameters: {param_str or "none"}
 * Return type: {return_type}
 * 
 * Write your solution below:
 */

// Your code here"""

    # Helper methods for type conversion
    @staticmethod
    def _convert_to_python_type(return_type: str) -> str:
        """Convert generic return type to Python type hint"""
        type_map = {
            "int": "int",
            "integer": "int",
            "float": "float",
            "double": "float",
            "string": "str",
            "str": "str",
            "bool": "bool",
            "boolean": "bool",
            "list": "List[int]",
            "array": "List[int]",
            "vector": "List[int]",
            "void": "None",
            "none": "None",
        }
        return type_map.get(return_type.lower(), "int")

    @staticmethod
    def _convert_to_java_type(return_type: str) -> str:
        """Convert generic return type to Java type"""
        type_map = {
            "int": "int",
            "integer": "int",
            "float": "double",
            "double": "double",
            "string": "String",
            "str": "String",
            "bool": "boolean",
            "boolean": "boolean",
            "list": "int[]",
            "array": "int[]",
            "vector": "int[]",
            "void": "void",
            "none": "void",
        }
        return type_map.get(return_type.lower(), "int")

    @staticmethod
    def _convert_to_cpp_type(return_type: str) -> str:
        """Convert generic return type to C++ type"""
        type_map = {
            "int": "int",
            "integer": "int",
            "float": "double",
            "double": "double",
            "string": "string",
            "str": "string",
            "bool": "bool",
            "boolean": "bool",
            "list": "vector<int>",
            "array": "vector<int>",
            "vector": "vector<int>",
            "void": "void",
            "none": "void",
        }
        return type_map.get(return_type.lower(), "int")

    @staticmethod
    def _convert_to_csharp_type(return_type: str) -> str:
        """Convert generic return type to C# type"""
        type_map = {
            "int": "int",
            "integer": "int",
            "float": "double",
            "double": "double",
            "string": "string",
            "str": "string",
            "bool": "bool",
            "boolean": "bool",
            "list": "int[]",
            "array": "int[]",
            "vector": "int[]",
            "void": "void",
            "none": "void",
        }
        return type_map.get(return_type.lower(), "int")

    @staticmethod
    def _convert_to_typescript_type(return_type: str) -> str:
        """Convert generic return type to TypeScript type"""
        type_map = {
            "int": "number",
            "integer": "number",
            "float": "number",
            "double": "number",
            "string": "string",
            "str": "string",
            "bool": "boolean",
            "boolean": "boolean",
            "list": "number[]",
            "array": "number[]",
            "vector": "number[]",
            "void": "void",
            "none": "void",
        }
        return type_map.get(return_type.lower(), "number")

    @staticmethod
    def _get_java_default_return(java_type: str) -> str:
        """Get default return statement for Java"""
        defaults = {
            "int": "return 0;",
            "double": "return 0.0;",
            "boolean": "return false;",
            "String": 'return "";',
            "int[]": "return new int[0];",
            "void": "",
        }
        return defaults.get(java_type, "return null;")

    @staticmethod
    def _get_cpp_default_return(cpp_type: str) -> str:
        """Get default return statement for C++"""
        defaults = {
            "int": "return 0;",
            "double": "return 0.0;",
            "bool": "return false;",
            "string": 'return "";',
            "vector<int>": "return {};",
            "void": "",
        }
        return defaults.get(cpp_type, "return 0;")

    @staticmethod
    def _get_csharp_default_return(csharp_type: str) -> str:
        """Get default return statement for C#"""
        defaults = {
            "int": "return 0;",
            "double": "return 0.0;",
            "bool": "return false;",
            "string": 'return "";',
            "int[]": "return new int[0];",
            "void": "",
        }
        return defaults.get(csharp_type, "return default;")

    @staticmethod
    def _to_camel_case(snake_str: str) -> str:
        """Convert snake_case to camelCase"""
        if not snake_str:
            return snake_str
        components = snake_str.split("_")
        return components[0] + "".join(word.capitalize() for word in components[1:])

    @staticmethod
    def _to_pascal_case(snake_str: str) -> str:
        """Convert snake_case to PascalCase"""
        if not snake_str:
            return snake_str
        return "".join(word.capitalize() for word in snake_str.split("_"))


# Convenience function for direct usage
def generate_starter_code(language: str, problem=None, **kwargs) -> str:
    """
    Generate starter code for a given language and problem.

    Args:
        language: Programming language
        problem: Problem model instance (optional)
        **kwargs: Override values for function_name, params, return_type, etc.

    Returns:
        Generated starter code string
    """
    # Extract values from problem model if provided
    if problem:
        function_name = kwargs.get("function_name", problem.function_name)
        params = kwargs.get("params", problem.function_params or [])
        return_type = kwargs.get("return_type", problem.return_type)
        problem_title = kwargs.get("problem_title", problem.title)

        # Check if problem has custom stub for this language
        if problem.default_stub and isinstance(problem.default_stub, dict):
            custom_stub = problem.default_stub.get(language.lower())
            if custom_stub:
                return custom_stub
    else:
        function_name = kwargs.get("function_name")
        params = kwargs.get("params", [])
        return_type = kwargs.get("return_type")
        problem_title = kwargs.get("problem_title")

    return StubGenerator.generate_stub(
        language=language,
        function_name=function_name,
        params=params,
        return_type=return_type,
        problem_title=problem_title,
    )
