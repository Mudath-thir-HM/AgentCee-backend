import httpx

from app.core.config import (
    settings
)


class OpenRouterClient:

    BASE_URL = (
        "https://openrouter.ai/api/v1"
    )

    async def chat_completion(
        self,
        prompt: str,
        model: str
    ):
        async with (
            httpx.AsyncClient()
            as client
        ):
            try:
                response = await (
                    client.post(
                        f"{self.BASE_URL}/chat/completions",
                        headers={
                            "Authorization":
                            f"Bearer {settings.OPENROUTER_API_KEY}",
                            "Content-Type":
                            "application/json",
                            "HTTP-Referer": "http://localhost:8000",
                            "X-Title": "Agentic Marketing API"
                        },
                        json={
                            "model":
                            model,
                            "messages": [
                                {
                                    "role":
                                    "user",
                                    "content":
                                    prompt
                                }
                            ]
                        },
                        timeout=60
                    )
                )
                
                if response.status_code == 429:
                    raise Exception(
                        "Model temporarily rate limited"
                    )

                if response.status_code != 200:
                    print(
                        "OpenRouter Response:",
                        response.status_code,
                        response.text
                    )

                    raise Exception(
                        f"OpenRouter failed: {response.text}"
                    )

                data = (
                    response.json()
                )

                return (
                    data["choices"][0]
                    ["message"]
                    ["content"]
                )
            except Exception as e:
                print(f"Chat completion error: {str(e)}")
                print(f"Model: {model}")
                print(f"API Key: {settings.OPENROUTER_API_KEY[:20]}...")
                raise

    async def ask_deepseek(
        self,
        prompt: str
    ):
        return await (
            self.chat_completion(
                prompt=prompt,
                model=(
                    settings
                    .DEEPSEEK_MODEL
                )
            )
        )

    async def ask_gemma(
        self,
        prompt: str
    ):
        return await (
            self.chat_completion(
                prompt=prompt,
                model=(
                    settings
                    .GEMMA_MODEL
                )
            )
        )


openrouter_client = (
    OpenRouterClient()
)


async def ask_openrouter(
    prompt: str,
    model: str = None
):
    models = [
        model or settings.DEEPSEEK_MODEL,
        settings.GEMMA_MODEL,
        "meta-llama/llama-3.3-70b-instruct:free",
        "qwen/qwen3-32b:free"
    ]

    last_error = None

    for model_name in models:
        try:
            print(f"Trying model: {model_name}")

            return await (
                openrouter_client.chat_completion(
                    prompt=prompt,
                    model=model_name
                )
            )

        except Exception as e:
            print(
                f"Model failed: "
                f"{model_name} -> {str(e)}"
            )

            last_error = e
            continue

    raise Exception(
        f"All models failed: {str(last_error)}"
    )