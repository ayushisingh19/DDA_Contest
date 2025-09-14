"""
Integration Tests for Starter Code API Endpoints

Tests the API endpoints for problem details and starter code generation.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import Problem, Contest, Student


class StarterCodeAPITest(TestCase):
    """Test cases for starter code API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create test contest and problem
        self.contest = Contest.objects.create(
            name="API Test Contest", start_at=timezone.now(), duration_minutes=120
        )

        self.problem = Problem.objects.create(
            contest=self.contest,
            code="API1",
            title="API Test Problem",
            description="Test problem for API validation",
            function_name="solve_api_problem",
            function_params=["input_value", "option"],
            return_type="str",
            constraints="1 <= input_value <= 1000",
        )

        # Create test student
        self.student = Student.objects.create(
            name="Test Student",
            email="test@example.com",
            password="hashedpassword",
            mobile="1234567890",
            college="Test College",
            passout_year=2024,
            branch="Computer Science",
        )

    def test_get_problem_detail_api(self):
        """Test the problem detail API endpoint"""
        url = reverse("problem_detail_api", kwargs={"problem_id": self.problem.id})

        # Test with default language (Python)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["id"], self.problem.id)
        self.assertEqual(data["title"], "API Test Problem")
        self.assertEqual(data["function_name"], "solve_api_problem")
        self.assertEqual(data["function_params"], ["input_value", "option"])
        self.assertEqual(data["return_type"], "str")
        self.assertIn("starter_code", data)
        self.assertIn("def solve_api_problem", data["starter_code"])

    def test_get_problem_detail_with_language_parameter(self):
        """Test problem detail API with specific language"""
        url = reverse("problem_detail_api", kwargs={"problem_id": self.problem.id})

        # Test with Java
        response = self.client.get(url, {"language": "java"})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("public class Solution", data["starter_code"])
        self.assertIn("solveApiProblem", data["starter_code"])  # camelCase conversion

    def test_get_starter_code_api(self):
        """Test the standalone starter code API endpoint"""
        url = reverse("starter_code_api", kwargs={"problem_id": self.problem.id})

        # Test Python starter code
        response = self.client.get(url, {"language": "python"})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["language"], "python")
        self.assertEqual(data["function_name"], "solve_api_problem")
        self.assertEqual(data["function_params"], ["input_value", "option"])
        self.assertIn("def solve_api_problem", data["starter_code"])

    def test_get_starter_code_different_languages(self):
        """Test starter code generation for different languages"""
        url = reverse("starter_code_api", kwargs={"problem_id": self.problem.id})

        languages = ["python", "java", "cpp", "csharp", "javascript", "typescript"]

        for language in languages:
            with self.subTest(language=language):
                response = self.client.get(url, {"language": language})
                self.assertEqual(response.status_code, 200)

                data = response.json()
                self.assertEqual(data["language"], language)
                self.assertIn("starter_code", data)
                self.assertGreater(len(data["starter_code"]), 10)

    def test_problem_not_found(self):
        """Test API response for non-existent problem"""
        url = reverse("problem_detail_api", kwargs={"problem_id": 99999})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_problem_with_custom_stub(self):
        """Test API when problem has custom starter code"""
        custom_stubs = {
            "python": '# Custom Python code\ndef custom_solution():\n    return "custom"',
            "java": "public class Custom {\n    // Custom Java code\n}",
        }

        self.problem.default_stub = custom_stubs
        self.problem.save()

        # Test Python custom stub
        url = reverse("starter_code_api", kwargs={"problem_id": self.problem.id})
        response = self.client.get(url, {"language": "python"})
        data = response.json()

        self.assertEqual(data["starter_code"], custom_stubs["python"])

        # Test Java custom stub
        response = self.client.get(url, {"language": "java"})
        data = response.json()

        self.assertEqual(data["starter_code"], custom_stubs["java"])

        # Test language without custom stub (should generate default)
        response = self.client.get(url, {"language": "cpp"})
        data = response.json()

        self.assertNotEqual(data["starter_code"], custom_stubs["python"])
        self.assertIn("solve_api_problem", data["starter_code"])

    def test_problem_detail_includes_solved_status(self):
        """Test that problem detail includes solved status for logged-in students"""
        # Test without login (should default to false)
        url = reverse("problem_detail_api", kwargs={"problem_id": self.problem.id})
        response = self.client.get(url)
        data = response.json()
        self.assertFalse(data["is_solved"])

        # Test with student session (mock login)
        session = self.client.session
        session["student_id"] = self.student.id
        session.save()

        response = self.client.get(url)
        data = response.json()
        self.assertFalse(data["is_solved"])  # Problem not yet solved

        # TODO: Add test case for solved problem (requires UserSolution creation)

    def test_problem_detail_includes_visible_testcases(self):
        """Test that problem detail includes visible test cases"""
        url = reverse("problem_detail_api", kwargs={"problem_id": self.problem.id})
        response = self.client.get(url)
        data = response.json()

        self.assertIn("visible_testcases", data)
        self.assertIsInstance(data["visible_testcases"], list)

    def test_invalid_language_parameter(self):
        """Test API behavior with invalid/unsupported language"""
        url = reverse("starter_code_api", kwargs={"problem_id": self.problem.id})

        # Test with unsupported language - should still return fallback stub
        response = self.client.get(url, {"language": "nonexistent_lang"})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["language"], "nonexistent_lang")
        self.assertIn("starter_code", data)
        # Should contain fallback stub
        self.assertIn("solve_api_problem", data["starter_code"])

    def test_problem_without_function_metadata(self):
        """Test API with problem that lacks function metadata"""
        # Create problem without function metadata
        problem_no_meta = Problem.objects.create(
            contest=self.contest,
            code="NOMETA",
            title="No Metadata Problem",
            # No function_name, function_params, return_type
        )

        url = reverse("problem_detail_api", kwargs={"problem_id": problem_no_meta.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should use defaults
        self.assertEqual(data["function_name"], "solution")
        self.assertEqual(data["function_params"], [])
        self.assertEqual(data["return_type"], "int")
        self.assertIn("def solution", data["starter_code"])

    def test_get_method_only(self):
        """Test that POST requests are rejected on GET-only endpoints"""
        url = reverse("starter_code_api", kwargs={"problem_id": self.problem.id})

        response = self.client.post(url, {"language": "python"})
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

        data = response.json()
        self.assertIn("error", data)

    def test_api_error_handling(self):
        """Test API error handling and response format"""
        # Test with invalid problem ID format (should be caught by URL routing)
        # This tests the 404 case which we already covered

        # Test database error simulation (hard to simulate without mocking)
        # For now, just verify proper JSON error format
        url = reverse("problem_detail_api", kwargs={"problem_id": 99999})
        response = self.client.get(url)

        # Should be JSON even for errors
        self.assertEqual(response["Content-Type"], "application/json")

    def test_concurrent_requests(self):
        """Test that concurrent requests for different languages work correctly"""
        import threading

        url = reverse("starter_code_api", kwargs={"problem_id": self.problem.id})
        results = {}

        def fetch_starter_code(language):
            response = self.client.get(url, {"language": language})
            results[language] = response.json()

        # Simulate concurrent requests
        threads = []
        languages = ["python", "java", "cpp"]

        for lang in languages:
            thread = threading.Thread(target=fetch_starter_code, args=(lang,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all requests completed successfully
        self.assertEqual(len(results), 3)
        for lang in languages:
            self.assertIn(lang, results)
            self.assertEqual(results[lang]["language"], lang)
            self.assertIn("starter_code", results[lang])

    def test_performance_multiple_languages(self):
        """Test performance of generating stubs for multiple languages"""
        import time

        url = reverse("starter_code_api", kwargs={"problem_id": self.problem.id})
        languages = ["python", "java", "cpp", "csharp", "javascript", "typescript"]

        start_time = time.time()

        for language in languages:
            response = self.client.get(url, {"language": language})
            self.assertEqual(response.status_code, 200)

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete all requests within reasonable time (adjust as needed)
        self.assertLess(total_time, 2.0, "Stub generation took too long")

    def test_response_format_consistency(self):
        """Test that all API responses follow consistent format"""
        # Test problem detail API
        url = reverse("problem_detail_api", kwargs={"problem_id": self.problem.id})
        response = self.client.get(url)
        data = response.json()

        required_fields = [
            "id",
            "code",
            "title",
            "description",
            "difficulty",
            "constraints",
            "function_name",
            "function_params",
            "return_type",
            "starter_code",
            "visible_testcases",
            "is_solved",
        ]

        for field in required_fields:
            self.assertIn(field, data, f"Missing required field: {field}")

        # Test starter code API
        url = reverse("starter_code_api", kwargs={"problem_id": self.problem.id})
        response = self.client.get(url, {"language": "python"})
        data = response.json()

        required_fields = [
            "language",
            "starter_code",
            "function_name",
            "function_params",
        ]

        for field in required_fields:
            self.assertIn(
                field, data, f"Missing required field in starter code API: {field}"
            )


if __name__ == "__main__":
    import unittest

    unittest.main()
