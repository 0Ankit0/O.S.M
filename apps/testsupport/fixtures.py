import pytest
import pytest_factoryboy
from rest_framework.test import APIClient

from .factories import UserFactory

pytest_factoryboy.register(UserFactory)


@pytest.fixture
def graphene_client():
    return APIClient()
