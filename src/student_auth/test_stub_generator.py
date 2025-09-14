"""
Unit Tests for Function Stub Generator

Tests the stub generation functionality for all supported languages
and validates proper generation of starter code templates.
"""

import unittest
from django.test import TestCase
from accounts.stub_generator import StubGenerator, generate_starter_code
from accounts.models import Problem, Contest
from django.utils import timezone


class StubGeneratorTest(TestCase):
    """Test cases for the StubGenerator class"""

    def setUp(self):
        """Set up test data"""
        self.contest = Contest.objects.create(
            name="Test Contest", start_at=timezone.now(), duration_minutes=120
        )

        self.problem = Problem.objects.create(
            contest=self.contest,
            code="P1",
            title="Add Two Numbers",
            function_name="add_numbers",
            function_params=["a", "b"],
            return_type="int",
        )

    def test_python_stub_generation(self):
        """Test Python starter code generation"""
        stub = StubGenerator.generate_stub(
            "python", "add_numbers", ["a", "b"], "int", " - Add Two Numbers"
        )

        self.assertIn("def add_numbers(a, b) -> int:", stub)
        self.assertIn("# Write your code here", stub)
        self.assertIn("pass", stub)
        self.assertIn("Add Two Numbers", stub)

    def test_java_stub_generation(self):
        """Test Java starter code generation"""
        stub = StubGenerator.generate_stub("java", "add_numbers", ["a", "b"], "int")

        self.assertIn("public class Solution", stub)
        self.assertIn("public static int addNumbers(int a, int b)", stub)
        self.assertIn("return 0;", stub)
        self.assertIn("// Write your code here", stub)

    def test_cpp_stub_generation(self):
        """Test C++ starter code generation"""
        stub = StubGenerator.generate_stub("cpp", "add_numbers", ["x", "y"], "int")

        self.assertIn("#include <iostream>", stub)
        self.assertIn("int add_numbers(int x, int y)", stub)
        self.assertIn("return 0;", stub)
        self.assertIn("// Write your code here", stub)

    def test_csharp_stub_generation(self):
        """Test C# starter code generation"""
        stub = StubGenerator.generate_stub("csharp", "solve_problem", ["data"], "int")

        self.assertIn("using System;", stub)
        self.assertIn("public class Solution", stub)
        self.assertIn("public int SolveProblem(int data)", stub)
        self.assertIn("return 0;", stub)

    def test_javascript_stub_generation(self):
        """Test JavaScript starter code generation"""
        stub = StubGenerator.generate_stub(
            "javascript", "calculateSum", ["arr"], "number"
        )

        self.assertIn("function calculateSum(arr)", stub)
        self.assertIn("// Write your code here", stub)
        self.assertIn("@param", stub)

    def test_typescript_stub_generation(self):
        """Test TypeScript starter code generation"""
        stub = StubGenerator.generate_stub(
            "typescript", "findMax", ["numbers"], "number"
        )

        self.assertIn("function findMax(numbers: number): number", stub)
        self.assertIn("return 0;", stub)
        self.assertIn("// Write your code here", stub)

    def test_fallback_stub_generation(self):
        """Test fallback stub for unsupported languages"""
        stub = StubGenerator.generate_stub(
            "unknown_language", "test_function", ["param1", "param2"], "string"
        )

        self.assertIn("test_function", stub)
        self.assertIn("param1, param2", stub)
        self.assertIn("// Your code here", stub)

    def test_empty_parameters(self):
        """Test stub generation with no parameters"""
        stub = StubGenerator.generate_stub("python", "get_answer", [], "int")

        self.assertIn("def get_answer() -> int:", stub)
        self.assertIn("No parameters", stub)

    def test_type_conversion_python(self):
        """Test type conversion to Python types"""
        self.assertEqual(StubGenerator._convert_to_python_type("int"), "int")
        self.assertEqual(StubGenerator._convert_to_python_type("string"), "str")
        self.assertEqual(StubGenerator._convert_to_python_type("list"), "List[int]")
        self.assertEqual(StubGenerator._convert_to_python_type("boolean"), "bool")

    def test_type_conversion_java(self):
        """Test type conversion to Java types"""
        self.assertEqual(StubGenerator._convert_to_java_type("int"), "int")
        self.assertEqual(StubGenerator._convert_to_java_type("string"), "String")
        self.assertEqual(StubGenerator._convert_to_java_type("list"), "int[]")
        self.assertEqual(StubGenerator._convert_to_java_type("boolean"), "boolean")

    def test_camel_case_conversion(self):
        """Test snake_case to camelCase conversion"""
        self.assertEqual(StubGenerator._to_camel_case("add_numbers"), "addNumbers")
        self.assertEqual(StubGenerator._to_camel_case("calculate_sum"), "calculateSum")
        self.assertEqual(StubGenerator._to_camel_case("solution"), "solution")

    def test_pascal_case_conversion(self):
        """Test snake_case to PascalCase conversion"""
        self.assertEqual(StubGenerator._to_pascal_case("add_numbers"), "AddNumbers")
        self.assertEqual(StubGenerator._to_pascal_case("solve_problem"), "SolveProblem")

    def test_language_name_normalization(self):
        """Test that language names are properly normalized"""
        # Test various ways to specify Python
        for lang in ["python", "Python", "PYTHON", "py", "python3"]:
            stub = StubGenerator.generate_stub(lang, "test", [], "int")
            self.assertIn("def test", stub)

        # Test various ways to specify Java
        for lang in ["java", "Java", "JAVA"]:
            stub = StubGenerator.generate_stub(lang, "test", [], "int")
            self.assertIn("public class Solution", stub)

    def test_generate_starter_code_function(self):
        """Test the convenience function with Problem model"""
        stub = generate_starter_code("python", self.problem)

        self.assertIn("def add_numbers(a, b) -> int:", stub)
        self.assertIn("Add Two Numbers", stub)

    def test_custom_stub_override(self):
        """Test that custom stubs override generated ones"""
        # Set a custom Python stub
        self.problem.default_stub = {
            "python": "# Custom Python starter code\ndef custom_solution():\n    return 42"
        }
        self.problem.save()

        stub = generate_starter_code("python", self.problem)
        self.assertEqual(
            stub, "# Custom Python starter code\ndef custom_solution():\n    return 42"
        )

    def test_multiple_languages_consistency(self):
        """Test that function names are consistent across languages"""
        languages = ["python", "java", "cpp", "csharp"]
        function_name = "solve_puzzle"
        params = ["input_data"]

        stubs = {}
        for lang in languages:
            stubs[lang] = StubGenerator.generate_stub(
                lang, function_name, params, "int"
            )

        # Python should keep snake_case
        self.assertIn("solve_puzzle", stubs["python"])

        # Java should use camelCase
        self.assertIn("solvePuzzle", stubs["java"])

        # C++ should keep snake_case
        self.assertIn("solve_puzzle", stubs["cpp"])

        # C# should use PascalCase
        self.assertIn("SolvePuzzle", stubs["csharp"])

    def test_return_type_defaults(self):
        """Test proper default return values for different languages"""
        # Test Java defaults
        java_stub = StubGenerator.generate_stub("java", "test", [], "String")
        self.assertIn('return "";', java_stub)

        java_stub_int = StubGenerator.generate_stub("java", "test", [], "int")
        self.assertIn("return 0;", java_stub_int)

        # Test C++ defaults
        cpp_stub = StubGenerator.generate_stub("cpp", "test", [], "string")
        self.assertIn('return "";', cpp_stub)

    def test_problem_without_metadata(self):
        """Test stub generation for problem without function metadata"""
        problem_no_meta = Problem.objects.create(
            contest=self.contest,
            code="P2",
            title="Basic Problem",
            # No function_name, function_params, return_type
        )

        stub = generate_starter_code("python", problem_no_meta)

        # Should use defaults
        self.assertIn("def solution", stub)
        self.assertIn("Basic Problem", stub)


class StubGeneratorIntegrationTest(TestCase):
    """Integration tests for stub generation with Django models"""

    def setUp(self):
        """Set up test data"""
        self.contest = Contest.objects.create(
            name="Integration Test Contest",
            start_at=timezone.now(),
            duration_minutes=60,
        )

    def test_problem_creation_with_stubs(self):
        """Test creating a problem and generating stubs"""
        problem = Problem.objects.create(
            contest=self.contest,
            code="INTEGRATION1",
            title="Integration Test Problem",
            function_name="calculate_result",
            function_params=["x", "y", "z"],
            return_type="float",
        )

        # Generate stubs for multiple languages
        languages = ["python", "java", "cpp", "csharp", "javascript"]
        stubs = {}

        for lang in languages:
            stubs[lang] = generate_starter_code(lang, problem)
            self.assertIsNotNone(stubs[lang])
            self.assertGreater(len(stubs[lang]), 10)  # Reasonable stub length

        # Verify function names appear correctly
        self.assertIn("calculate_result", stubs["python"])
        self.assertIn("calculateResult", stubs["java"])
        self.assertIn("calculate_result", stubs["cpp"])
        self.assertIn("CalculateResult", stubs["csharp"])
        self.assertIn("calculate_result", stubs["javascript"])

    def test_bulk_stub_generation(self):
        """Test generating stubs for multiple problems"""
        problems = []
        for i in range(3):
            problem = Problem.objects.create(
                contest=self.contest,
                code=f"BULK{i+1}",
                title=f"Bulk Test Problem {i+1}",
                function_name=f"solve_problem_{i+1}",
                function_params=["data"],
                return_type="int",
            )
            problems.append(problem)

        # Generate Python stubs for all problems
        for problem in problems:
            stub = generate_starter_code("python", problem)
            self.assertIn(f"solve_problem_{problems.index(problem)+1}", stub)
            self.assertIn(f"Bulk Test Problem {problems.index(problem)+1}", stub)

    def test_edge_cases(self):
        """Test edge cases in stub generation"""
        # Problem with special characters in title
        problem_special = Problem.objects.create(
            contest=self.contest,
            code="SPECIAL",
            title="Problem: Find Max Element (Advanced)",
            function_name="find_max_element",
            function_params=["arr", "n"],
            return_type="int",
        )

        stub = generate_starter_code("python", problem_special)
        self.assertIn("find_max_element", stub)
        self.assertIn("Problem: Find Max Element", stub)

        # Problem with long parameter list
        problem_many_params = Problem.objects.create(
            contest=self.contest,
            code="MANYPARAMS",
            title="Complex Function",
            function_name="complex_calculation",
            function_params=["a", "b", "c", "d", "e", "f"],
            return_type="List[int]",
        )

        stub = generate_starter_code("python", problem_many_params)
        self.assertIn("def complex_calculation(a, b, c, d, e, f)", stub)
        self.assertIn("List[int]", stub)


if __name__ == "__main__":
    unittest.main()
