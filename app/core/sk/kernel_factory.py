# app/core/sk/kernel_factory.py
import os
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
# load the environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

class KernelFactory:
    def __init__(self) -> None:
        self._kernel: sk.Kernel | None = None
        self._api_key   = os.getenv("GITHUB_TOKEN")
        self._endpoint  = os.getenv("ENDPOINT", "https://models.inference.ai.azure.com")
        # Get model name and ensure it doesn't have the "openai/" prefix for SK 1.28.1 compatibility
        model_env = os.getenv("GITHUB_MODEL", "openai/gpt-4o")
        self._model = model_env.split("/")[-1] if "/" in model_env else model_env

    def get_kernel(self) -> sk.Kernel:
        if self._kernel is None:
            self._kernel = self._build_kernel()
        return self._kernel

    def _build_kernel(self) -> sk.Kernel:
        k = sk.Kernel()                                    # still valid; builder is optional
        svc = AzureChatCompletion(                         # new class
            service_id="github",
            deployment_name=self._model,  # Already cleaned up in __init__
            endpoint=self._endpoint,
            api_key=self._api_key,
        )
        k.add_service(svc)
        print(f"Semantic Kernel initialised with: {self._model}")
        return k

_kernel_factory = KernelFactory()
def get_kernel() -> sk.Kernel: return _kernel_factory.get_kernel()