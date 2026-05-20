import httpx

import pytest
from openai import APIError

from integrations.openai.client import OPEN_AI_API_ERROR_MSG, OpenAIClient
from integrations.openai.exceptions import OpenAIClientException

pytestmark = pytest.mark.django_db


class TestOpenAIClientGetSaasIdeas:
    def test_success(self, mocker, openai_completion_mock):
        message = mocker.Mock(content="- Fitness planner\n- AI meal coach\n3. Smart order upsell assistant")
        response = mocker.Mock(choices=[mocker.Mock(message=message)])
        openai_completion_mock.create.return_value = response
        keywords = ["fitness", "ai"]

        result = OpenAIClient.get_saas_ideas(keywords)

        openai_completion_mock.create.assert_called_once_with(
            **{
                "max_tokens": 200,
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that generates SaaS ideas."},
                    {
                        "role": "user",
                        "content": "Get me 3-5 fitness, ai saas ideas. Return them as a simple bulleted list.",
                    },
                ],
                "temperature": 0.7,
            }
        )
        assert result.ideas == ["Fitness planner", "AI meal coach", "Smart order upsell assistant"]

    def test_api_exception(self, openai_completion_mock):
        openai_completion_mock.create.side_effect = APIError(
            "The server had an error while processing your request.",
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
            body=None,
        )

        with pytest.raises(OpenAIClientException) as error:
            OpenAIClient.get_saas_ideas(["idea"])

        assert str(error.value) == OPEN_AI_API_ERROR_MSG
