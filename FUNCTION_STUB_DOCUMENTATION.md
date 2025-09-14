# Function Stub (Starter Code) Feature Documentation

## Overview

The Function Stub feature provides automatic generation of language-specific starter code templates for programming problems. This ensures that the submission editor is never blank and helps users get started quickly with the appropriate function signature and boilerplate code.

## Features

- **Multi-language Support**: Python, Java, C++, C#, JavaScript, TypeScript, and fallback
- **Automatic Generation**: Creates appropriate stubs based on problem metadata
- **Custom Overrides**: Maintainers can set custom starter code per language
- **Frontend Integration**: React UI with language switching and stub controls
- **Type-aware**: Proper type conversions and naming conventions per language

## Architecture

### Backend Components

1. **StubGenerator Class** (`accounts/stub_generator.py`)
   - Core logic for generating language-specific starter code
   - Supports function signature analysis and type conversion
   - Handles naming convention conversions (snake_case → camelCase, etc.)

2. **Problem Model Extensions** (`accounts/models.py`)
   - `function_name`: Function name for starter code generation
   - `function_params`: List of parameter names
   - `return_type`: Expected return type
   - `default_stub`: Custom starter code by language (JSON field)

3. **API Endpoints** (`accounts/views.py`)
   - `GET /api/problems/{id}/`: Problem details with starter code
   - `GET /api/problems/{id}/starter-code/`: Standalone starter code endpoint

### Frontend Components

1. **Enhanced Submission Interface** (`frontend/src/main.tsx`)
   - Problem details panel with metadata display
   - Language selector with automatic stub updates
   - Starter code toggle and reset functionality
   - Improved code editor with syntax highlighting hints

2. **API Client** (`frontend/src/api/client.ts`)
   - `getProblemDetail()`: Fetch problem with starter code
   - `getStarterCode()`: Get starter code for specific language

## Usage

### For Students

1. **Automatic Starter Code**: When opening a problem, the editor is pre-filled with appropriate starter code for the selected language.

2. **Language Switching**: Change the language selector to get different starter templates:
   - Python → `def function_name(params): pass`
   - Java → `public class Solution { public static returnType functionName(params) {} }`
   - C++ → `returnType function_name(params) {}`
   - C# → `public class Solution { public ReturnType FunctionName(params) {} }`

3. **Starter Code Controls**:
   - ☑️ **Use starter code template**: Toggle to enable/disable automatic starter code
   - **Reset to Starter Code**: Button to restore original template

### For Maintainers

#### Setting Function Metadata

When creating or editing problems, set these fields for automatic stub generation:

```python
problem = Problem.objects.create(
    title="Two Sum",
    function_name="two_sum",           # snake_case function name
    function_params=["nums", "target"], # list of parameter names
    return_type="List[int]",           # return type hint
    # ... other fields
)
```

#### Custom Starter Code

For problems requiring specific starter templates:

```python
problem.default_stub = {
    "python": '''def two_sum(nums, target):
    """
    Given an array of integers, return indices of two numbers that add up to target.
    """
    # Your solution here
    pass''',
    
    "java": '''public class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Your solution here
        return new int[]{};
    }
}'''
}
problem.save()
```

#### Bulk Population Script

To populate existing problems with starter code metadata:

```bash
cd src/student_auth
python populate_function_stubs.py
```

This script:
- Analyzes existing problem titles for common patterns
- Sets appropriate function names and parameters
- Generates default stubs for all supported languages

## API Reference

### Get Problem Detail with Starter Code

```http
GET /api/problems/{problem_id}/?language={language}
```

**Parameters:**
- `problem_id` (int): Problem ID
- `language` (string, optional): Programming language (default: python)

**Response:**
```json
{
  "id": 1,
  "code": "P1",
  "title": "Two Sum",
  "description": "Find two numbers that add up to target...",
  "difficulty": "Easy",
  "constraints": "1 <= nums.length <= 10^4",
  "function_name": "two_sum",
  "function_params": ["nums", "target"],
  "return_type": "List[int]",
  "starter_code": "def two_sum(nums, target):\n    # Write your code here\n    pass",
  "visible_testcases": [...],
  "is_solved": false
}
```

### Get Starter Code Only

```http
GET /api/problems/{problem_id}/starter-code/?language={language}
```

**Response:**
```json
{
  "language": "python",
  "starter_code": "def two_sum(nums, target):\n    # Write your code here\n    pass",
  "function_name": "two_sum",
  "function_params": ["nums", "target"]
}
```

## Language-Specific Templates

### Python Template
```python
def function_name(param1, param2) -> return_type:
    """
    TODO: Implement this function - Problem Title
    
    Args:
        param1: TODO - describe parameter
        param2: TODO - describe parameter
    
    Returns:
        return_type: TODO - describe return value
    """
    # Write your code here
    pass
```

### Java Template
```java
public class Solution {
    /**
     * TODO: Implement this method - Problem Title
     * 
     * @param param1 TODO - describe parameter
     * @param param2 TODO - describe parameter
     * @return returnType TODO - describe return value
     */
    public static returnType functionName(int param1, int param2) {
        // Write your code here
        return defaultValue;
    }
}
```

### C++ Template
```cpp
#include <iostream>
#include <vector>
#include <string>
using namespace std;

/**
 * TODO: Implement this function - Problem Title
 * 
 * @param param1 TODO - describe parameter
 * @param param2 TODO - describe parameter
 * @return returnType TODO - describe return value
 */
returnType function_name(int param1, int param2) {
    // Write your code here
    return defaultValue;
}
```

## Extension Guide

### Adding New Languages

1. **Add Language Mapping**: Update the `generators` dictionary in `StubGenerator.generate_stub()`:

```python
generators = {
    # ... existing languages
    'rust': StubGenerator._generate_rust_stub,
    'go': StubGenerator._generate_go_stub,
}
```

2. **Implement Language Generator**: Create the generator method:

```python
@staticmethod
def _generate_rust_stub(function_name: str, params: List[str], 
                       return_type: str, title_comment: str) -> str:
    """Generate Rust starter code"""
    rust_return_type = StubGenerator._convert_to_rust_type(return_type)
    param_str = ", ".join([f"{p}: i32" for p in params])  # Default to i32
    
    return f'''fn {function_name}({param_str}) -> {rust_return_type} {{
    // TODO: Implement this function{title_comment}
    // Write your code here
    0 // Replace with actual implementation
}}'''
```

3. **Add Type Conversion**: Implement type mapping for the new language:

```python
@staticmethod
def _convert_to_rust_type(return_type: str) -> str:
    """Convert generic return type to Rust type"""
    type_map = {
        'int': 'i32',
        'string': 'String',
        'bool': 'bool',
        'list': 'Vec<i32>',
        # ... more mappings
    }
    return type_map.get(return_type.lower(), 'i32')
```

4. **Update Frontend**: Add the new language to the language selector in `main.tsx`:

```tsx
<option value="rust">Rust</option>
<option value="go">Go</option>
```

### Custom Stub Templates

For problems requiring specialized templates, use the `default_stub` field:

```python
# Complex template with imports and helper functions
problem.default_stub = {
    "python": '''import sys
from typing import List, Dict, Set

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def solve_tree_problem(root: TreeNode) -> int:
    """
    Solve the binary tree problem.
    """
    # Your solution here
    pass'''
}
```

## Testing

### Running Tests

```bash
# Run stub generator unit tests
python test_stub_generator.py

# Run API integration tests  
python test_api_integration.py

# Run all tests
python manage.py test accounts
```

### Test Coverage

- **Unit Tests**: Function signature parsing, type conversion, language-specific generation
- **Integration Tests**: API endpoints, database interactions, error handling
- **Performance Tests**: Concurrent requests, bulk generation timing

## Database Migration

The feature requires a database migration to add new fields to the Problem model:

```bash
# Apply migration
python manage.py migrate accounts 0002_add_function_stub_fields

# Populate existing problems
python populate_function_stubs.py
```

## Troubleshooting

### Common Issues

1. **Missing Starter Code**: Check that problem has `function_name` set
2. **Wrong Function Name**: Verify language-specific naming conventions are applied
3. **API Errors**: Ensure migration has been applied and problem exists

### Debug Mode

Enable debug logging to trace stub generation:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Debug stub generation
from accounts.stub_generator import generate_starter_code
stub = generate_starter_code("python", problem)
print(stub)
```

## Performance Considerations

- **Caching**: Consider caching generated stubs for frequently accessed problems
- **Lazy Loading**: Stubs are generated on-demand, not pre-computed
- **Database Impact**: JSON fields are efficient for storing custom stubs

## Security Considerations

- **Input Validation**: All user inputs are validated before stub generation
- **XSS Prevention**: Generated code is properly escaped in frontend
- **Rate Limiting**: Consider rate limiting on stub generation endpoints

## Future Enhancements

1. **Monaco Editor Integration**: Rich code editor with syntax highlighting
2. **Template Marketplace**: Community-contributed starter templates
3. **AI-Generated Stubs**: Use AI to generate more contextual starter code
4. **Language-Specific Imports**: Automatic import statements based on problem type
5. **Interactive Examples**: Inline examples within starter code comments

---

## Maintenance Checklist

- [ ] Regular review of language support and templates
- [ ] Monitor API performance and response times  
- [ ] Update type mappings for new language versions
- [ ] Review and update documentation
- [ ] Test new language additions thoroughly
- [ ] Backup custom stub data before major updates