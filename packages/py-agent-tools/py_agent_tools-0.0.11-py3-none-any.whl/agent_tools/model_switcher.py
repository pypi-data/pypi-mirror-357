from collections import defaultdict

from pydantic import BaseModel

from agent_tools.agent_base import ModelNameBase
from agent_tools.ark_agent import ArkAgent, ArkCredentialPool, ArkModelName
from agent_tools.azure_agent import AzureAgent, AzureCredentialPool, AzureModelName
from agent_tools.bailian_agent import BailianAgent, BailianCredentialPool, BailianModelName
from agent_tools.credential_pool_base import CredentialPoolBase, RemoteCredentialPool
from agent_tools.openai_agent import OpenAIAgent, OpenAICredentialPool, OpenAIModelName
from agent_tools.settings import ModelProvider
from agent_tools.vertex_agent import VertexAgent, VertexCredentialPool, VertexModelName


class ProviderMapping(BaseModel):
    provider: str
    agent: type
    local_credential_pool: type
    model_name_enum: type[ModelNameBase]


class ModelSwitcher:
    def __init__(self, allowed_providers: list[str], using_remote_credential_pools: bool = False):
        self.using_remote_credential_pools = using_remote_credential_pools
        self.allowed_providers = allowed_providers
        self._credential_pools: defaultdict[
            str, dict[str, CredentialPoolBase | RemoteCredentialPool]
        ] = defaultdict(dict)

    @property
    def _provider_mapping(self) -> dict[str, ProviderMapping]:
        return {
            'ark': ProviderMapping(
                provider='ark',
                agent=ArkAgent,
                local_credential_pool=ArkCredentialPool,
                model_name_enum=ArkModelName,
            ),
            'azure': ProviderMapping(
                provider='azure',
                agent=AzureAgent,
                local_credential_pool=AzureCredentialPool,
                model_name_enum=AzureModelName,
            ),
            'bailian': ProviderMapping(
                provider='bailian',
                agent=BailianAgent,
                local_credential_pool=BailianCredentialPool,
                model_name_enum=BailianModelName,
            ),
            'openai': ProviderMapping(
                provider='openai',
                agent=OpenAIAgent,
                local_credential_pool=OpenAICredentialPool,
                model_name_enum=OpenAIModelName,
            ),
            'vertex': ProviderMapping(
                provider='vertex',
                agent=VertexAgent,
                local_credential_pool=VertexCredentialPool,
                model_name_enum=VertexModelName,
            ),
        }

    def get_credential_pool(
        self, provider: str, model_name: str
    ) -> CredentialPoolBase | RemoteCredentialPool:
        """Get credential pool for a specific model."""
        if provider not in self._credential_pools:
            raise ValueError(f"Provider '{provider}' not found")
        if model_name not in self._credential_pools[provider]:
            raise ValueError(f"Model '{model_name}' not found for provider '{provider}'")
        return self._credential_pools[provider][model_name]

    async def start_all_pools(self):
        """Start all credential pools for health checking."""
        for provider, mapping in self._provider_mapping.items():
            for model_name in mapping.model_name_enum:
                if self.using_remote_credential_pools:
                    raise NotImplementedError("Remote credential pools are not implemented yet")
                else:
                    pool = mapping.local_credential_pool(target_model=model_name)
                    await pool.start()
                    self._credential_pools[provider][model_name.value] = pool

    def stop_all_pools(self):
        """Stop all credential pools."""
        for provider, pools in self._credential_pools.items():
            for pool in pools.values():
                if isinstance(pool, RemoteCredentialPool):
                    continue
                pool.stop()


if __name__ == "__main__":
    import asyncio

    async def test_model_switcher():
        """Test the ModelSwitcher functionality."""
        allowed_providers = [provider.value for provider in ModelProvider]
        switcher = ModelSwitcher(allowed_providers=allowed_providers)
        await switcher.start_all_pools()
        switcher.stop_all_pools()

    try:
        asyncio.run(test_model_switcher())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print("Tests completed successfully (cleanup warning ignored)")
        else:
            raise
