# test_sk_kernel.py
import os
import sys
# Add the project root to sys.path to allow 'app' imports regardless of how the test is run
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
# test_sk_kernel.py
import asyncio
from app.core.sk.kernel_factory import get_kernel
from semantic_kernel.functions.kernel_arguments import KernelArguments

# test_sk_kernel.py  (fixed)
import asyncio
from app.core.sk.kernel_factory import get_kernel
from semantic_kernel.functions.kernel_arguments import KernelArguments

async def smoke():
    kernel = get_kernel()

    response = await kernel.invoke_prompt(        # <-- new name
        prompt="Answer in one sentence: What is Semantic Kernel?",
        arguments=KernelArguments(),
        service_id="github"   # optional; omit if you have a default service
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(smoke())