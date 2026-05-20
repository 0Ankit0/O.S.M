import pytest

from ..openai import client


@pytest.fixture
def openai_completion_mock(mocker):
    openai_client = mocker.patch.object(client, "OpenAI", autospec=True)
    return openai_client.return_value.chat.completions


@pytest.fixture
def openai_client_mock(mocker):
    return mocker.patch.object(client, "OpenAIClient", autospec=True)
