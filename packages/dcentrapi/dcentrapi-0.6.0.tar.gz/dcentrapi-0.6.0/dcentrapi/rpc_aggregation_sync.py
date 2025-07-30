import asyncio
import threading
from typing import List, Tuple, Optional
from decimal import Decimal
from web3 import Web3

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


class RpcAggregation:
    """
    Synchronous wrapper for AsyncRpcAggregation class.
    
    This class provides synchronous methods that wrap the async methods
    of AsyncRpcAggregation, handling the event loop management internally.
    """
    
    def __init__(self, web3: Web3, chain_id: ChainId):
        """
        Initialize the RpcAggregation class.

        Args:
            web3: Web3 instance (synchronous)
            chain_id: The chain ID of the blockchain
        """
        # Convert sync Web3 to AsyncWeb3 for the underlying async class
        from web3 import AsyncWeb3
        
        # Create AsyncWeb3 instance with the same provider
        if not hasattr(web3.provider, 'endpoint_uri'):
            raise ValueError(
                "Web3 provider must have an 'endpoint_uri' attribute. "
                "Only HTTP providers are currently supported for the sync wrapper."
            )
        
        endpoint_uri = getattr(web3.provider, 'endpoint_uri')
        if not endpoint_uri:
            raise ValueError("Web3 provider endpoint_uri cannot be empty.")
            
        self._async_web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(endpoint_uri))
        
        self._async_aggregation = AsyncRpcAggregation(self._async_web3, chain_id)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def _get_event_loop(self):
        """Get or create an event loop for async operations."""
        with self._lock:
            if self._loop is None or self._loop.is_closed():
                # Create a new event loop in a separate thread
                self._loop = asyncio.new_event_loop()
                self._thread = threading.Thread(
                    target=self._run_event_loop, 
                    daemon=True
                )
                self._thread.start()
            return self._loop
    
    def _run_event_loop(self):
        """Run the event loop in a separate thread."""
        if self._loop is not None:
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()
    
    def _run_async(self, coro):
        """Run an async coroutine and return the result."""
        try:
            # If we're already in an event loop, asyncio.run() would fail
            # So we use run_coroutine_threadsafe with our separate background loop
            asyncio.get_running_loop()  # This will raise RuntimeError if no loop is running
            loop = self._get_event_loop()
            future = asyncio.run_coroutine_threadsafe(coro, loop)
            return future.result()
        except RuntimeError:
            # No event loop running, safe to use asyncio.run()
            return asyncio.run(coro)
    
    def __del__(self):
        """Clean up the event loop when the object is destroyed."""
        if hasattr(self, '_loop') and self._loop and not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._loop.stop)
    
    @classmethod
    def clear_cache(cls, chain_id: Optional[ChainId] = None) -> None:
        """
        Clear the contract cache.

        Args:
            chain_id: Optional chain ID. If provided, only clears cache for that chain.
                     If None, clears all caches.
        """
        AsyncRpcAggregation.clear_cache(chain_id)

    def get_token_balance(
        self, user: Address, token: Address, rpc_url: Optional[str] = None
    ) -> Amount:
        """
        Get token balance for a user.

        Args:
            user: User address
            token: Token address
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            Token balance
        """
        return self._run_async(
            self._async_aggregation.get_token_balance(user, token, rpc_url)
        )

    def get_token_balances_for_user(
        self, user: Address, tokens: List[Address], rpc_url: Optional[str] = None
    ) -> Tuple[List[Address], List[Amount]]:
        """
        Get token balances for a user across multiple tokens.

        Args:
            user: User address
            tokens: List of token addresses
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            Tuple containing (token_addresses, token_balances)
        """
        return self._run_async(
            self._async_aggregation.get_token_balances_for_user(user, tokens, rpc_url)
        )

    def get_token_balance_for_users(
        self, users: List[Address], token: Address, rpc_url: Optional[str] = None
    ) -> Tuple[List[Address], List[Amount]]:
        """
        Get token balances for multiple users.

        Args:
            users: List of user addresses
            token: Token address
            rpc_url: RPC URL

        Returns:
            Tuple containing (user_addresses, token_balances)
        """
        return self._run_async(
            self._async_aggregation.get_token_balance_for_users(users, token, rpc_url)
        )

    def get_token_balances_for_users(
        self, users: List[Address], tokens: List[Address], rpc_url: Optional[str] = None
    ) -> List[Amount]:
        """
        Get token balances for multiple users and tokens.

        Args:
            users: List of user addresses
            tokens: List of token addresses
            rpc_url: RPC URL

        Returns:
            List of token balances
        """
        return self._run_async(
            self._async_aggregation.get_token_balances_for_users(users, tokens, rpc_url)
        )

    def calculate_token_price_from_pair(
        self, pool: Address, target_token_address: Address, rpc_url: str
    ) -> Tuple[Decimal, Address, Address]:
        """
        Calculate token price from a pair.

        Args:
            pool: Pool address
            target_token_address: Target token address
            rpc_url: RPC URL

        Returns:
            Tuple containing (token_price, token0_address, token1_address)
        """
        return self._run_async(
            self._async_aggregation.calculate_token_price_from_pair(
                pool, target_token_address, rpc_url
            )
        )

    def calculate_reserves_amount_from_pair(
        self, pool: Address, amount: Amount, rpc_url: str
    ) -> ReserveAssetDict:
        """
        Calculate reserves amount from a pair.

        Args:
            pool: Pool address
            amount: Amount
            rpc_url: RPC URL

        Returns:
            Dictionary with reserve asset information
        """
        return self._run_async(
            self._async_aggregation.calculate_reserves_amount_from_pair(
                pool, amount, rpc_url
            )
        )

    def get_reserves_from_pair(
        self, pool: Address, rpc_url: Optional[str] = None
    ) -> ReserveAssetDict:
        """
        Get reserves from a pair.

        Args:
            pool: Pool address
            rpc_url: RPC URL

        Returns:
            Dictionary with reserve asset information
        """
        return self._run_async(
            self._async_aggregation.get_reserves_from_pair(pool, rpc_url)
        )

    def get_reserves_from_pools(
        self, factory_type: FactoryType, pools: List[Address], rpc_url: str
    ) -> ReservesResponseDict:
        """
        Get reserves from pools.

        Args:
            factory_type: Factory type (UNI_V2, UNI_V3, CURVE, BALANCER)
            pools: List of pool addresses
            rpc_url: RPC URL

        Returns:
            Dictionary with reserve asset information
        """
        return self._run_async(
            self._async_aggregation.get_reserves_from_pools(
                factory_type, pools, rpc_url
            )
        )

    def get_pool_data_from_factory(
        self,
        factory_type: FactoryType,
        factory: Address,
        indices: List[int],
        rpc_url: str,
    ) -> PoolsResponseDict:
        """
        Get pool data from factory.

        Args:
            factory_type: Factory type (UNI_V2, UNI_V3, CURVE, BALANCER)
            factory: Factory address
            indices: List of indices
            rpc_url: RPC URL

        Returns:
            Dictionary with pool data
        """
        return self._run_async(
            self._async_aggregation.get_pool_data_from_factory(
                factory_type, factory, indices, rpc_url
            )
        )

    def get_uni_v3_pools_slot0_values(
        self, pools: List[Address], rpc_url: str
    ) -> List[Slot0DataDict]:
        """
        Get Uniswap V3 pool slot0 values.

        Args:
            pools: List of pool addresses
            rpc_url: RPC URL

        Returns:
            List of slot0 values
        """
        return self._run_async(
            self._async_aggregation.get_uni_v3_pools_slot0_values(pools, rpc_url)
        )

    def get_uni_v3_position_data(
        self,
        nft_pos_mgr_address: Address,
        token_ids: List[TokenId],
        rpc_url: str,
    ) -> List[UniswapNFTPositionDataDict]:
        """
        Get Uniswap V3 NFT position data.

        Args:
            nft_pos_mgr_address: NFT position manager address
            token_ids: List of token IDs
            rpc_url: RPC URL

        Returns:
            List of position data
        """
        return self._run_async(
            self._async_aggregation.get_uni_v3_position_data(
                nft_pos_mgr_address, token_ids, rpc_url
            )
        )

    def get_uni_v3_position_liquidity(
        self,
        nft_pos_mgr_address: Address,
        token_ids: List[TokenId],
        rpc_url: str,
    ) -> List[Amount]:
        """
        Get Uniswap V3 position liquidity data.

        Args:
            nft_pos_mgr_address: NFT position manager address
            token_ids: List of token IDs
            rpc_url: RPC URL

        Returns:
            List of liquidity data
        """
        return self._run_async(
            self._async_aggregation.get_uni_v3_position_liquidity(
                nft_pos_mgr_address, token_ids, rpc_url
            )
        )

    def estimate_amount_out(
        self, pool: Address, token_in: Address, amount_in: Amount, rpc_url: Optional[str] = None
    ) -> Amount:
        """
        Estimate amount out.

        Args:
            pool: Pool address
            token_in: Token in address
            amount_in: Amount in
            rpc_url: RPC URL

        Returns:
            Estimated amount out
        """
        return self._run_async(
            self._async_aggregation.estimate_amount_out(
                pool, token_in, amount_in, rpc_url
            )
        )

    def swap_exact_input_single(
        self,
        address_of_swap_router: Address,
        pool: Address,
        token_in: Address,
        amount_in: Amount,
        deadline: Deadline,
        amount_out_minimum: Amount,
        rpc_url: str,
    ) -> Amount:
        """
        Swap exact input single.

        Args:
            address_of_swap_router: Swap router address
            pool: Pool address
            token_in: Token in address
            amount_in: Amount in
            deadline: Deadline
            amount_out_minimum: Amount out minimum
            rpc_url: RPC URL

        Returns:
            Amount out
        """
        return self._run_async(
            self._async_aggregation.swap_exact_input_single(
                address_of_swap_router,
                pool,
                token_in,
                amount_in,
                deadline,
                amount_out_minimum,
                rpc_url,
            )
        )

    def swap_exact_output_single(
        self,
        address_of_swap_router: Address,
        pool: Address,
        token_in: Address,
        amount_in_maximum: Amount,
        deadline: Deadline,
        amount_out: Amount,
        rpc_url: str,
    ) -> Amount:
        """
        Swap exact output single.

        Args:
            address_of_swap_router: Swap router address
            pool: Pool address
            token_in: Token in address
            amount_in_maximum: Maximum amount in
            deadline: Deadline
            amount_out: Amount out
            rpc_url: RPC URL

        Returns:
            Amount in
        """
        return self._run_async(
            self._async_aggregation.swap_exact_output_single(
                address_of_swap_router,
                pool,
                token_in,
                amount_in_maximum,
                deadline,
                amount_out,
                rpc_url,
            )
        ) 