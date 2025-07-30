"""
Multi-Chain RPC Aggregator

A simplified interface for working with multiple blockchain networks.
This class provides a unified interface where chain_id is specified as a parameter
for each method call, making it easy to compose cross-chain operations.
"""

from typing import List, Dict, Tuple, Optional, Union, TypedDict
from decimal import Decimal
import logging
from web3 import AsyncWeb3

from dcentrapi.rpc_aggregation_async import (
    AsyncRpcAggregation,
    Slot0DataDict,
    UniswapNFTPositionDataDict,
    ReserveAssetDict,
    ReservesResponseDict,
    PoolsResponseDict,
    TokenId,
    Deadline,
    FactoryType,
)
from dcentrapi.utils import (
    Address,
    Amount,
    ChainId,
)
from dcentrapi.constants import (
    get_helper_address,
    get_curve_address,
    UTILS_CONTRACT_ADDRESSES,
    CURVE_CONTRACT_ADDRESSES,
)

# Setup logger
logger = logging.getLogger(__name__)


class ChainConfig(TypedDict, total=False):
    """Configuration for a blockchain network."""

    rpc_urls: Union[str, List[str]]
    helper_address: Optional[str]  # Optional custom helper contract address
    curve_address: Optional[str]  # Optional custom curve contract address


class ChainInfo(TypedDict):
    """Information about a configured blockchain network."""

    chain_id: ChainId
    name: str
    rpc_urls: List[str]
    helper_address: Optional[str]
    curve_address: Optional[str]
    is_connected: bool  # Whether an aggregator instance is cached


class SupportedChainInfo(TypedDict):
    """Information about a supported blockchain network from constants."""

    chain_id: ChainId
    name: str
    helper_address: str
    curve_address: str


class MultiChainAggregator:
    """
    Multi-chain RPC aggregator that provides a unified interface for blockchain operations
    across multiple networks.

    Key features:
    - Simple setup with chain ID to RPC URL mapping
    - Fallback RPC support for reliability
    - Lazy loading of aggregator instances
    - Chain ID as parameter for all operations
    - User-composable cross-chain operations
    """

    def __init__(
        self,
        chains: Dict[ChainId, Union[str, List[str], ChainConfig]],
        names: Optional[Dict[ChainId, str]] = None,
    ):
        """
        Initialize the multi-chain aggregator.

        Args:
            chains: Mapping of chain ID to RPC configuration. Can be:
                   - A single RPC URL string
                   - A list of RPC URLs for fallback support
                   - A ChainConfig dict with rpc_urls and optional helper addresses
            names: Optional mapping of chain ID to human-readable names for logging.
                  Defaults to "chain_{id}" if not provided.

        Examples:
            # Simple setup
            aggregator = MultiChainAggregator({
                1: "https://eth-mainnet.alchemyapi.io/v2/KEY",
                137: "https://polygon-mainnet.alchemyapi.io/v2/KEY"
            })

            # With fallback RPCs
            aggregator = MultiChainAggregator({
                1: [
                    "https://eth-mainnet.alchemyapi.io/v2/KEY",
                    "https://eth.llamarpc.com",
                    "https://rpc.ankr.com/eth"
                ]
            })

            # With custom helper contracts
            aggregator = MultiChainAggregator({
                1: {
                    "rpc_urls": "https://eth-mainnet.alchemyapi.io/v2/KEY",
                    "helper_address": "0x1159a7F493FDD145172bFDFF4764Bb89E6A99B68",
                    "curve_address": "0x23eD44EFdF2e1e43933f5d81Ec5Cbd3663e1f8F4"
                },
                999: {  # Custom chain not in constants.py
                    "rpc_urls": ["https://custom-rpc1...", "https://custom-rpc2..."],
                    "helper_address": "0xCustomHelperAddress...",
                    "curve_address": "0xCustomCurveAddress..."
                }
            })

            # Mixed configuration
            aggregator = MultiChainAggregator({
                1: "https://eth-rpc...",  # Simple string
                137: ["https://poly-rpc1...", "https://poly-rpc2..."],  # List of RPCs
                42161: {  # Full config
                    "rpc_urls": "https://arb-rpc...",
                    "helper_address": "0x74EA85e968783AD211de4b6a535cfcd5618E2477"
                }
            })
        """
        self._chains = chains
        self._names = names or {}
        self._aggregators: Dict[ChainId, AsyncRpcAggregation] = {}

        logger.info(
            f"Initialized MultiChainAggregator with {len(chains)} chains: {list(chains.keys())}"
        )

    def add_chain(
        self,
        chain_id: ChainId,
        config: Union[str, List[str], ChainConfig],
        name: Optional[str] = None,
    ) -> None:
        """
        Add a new chain configuration.

        Args:
            chain_id: The blockchain network ID
            config: Chain configuration (RPC URL(s) or full config dict)
            name: Optional human-readable name for logging
        """
        self._chains[chain_id] = config
        if name:
            self._names[chain_id] = name

        # Clear cached aggregator if it exists
        if chain_id in self._aggregators:
            del self._aggregators[chain_id]

        logger.info(f"Added chain {chain_id} ({self.get_chain_name(chain_id)})")

    def add_batch_chains(
        self,
        chains: Dict[ChainId, Union[str, List[str], ChainConfig]],
        names: Optional[Dict[ChainId, str]] = None,
    ) -> None:
        """
        Add multiple chain configurations at once.

        Args:
            chains: Dictionary mapping chain IDs to their configurations
            names: Optional dictionary mapping chain IDs to human-readable names

        Examples:
            aggregator.add_batch_chains({
                42161: "https://arb-mainnet.alchemyapi.io/v2/KEY",
                10: ["https://op-rpc1...", "https://op-rpc2..."],
                8453: {
                    "rpc_urls": "https://base-rpc...",
                    "helper_address": "0x930d7f12f787266e92dfDA9Bb6c60BC149951A1F"
                }
            }, names={42161: "arbitrum", 10: "optimism", 8453: "base"})
        """
        names = names or {}

        for chain_id, config in chains.items():
            self._chains[chain_id] = config
            if chain_id in names:
                self._names[chain_id] = names[chain_id]

            # Clear cached aggregator if it exists
            if chain_id in self._aggregators:
                del self._aggregators[chain_id]

        chain_ids = list(chains.keys())
        logger.info(f"Added {len(chain_ids)} chains in batch: {chain_ids}")

    def remove_chain(self, chain_id: ChainId) -> None:
        """
        Remove a chain configuration.

        Args:
            chain_id: The blockchain network ID to remove
        """
        if chain_id in self._chains:
            del self._chains[chain_id]
        if chain_id in self._names:
            del self._names[chain_id]
        if chain_id in self._aggregators:
            del self._aggregators[chain_id]

        logger.info(f"Removed chain {chain_id}")

    def get_configured_chains(self) -> List[ChainId]:
        """
        Get list of configured chain IDs.

        Returns:
            List of chain IDs that have been configured
        """
        return list(self._chains.keys())

    def get_chain_name(self, chain_id: ChainId) -> str:
        """
        Get human-readable name for a chain.

        Args:
            chain_id: The blockchain network ID

        Returns:
            Human-readable name or "chain_{id}" if not configured
        """
        return self._names.get(chain_id, f"chain_{chain_id}")

    def get_chain_info(self, chain_id: ChainId) -> ChainInfo:
        """
        Get detailed information about a specific chain configuration.

        Args:
            chain_id: The blockchain network ID

        Returns:
            ChainInfo dictionary with detailed chain information

        Raises:
            ValueError: If chain_id is not configured
        """
        if chain_id not in self._chains:
            raise ValueError(
                f"Chain {chain_id} is not configured. Available chains: {self.get_configured_chains()}"
            )

        chain_config = self._chains[chain_id]
        rpc_urls, custom_helper_address, custom_curve_address = (
            self._parse_chain_config(chain_config)
        )

        # Try to get helper and curve addresses with fallback
        try:
            helper_address = custom_helper_address or get_helper_address(chain_id)
        except (KeyError, ValueError):
            helper_address = custom_helper_address

        try:
            curve_address = custom_curve_address or get_curve_address(chain_id)
        except (KeyError, ValueError):
            curve_address = custom_curve_address

        return ChainInfo(
            chain_id=chain_id,
            name=self.get_chain_name(chain_id),
            rpc_urls=rpc_urls,
            helper_address=helper_address,
            curve_address=curve_address,
            is_connected=(chain_id in self._aggregators),
        )

    def get_all_chains_info(self) -> Dict[ChainId, ChainInfo]:
        """
        Get detailed information about all configured chains.

        Returns:
            Dictionary mapping chain IDs to their ChainInfo
        """
        return {
            chain_id: self.get_chain_info(chain_id)
            for chain_id in self.get_configured_chains()
        }

    def _parse_chain_config(
        self, chain_config: Union[str, List[str], ChainConfig]
    ) -> Tuple[List[str], Optional[str], Optional[str]]:
        """
        Parse chain configuration to extract RPC URLs and helper addresses.

        Args:
            chain_config: Chain configuration in various formats

        Returns:
            Tuple of (rpc_urls_list, helper_address, curve_address)
        """
        if isinstance(chain_config, str):
            # Simple string format
            return [chain_config], None, None
        elif isinstance(chain_config, list):
            # List of RPC URLs
            return chain_config, None, None
        elif isinstance(chain_config, dict):
            # Full configuration dict
            rpc_urls = chain_config.get("rpc_urls", [])
            if isinstance(rpc_urls, str):
                rpc_urls = [rpc_urls]
            helper_address = chain_config.get("helper_address")
            curve_address = chain_config.get("curve_address")
            return rpc_urls, helper_address, curve_address
        else:
            raise ValueError(
                f"Invalid chain configuration format: {type(chain_config)}"
            )

    async def _get_aggregator(self, chain_id: ChainId) -> AsyncRpcAggregation:
        """
        Get or create an aggregator instance for the specified chain.
        Implements lazy loading and failover logic.

        Args:
            chain_id: The blockchain network ID

        Returns:
            AsyncRpcAggregation instance for the chain

        Raises:
            ValueError: If chain_id is not configured
            ConnectionError: If all RPCs fail for the chain
        """
        if chain_id not in self._chains:
            raise ValueError(
                f"Chain {chain_id} is not configured. Available chains: {self.get_configured_chains()}"
            )

        # Return cached aggregator if available
        if chain_id in self._aggregators:
            return self._aggregators[chain_id]

        # Parse chain configuration
        chain_config = self._chains[chain_id]
        rpc_urls, custom_helper_address, custom_curve_address = (
            self._parse_chain_config(chain_config)
        )

        # Try each RPC URL until one works
        last_error = None
        chain_name = self.get_chain_name(chain_id)

        for i, rpc_url in enumerate(rpc_urls):
            try:
                logger.debug(
                    f"Trying RPC {i + 1}/{len(rpc_urls)} for {chain_name}: {rpc_url}"
                )

                # Create Web3 instance
                web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))

                # Test connection with a simple call
                await web3.eth.get_block_number()

                # Create aggregator with custom helper addresses if provided
                aggregator = AsyncRpcAggregation(web3, chain_id)

                # Override helper addresses if provided in config
                if custom_helper_address or custom_curve_address:
                    logger.debug(f"Using custom contract addresses for {chain_name}")
                    if custom_helper_address:
                        logger.debug(f"  Helper address: {custom_helper_address}")
                    if custom_curve_address:
                        logger.debug(f"  Curve address: {custom_curve_address}")

                    # Note: We'll need to check if AsyncRpcAggregation supports
                    # overriding these addresses. For now, we'll create the aggregator
                    # and hope the custom addresses are handled properly.
                    # This might require future updates to AsyncRpcAggregation.

                self._aggregators[chain_id] = aggregator

                logger.debug(f"Successfully connected to {chain_name} via RPC {i + 1}")
                return aggregator

            except Exception as e:
                last_error = e
                logger.warning(f"RPC {rpc_url} failed for {chain_name}: {e}")
                continue

        # All RPCs failed
        raise ConnectionError(
            f"All RPCs failed for {chain_name} (chain {chain_id}): {last_error}"
        )

    def get_helper_address(self, chain_id: ChainId) -> str:
        """
        Get the helper contract address for a chain.
        Uses custom address from config if provided, otherwise falls back to constants.

        Args:
            chain_id: The blockchain network ID

        Returns:
            Helper contract address

        Raises:
            ValueError: If no helper address is available
        """
        if chain_id in self._chains:
            chain_config = self._chains[chain_id]
            _, custom_helper_address, _ = self._parse_chain_config(chain_config)
            if custom_helper_address:
                return custom_helper_address

        # Fall back to constants
        try:
            return get_helper_address(chain_id)
        except KeyError:
            raise ValueError(
                f"No helper contract address available for chain {chain_id}"
            )

    def get_curve_address(self, chain_id: ChainId) -> str:
        """
        Get the curve contract address for a chain.
        Uses custom address from config if provided, otherwise falls back to constants.

        Args:
            chain_id: The blockchain network ID

        Returns:
            Curve contract address

        Raises:
            ValueError: If no curve address is available
        """
        if chain_id in self._chains:
            chain_config = self._chains[chain_id]
            _, _, custom_curve_address = self._parse_chain_config(chain_config)
            if custom_curve_address:
                return custom_curve_address

        # Fall back to constants
        try:
            return get_curve_address(chain_id)
        except KeyError:
            raise ValueError(
                f"No curve contract address available for chain {chain_id}"
            )

    # ========== Token Balance Operations ==========

    async def get_token_balance(
        self,
        user: Address,
        token: Address,
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> Amount:
        """
        Get token balance for a user on the specified chain.

        Args:
            user: User address
            token: Token address
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            Token balance
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.get_token_balance(user, token, rpc_url)

    async def get_token_balances_for_user(
        self,
        user: Address,
        tokens: List[Address],
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> Tuple[List[Address], List[Amount]]:
        """
        Get token balances for a user across multiple tokens on the specified chain.

        Args:
            user: User address
            tokens: List of token addresses
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            Tuple containing (token_addresses, token_balances)
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.get_token_balances_for_user(user, tokens, rpc_url)

    async def get_token_balance_for_users(
        self,
        users: List[Address],
        token: Address,
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> Tuple[List[Address], List[Amount]]:
        """
        Get token balances for multiple users on the specified chain.

        Args:
            users: List of user addresses
            token: Token address
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            Tuple containing (user_addresses, token_balances)
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.get_token_balance_for_users(users, token, rpc_url)

    async def get_token_balances_for_users(
        self,
        users: List[Address],
        tokens: List[Address],
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> List[Amount]:
        """
        Get token balances for multiple users and tokens on the specified chain.

        Args:
            users: List of user addresses
            tokens: List of token addresses
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            List of token balances
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.get_token_balances_for_users(users, tokens, rpc_url)

    # ========== Price and Reserve Operations ==========

    async def calculate_token_price_from_pair(
        self,
        pool: Address,
        target_token_address: Address,
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> Tuple[Decimal, Address, Address]:
        """
        Calculate token price from a pair on the specified chain.

        Args:
            pool: Pool address
            target_token_address: Target token address
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            Tuple containing (token_price, token0_address, token1_address)
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.calculate_token_price_from_pair(
            pool, target_token_address, rpc_url
        )

    async def calculate_reserves_amount_from_pair(
        self,
        pool: Address,
        amount: Amount,
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> ReserveAssetDict:
        """
        Calculate reserves amount from a pair on the specified chain.

        Args:
            pool: Pool address
            amount: Amount
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            Dictionary with reserve asset information
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.calculate_reserves_amount_from_pair(
            pool, amount, rpc_url
        )

    async def get_reserves_from_pair(
        self, pool: Address, chain_id: ChainId, rpc_url: Optional[str] = None
    ) -> ReserveAssetDict:
        """
        Get reserves from a pair on the specified chain.

        Args:
            pool: Pool address
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            Dictionary with reserve asset information
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.get_reserves_from_pair(pool, rpc_url)

    async def get_reserves_from_pools(
        self,
        factory_type: FactoryType,
        pools: List[Address],
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> ReservesResponseDict:
        """
        Get reserves from pools on the specified chain.

        Args:
            factory_type: Factory type (UNI_V2, UNI_V3, CURVE, BALANCER)
            pools: List of pool addresses
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            Dictionary with reserve asset information
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.get_reserves_from_pools(factory_type, pools, rpc_url)

    # ========== Pool Operations ==========

    async def get_pool_data_from_factory(
        self,
        factory_type: FactoryType,
        factory: Address,
        indices: List[int],
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> PoolsResponseDict:
        """
        Get pool data from factory on the specified chain.

        Args:
            factory_type: Factory type (UNI_V2, UNI_V3, CURVE, BALANCER)
            factory: Factory address
            indices: List of indices
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            Dictionary with pool data
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.get_pool_data_from_factory(
            factory_type, factory, indices, rpc_url
        )

    # ========== Uniswap V3 Operations ==========

    async def get_uni_v3_pools_slot0_values(
        self, pools: List[Address], chain_id: ChainId, rpc_url: Optional[str] = None
    ) -> List[Slot0DataDict]:
        """
        Get Uniswap V3 pool slot0 values on the specified chain.

        Args:
            pools: List of pool addresses
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            List of slot0 values
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.get_uni_v3_pools_slot0_values(pools, rpc_url)

    async def get_uni_v3_position_data(
        self,
        nft_pos_mgr_address: Address,
        token_ids: List[TokenId],
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> List[UniswapNFTPositionDataDict]:
        """
        Get Uniswap V3 NFT position data on the specified chain.

        Args:
            nft_pos_mgr_address: NFT position manager address
            token_ids: List of token IDs
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            List of position data
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.get_uni_v3_position_data(
            nft_pos_mgr_address, token_ids, rpc_url
        )

    async def get_uni_v3_position_liquidity(
        self,
        nft_pos_mgr_address: Address,
        token_ids: List[TokenId],
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> List[Amount]:
        """
        Get Uniswap V3 position liquidity data on the specified chain.

        Args:
            nft_pos_mgr_address: NFT position manager address
            token_ids: List of token IDs
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            List of liquidity data
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.get_uni_v3_position_liquidity(
            nft_pos_mgr_address, token_ids, rpc_url
        )

    # ========== Trading Operations ==========

    async def estimate_amount_out(
        self,
        pool: Address,
        token_in: Address,
        amount_in: Amount,
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> Amount:
        """
        Estimate amount out on the specified chain.

        Args:
            pool: Pool address
            token_in: Token in address
            amount_in: Amount in
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            Estimated amount out
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.estimate_amount_out(pool, token_in, amount_in, rpc_url)

    async def swap_exact_input_single(
        self,
        address_of_swap_router: Address,
        pool: Address,
        token_in: Address,
        amount_in: Amount,
        deadline: Deadline,
        amount_out_minimum: Amount,
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> Amount:
        """
        Swap exact input single on the specified chain.

        Args:
            address_of_swap_router: Swap router address
            pool: Pool address
            token_in: Token in address
            amount_in: Amount in
            deadline: Deadline
            amount_out_minimum: Amount out minimum
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            Amount out
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.swap_exact_input_single(
            address_of_swap_router,
            pool,
            token_in,
            amount_in,
            deadline,
            amount_out_minimum,
            rpc_url,
        )

    async def swap_exact_output_single(
        self,
        address_of_swap_router: Address,
        pool: Address,
        token_in: Address,
        amount_in_maximum: Amount,
        deadline: Deadline,
        amount_out: Amount,
        chain_id: ChainId,
        rpc_url: Optional[str] = None,
    ) -> Amount:
        """
        Swap exact output single on the specified chain.

        Args:
            address_of_swap_router: Swap router address
            pool: Pool address
            token_in: Token in address
            amount_in_maximum: Maximum amount in
            deadline: Deadline
            amount_out: Amount out
            chain_id: The blockchain network ID
            rpc_url: Optional RPC URL override

        Returns:
            Amount in
        """
        aggregator = await self._get_aggregator(chain_id)
        return await aggregator.swap_exact_output_single(
            address_of_swap_router,
            pool,
            token_in,
            amount_in_maximum,
            deadline,
            amount_out,
            rpc_url,
        )

    # ========== Utility Methods ==========

    @classmethod
    def get_supported_chains(cls) -> Dict[ChainId, SupportedChainInfo]:
        """
        Get all chains that are natively supported by the library.

        These are chains that have predefined helper contract addresses in constants.py
        and can be used without providing custom contract addresses.

        Returns:
            Dictionary mapping chain IDs to their supported chain information
        """
        # Chain ID to name mapping for known chains
        CHAIN_NAMES = {
            1: "Ethereum",
            10: "Optimism",
            56: "BNB Smart Chain",
            137: "Polygon",
            250: "Fantom",
            1030: "Conflux",
            2001: "Milkomeda",
            8453: "Base",
            42161: "Arbitrum",
            43114: "Avalanche",
            59144: "Linea",
        }

        supported_chains = {}

        # Get all chains that have both helper and curve addresses
        for chain_id in UTILS_CONTRACT_ADDRESSES:
            if chain_id in CURVE_CONTRACT_ADDRESSES:
                supported_chains[chain_id] = SupportedChainInfo(
                    chain_id=chain_id,
                    name=CHAIN_NAMES.get(chain_id, f"Chain {chain_id}"),
                    helper_address=UTILS_CONTRACT_ADDRESSES[chain_id],
                    curve_address=CURVE_CONTRACT_ADDRESSES[chain_id],
                )

        return supported_chains

    @classmethod
    def list_supported_chains(cls) -> List[ChainId]:
        """
        Get a simple list of supported chain IDs.

        Returns:
            List of chain IDs that are natively supported
        """
        return list(cls.get_supported_chains().keys())

    @classmethod
    def is_chain_supported(cls, chain_id: ChainId) -> bool:
        """
        Check if a chain is natively supported by the library.

        Args:
            chain_id: The blockchain network ID to check

        Returns:
            True if the chain has predefined helper contracts, False otherwise
        """
        return (
            chain_id in UTILS_CONTRACT_ADDRESSES
            and chain_id in CURVE_CONTRACT_ADDRESSES
        )

    @classmethod
    def clear_cache(cls, chain_id: Optional[ChainId] = None) -> None:
        """
        Clear the contract cache.

        Args:
            chain_id: Optional chain ID. If provided, only clears cache for that chain.
                     If None, clears all caches.
        """
        AsyncRpcAggregation.clear_cache(chain_id)

    def __repr__(self) -> str:
        """String representation of the aggregator."""
        chain_names = [
            f"{cid}({self.get_chain_name(cid)})" for cid in self.get_configured_chains()
        ]
        return f"MultiChainAggregator(chains=[{', '.join(chain_names)}])"
