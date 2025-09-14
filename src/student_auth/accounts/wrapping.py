import os
import re
from django.conf import settings


def _template_path(problem, language: str) -> str | None:
    ext = "py" if language == "python" else ("cpp" if language == "cpp" else None)
    if not ext:
        return None
    # Templates are stored under MEDIA_ROOT/testcases/<contest>/<problem>/solution.<ext>
    base = os.path.join(
        getattr(settings, "MEDIA_ROOT", ""),
        "testcases",
        str(getattr(problem.contest, "name", "") or "").strip(),
        str(problem.code).strip(),
    )
    path = os.path.join(base, f"solution.{ext}")
    return path if os.path.exists(path) else None


def _wrap_python(user_code: str, template: str) -> str:
    # Try to find user's class Solution ... block
    m = re.search(r"class\s+Solution\b.*?(?=\n# --- Input/Output Handling ---|\Z)", user_code, re.DOTALL)
    if not m:
        # Safe fallback: do not alter behavior if we cannot identify a Solution block
        return user_code
    user_block = m.group(0)
    # Replace the template's Solution block with user's
    wrapped, n = re.subn(
        r"class\s+Solution\b.*?(?=\n# --- Input/Output Handling ---|\Z)",
        user_block,
        template,
        flags=re.DOTALL,
    )
    # If replacement didn't happen, keep original user code to avoid breaking
    return wrapped if n > 0 else user_code


def _wrap_cpp(user_code: str, template: str) -> str:
    m = re.search(r"class\s+Solution\s*\{.*?\};", user_code, re.DOTALL)
    if not m:
        return user_code
    user_block = m.group(0)
    wrapped, n = re.subn(r"class\s+Solution\s*\{.*?\};", user_block, template, flags=re.DOTALL)
    return wrapped if n > 0 else user_code


def maybe_wrap_code(problem, language: str, user_code: str) -> str:
    """
    Attempt to inject user's partial code into the problem template.
    If template is missing or patterns don't match, return original code.
    """
    path = _template_path(problem, language)
    if not path:
        return user_code
    try:
        with open(path, "r", encoding="utf-8") as f:
            template = f.read()
    except Exception:
        return user_code

    if language == "python":
        return _wrap_python(user_code, template)
    if language == "cpp":
        return _wrap_cpp(user_code, template)
    return user_code
