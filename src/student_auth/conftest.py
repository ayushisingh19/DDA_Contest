import pytest

# Allow database access for all tests in this package for smoother DX
pytestmark = pytest.mark.django_db
