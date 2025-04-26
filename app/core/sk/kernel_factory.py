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
        self._model     = os.getenv("GITHUB_MODEL", "openai/gpt-4o")

    def get_kernel(self) -> sk.Kernel:
        if self._kernel is None:
            self._kernel = self._build_kernel()
        return self._kernel

    def _build_kernel(self) -> sk.Kernel:
        k = sk.Kernel()                                    # still valid; builder is optional
        deployment = self._model.split("/")[-1]
        svc = AzureChatCompletion(                         # new class
            service_id="github",
            deployment_name=deployment,
            endpoint=self._endpoint,
            api_key=self._api_key,
        )
        k.add_service(svc)
        print(f"Semantic Kernel initialised with: {deployment}")
        return k

_kernel_factory = KernelFactory()
def get_kernel() -> sk.Kernel: return _kernel_factory.get_kernel()