from typing import List, Dict, Tuple, Optional, ClassVar, Union, Sequence, TypedDict

from decimal import Decimal
import logging
from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContract


from dcentrapi.abis.dcentral_helper import DCENTRA_UTILS_ABI
from dcentrapi.constants import (
    get_helper_address,
    get_curve_address,
    FACTORY_TYPE_UNI_V2,
    FACTORY_TYPE_UNI_V3,
    FACTORY_TYPE_CURVE,
)

from dcentrapi.utils import (
    Address,
    Amount,
    ChainId,
    reserve_asset_pair_helper,
    get_reserves_data_uni_pair,
    get_reserves_res_err_dict,
    get_pool_data_uni_v2,
    get_pool_data_curve,
    get_pools_res_err_dict,
    ReservesResponseDict,
    PoolsResponseDict,
)

# Setup logger
logger = logging.getLogger(__name__)

# Type definitions for better type safety

TokenId = int
Deadline = int
FactoryType = str
# ReserveAsset tuple from smart contract: (tokenAddress, decimals, amount)
ReserveAssetTuple = Tuple[str, int, int]
# Processed ReserveAsset with amount_units: (tokenAddress, decimals, amount_wei, amount_units)
ProcessedReserveAssetTuple = Tuple[str, int, int, float]
# Single token reserve data
TokenReserveData = Dict[str, Union[str, int, float]]
# Dictionary representation for API responses with token0 and token1
ReserveAssetDict = Dict[str, TokenReserveData]

# TypedDict classes based on smart contract structures
class Slot0DataDict(TypedDict):
    """Slot0 data structure based on Slot0Data struct."""
    isValid: bool
    sqrtPriceX96: int
    tick: int
    observationIndex: int
    observationCardinality: int
    observationCardinalityNext: int
    feeProtocol: int
    unlocked: bool

class UniswapNFTPositionDataDict(TypedDict):
    """Uniswap NFT position data based on UniswapNFTPositionData struct."""
    isPosition: bool
    nonce: int
    operator: str
    token0: str
    token1: str
    fee: int
    tickLower: int
    tickUpper: int
    liquidity: int
    feeGrowthInside0LastX128: int
    feeGrowthInside1LastX128: int
    tokensOwed0: int
    tokensOwed1: int

# Legacy type aliases for backward compatibility
SlotValue = Slot0DataDict
PositionData = UniswapNFTPositionDataDict


class AsyncRpcAggregation:
    # Class-level contract cache
    _contract_cache: ClassVar[Dict[ChainId, Dict[str, AsyncContract]]] = {}

    def __init__(self, web3: AsyncWeb3, chain_id: ChainId):
        """
        Initialize the AsyncRpcAggregation class.

        Args:
            web3: AsyncWeb3 instance
            chain_id: The chain ID of the blockchain
        """
        self.web3 = web3
        self.chain_id = chain_id
        
        # Extract default RPC URL from the Web3 provider
        self._default_rpc_url = None
        if hasattr(web3.provider, 'endpoint_uri'):
            self._default_rpc_url = getattr(web3.provider, 'endpoint_uri')

        # Initialize chain-specific cache if it doesn't exist
        if self.chain_id not in AsyncRpcAggregation._contract_cache:
            AsyncRpcAggregation._contract_cache[self.chain_id] = {}

    def _get_rpc_url(self, rpc_url: Optional[str] = None) -> str:
        """
        Get the RPC URL to use, defaulting to the provider's endpoint if not specified.
        
        Args:
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.
            
        Returns:
            The RPC URL to use
            
        Raises:
            ValueError: If no RPC URL is provided and no default is available
        """
        if rpc_url is not None:
            return rpc_url
        
        if self._default_rpc_url is not None:
            return self._default_rpc_url
            
        raise ValueError(
            "No RPC URL provided and Web3 provider doesn't have an endpoint_uri. "
            "Please provide an rpc_url parameter or use a Web3 provider with endpoint_uri."
        )

    async def _get_helper_contract(self, rpc_url: str) -> AsyncContract:
        """
        Get or create an async contract instance for the RPC helper.
        Uses a cached instance if available.

        Args:
            rpc_url: The RPC URL to use for this contract

        Returns:
            AsyncContract instance for the RPC helper
        """
        # Get helper address for this chain
        address = get_helper_address(self.chain_id)
        checksum_address = self.web3.to_checksum_address(address)

        # Check if the contract is already in the cache
        contract_key = f"helper:{checksum_address}:{rpc_url}"
        chain_cache = AsyncRpcAggregation._contract_cache[self.chain_id]

        if contract_key not in chain_cache:
            # Create the contract instance and cache it
            chain_cache[contract_key] = self.web3.eth.contract(
                address=checksum_address, abi=DCENTRA_UTILS_ABI
            )

        return chain_cache[contract_key]

    async def get_curve_contract(self, rpc_url: Optional[str] = None) -> AsyncContract:
        """
        Get or create an async contract instance for the Curve helper.
        Uses a cached instance if available.

        Args:
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            AsyncContract instance for the Curve helper
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        # Get curve helper address for this chain
        address = get_curve_address(self.chain_id)
        checksum_address = self.web3.to_checksum_address(address)

        # Check if the contract is already in the cache
        contract_key = f"curve:{checksum_address}:{actual_rpc_url}"
        chain_cache = AsyncRpcAggregation._contract_cache[self.chain_id]

        if contract_key not in chain_cache:
            # Create the contract instance and cache it
            chain_cache[contract_key] = self.web3.eth.contract(
                address=checksum_address, abi=DCENTRA_UTILS_ABI
            )

        return chain_cache[contract_key]

    async def _get_token_balances_for_user_helper(
        self, contract: AsyncContract, user: Address, tokens: Sequence[Address]
    ) -> Tuple[List[Address], List[Amount]]:
        """
        Helper function to handle token balances for a user when there are many tokens.
        Breaks the tokens into chunks of 1700 to avoid contract call size limitations.

        Args:
            contract: AsyncContract instance
            user: User address
            tokens: List of token addresses

        Returns:
            Tuple of (token_addresses, token_balances)
        """
        MAX_TOKENS_PER_CALL = 1700
        all_tokens: List[Address] = []
        all_balances: List[Amount] = []

        # Process tokens in chunks of 1700
        for i in range(0, len(tokens), MAX_TOKENS_PER_CALL):
            chunk = tokens[i : i + MAX_TOKENS_PER_CALL]
            result = await contract.functions.tokenBalancesForUser(user, chunk).call()
            all_tokens.extend(result[0])
            all_balances.extend(result[1])

        return (all_tokens, all_balances)

    async def _get_token_balance_for_users_helper(
        self, contract: AsyncContract, token: Address, users: Sequence[Address]
    ) -> Tuple[List[Address], List[Amount]]:
        """
        Helper function to handle token balances for users when there are many users.
        Breaks the users into chunks of 1700 to avoid contract call size limitations.

        Args:
            contract: AsyncContract instance
            token: Token address
            users: List of user addresses

        Returns:
            Tuple of (user_addresses, token_balances)
        """
        MAX_USERS_PER_CALL = 1700
        all_users: List[Address] = []
        all_balances: List[Amount] = []

        # Process users in chunks of 1700
        for i in range(0, len(users), MAX_USERS_PER_CALL):
            chunk = users[i : i + MAX_USERS_PER_CALL]
            result = await contract.functions.tokenBalanceForUsers(chunk, token).call()
            all_users.extend(result[0])
            all_balances.extend(result[1])

        return (all_users, all_balances)

    @classmethod
    def clear_cache(cls, chain_id: Optional[ChainId] = None) -> None:
        """
        Clear the contract cache.

        Args:
            chain_id: Optional chain ID. If provided, only clears cache for that chain.
                     If None, clears all caches.
        """
        if chain_id is not None:
            if chain_id in cls._contract_cache:
                cls._contract_cache[chain_id] = {}
        else:
            cls._contract_cache = {}

    async def get_token_balance(
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
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        user_address = self.web3.to_checksum_address(user)
        token_address = self.web3.to_checksum_address(token)

        balance = await contract.functions.tokenBalance(
            user_address, token_address
        ).call()

        return balance

    async def get_token_balances_for_user(
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
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        user_address = self.web3.to_checksum_address(user)
        token_addresses = [self.web3.to_checksum_address(token) for token in tokens]

        if len(token_addresses) > 1700:
            response = await self._get_token_balances_for_user_helper(
                contract, user_address, token_addresses
            )
        else:
            response = await contract.functions.tokenBalancesForUser(
                user_address, token_addresses
            ).call()

        return response

    async def get_token_balance_for_users(
        self, users: List[Address], token: Address, rpc_url: Optional[str] = None
    ) -> Tuple[List[Address], List[Amount]]:
        """
        Get token balances for multiple users.

        Args:
            users: List of user addresses
            token: Token address
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            Tuple containing (user_addresses, token_balances)
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        user_addresses = [self.web3.to_checksum_address(user) for user in users]
        token_address = self.web3.to_checksum_address(token)

        if len(user_addresses) > 1700:
            response = await self._get_token_balance_for_users_helper(
                contract, token_address, user_addresses
            )
        else:
            response = await contract.functions.tokenBalanceForUsers(
                user_addresses, token_address
            ).call()

        return response

    async def get_token_balances_for_users(
        self, users: List[Address], tokens: List[Address], rpc_url: Optional[str] = None
    ) -> List[Amount]:
        """
        Get token balances for multiple users and tokens.

        Args:
            users: List of user addresses
            tokens: List of token addresses
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            List of token balances
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        user_addresses = [self.web3.to_checksum_address(user) for user in users]
        token_addresses = [self.web3.to_checksum_address(token) for token in tokens]

        return await contract.functions.tokenBalances(
            user_addresses, token_addresses
        ).call()

    async def calculate_token_price_from_pair(
        self, pool: Address, target_token_address: Address, rpc_url: Optional[str] = None
    ) -> Tuple[Decimal, Address, Address]:
        """
        Calculate token price from a pair.

        Args:
            pool: Pool address
            target_token_address: Target token address
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            Tuple containing (token_price, token0_address, token1_address)
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        pool_address = self.web3.to_checksum_address(pool)
        target_token = self.web3.to_checksum_address(target_token_address)

        response = await contract.functions.getReservesFromPair(pool_address).call()

        (
            token0_address,
            token0_decimal,
            token0_price,
            token1_address,
            token1_decimal,
            token1_price,
        ) = response[0] + response[1]

        # Convert from wei using custom decimal calculation instead of Web3.from_wei
        # since Web3.from_wei expects unit names, not decimal places
        token0_price_decimal = Decimal(token0_price) / Decimal(10 ** token0_decimal)
        token1_price_decimal = Decimal(token1_price) / Decimal(10 ** token1_decimal)
        token_price = token0_price_decimal / token1_price_decimal

        if target_token == token1_address:
            token_price = Decimal(1) / token_price

        return (token_price, token0_address, token1_address)

    async def calculate_reserves_amount_from_pair(
        self, pool: Address, amount: Amount, rpc_url: Optional[str] = None
    ) -> ReserveAssetDict:
        """
        Calculate reserves amount from a pair.

        Args:
            pool: Pool address
            amount: Amount
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            Dictionary with reserve asset information
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        pool_address = self.web3.to_checksum_address(pool)

        response = await contract.functions.calculateReservesAmountsFromPair(
            pool_address, amount
        ).call()

        # Process the response to add human-readable amounts
        processed_response = reserve_asset_pair_helper(response)
        
        # Convert to dictionary format
        return {
            "token0": {
                "address": processed_response[0][0],
                "decimals": processed_response[0][1],
                "amount_wei": processed_response[0][2],
                "amount_units": processed_response[0][3],
            },
            "token1": {
                "address": processed_response[1][0],
                "decimals": processed_response[1][1],
                "amount_wei": processed_response[1][2],
                "amount_units": processed_response[1][3],
            },
        }

    async def get_reserves_from_pair(
        self, pool: Address, rpc_url: Optional[str] = None
    ) -> ReserveAssetDict:
        """
        Get reserves from a pair.

        Args:
            pool: Pool address
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            Dictionary with reserve asset information
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        pool_address = self.web3.to_checksum_address(pool)

        response = await contract.functions.getReservesFromPair(pool_address).call()

        # Process the response to add human-readable amounts
        processed_response = reserve_asset_pair_helper(response)
        
        # Convert to dictionary format
        return {
            "token0": {
                "address": processed_response[0][0],
                "decimals": processed_response[0][1],
                "amount_wei": processed_response[0][2],
                "amount_units": processed_response[0][3],
            },
            "token1": {
                "address": processed_response[1][0],
                "decimals": processed_response[1][1],
                "amount_wei": processed_response[1][2],
                "amount_units": processed_response[1][3],
            },
        }

    async def get_reserves_from_pools(
        self, factory_type: FactoryType, pools: List[Address], rpc_url: Optional[str] = None
    ) -> ReservesResponseDict:
        """
        Get reserves from pools.

        Args:
            factory_type: Factory type (UNI_V2, UNI_V3, CURVE, BALANCER)
            pools: List of pool addresses
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            Dictionary with reserve asset information
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        pool_addresses = [self.web3.to_checksum_address(pool) for pool in pools]
        factory_type = factory_type.upper()

        if factory_type == FACTORY_TYPE_UNI_V2 or factory_type == FACTORY_TYPE_UNI_V3:
            return await get_reserves_data_uni_pair(
                chain_id=self.chain_id,
                contract=contract,
                pools=pool_addresses,
                factory_type=factory_type,
            )
        else:
            # Unsupported factory type
            return get_reserves_res_err_dict(
                msg="Unsupported factory type for get_reserves_from_pools",
                network=self.chain_id,
                factory_type=factory_type,
            )

    async def get_pool_data_from_factory(
        self,
        factory_type: FactoryType,
        factory: Address,
        indices: List[int],
        rpc_url: Optional[str] = None,
    ) -> PoolsResponseDict:
        """
        Get pool data from factory.

        Args:
            factory_type: Factory type (UNI_V2, UNI_V3, CURVE, BALANCER)
            factory: Factory address
            indices: List of indices
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            Dictionary with pool data
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        factory_address = self.web3.to_checksum_address(factory)
        factory_type = factory_type.upper()
        indices = [int(i) for i in indices]

        if factory_type == FACTORY_TYPE_UNI_V2:
            contract = await self._get_helper_contract(actual_rpc_url)
            return await get_pool_data_uni_v2(
                chain_id=self.chain_id,
                contract=contract,
                factory=factory_address,
                indices=indices,
            )
        elif factory_type == FACTORY_TYPE_CURVE:
            # For Curve, use the cached curve contract
            curve_contract = await self.get_curve_contract(actual_rpc_url)
            return await get_pool_data_curve(
                chain_id=self.chain_id,
                contract=curve_contract,
                factory=factory_address,
                indices=indices,
            )
        else:
            # Unsupported factory type
            return get_pools_res_err_dict(
                msg="Unsupported factory type for get_pool_data_from_factory",
                network=self.chain_id,
                factory_type=factory_type,
            )

    async def get_uni_v3_pools_slot0_values(
        self, pools: List[Address], rpc_url: Optional[str] = None
    ) -> List[Slot0DataDict]:
        """
        Get Uniswap V3 pool slot0 values.

        Args:
            pools: List of pool addresses
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            List of slot0 values
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        pool_addresses = [self.web3.to_checksum_address(pool) for pool in pools]

        try:
            slot0_values = await contract.functions.getSlot0Values(
                pool_addresses
            ).call()

            # Convert to a more usable format
            result: List[Slot0DataDict] = []
            for value in slot0_values:
                result.append(
                    {
                        "isValid": value[0],
                        "sqrtPriceX96": value[1],
                        "tick": value[2],
                        "observationIndex": value[3],
                        "observationCardinality": value[4],
                        "observationCardinalityNext": value[5],
                        "feeProtocol": value[6],
                        "unlocked": value[7],
                    }
                )
            return result

        except Exception as e:
            logger.error(f"Error getting slot0 values: {e}")
            return []

    async def get_uni_v3_position_data(
        self,
        nft_pos_mgr_address: Address,
        token_ids: List[TokenId],
        rpc_url: Optional[str] = None,
    ) -> List[UniswapNFTPositionDataDict]:
        """
        Get Uniswap V3 NFT position data.

        Args:
            nft_pos_mgr_address: NFT position manager address
            token_ids: List of token IDs
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            List of position data
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        nft_mgr_address = self.web3.to_checksum_address(nft_pos_mgr_address)

        try:
            position_data = await contract.functions.getUniV3NFTPositionData(
                nft_mgr_address, token_ids
            ).call()

            # Convert to a more usable format
            result: List[UniswapNFTPositionDataDict] = []
            for data in position_data:
                result.append(
                    {
                        "isPosition": data[0],
                        "nonce": data[1],
                        "operator": data[2],
                        "token0": data[3],
                        "token1": data[4],
                        "fee": data[5],
                        "tickLower": data[6],
                        "tickUpper": data[7],
                        "liquidity": data[8],
                        "feeGrowthInside0LastX128": data[9],
                        "feeGrowthInside1LastX128": data[10],
                        "tokensOwed0": data[11],
                        "tokensOwed1": data[12],
                    }
                )
            return result

        except Exception as e:
            logger.error(f"Error getting position data: {e}")
            return []

    async def get_uni_v3_position_liquidity(
        self,
        nft_pos_mgr_address: Address,
        token_ids: List[TokenId],
        rpc_url: Optional[str] = None,
    ) -> List[Amount]:
        """
        Get Uniswap V3 position liquidity data.

        Args:
            nft_pos_mgr_address: NFT position manager address
            token_ids: List of token IDs
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            List of liquidity data
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        nft_mgr_address = self.web3.to_checksum_address(nft_pos_mgr_address)

        try:
            liquidity_data = await contract.functions.getUniV3LiquidityData(
                nft_mgr_address, token_ids
            ).call()
            return liquidity_data

        except Exception as e:
            logger.error(f"Error getting liquidity data: {e}")
            return []

    async def estimate_amount_out(
        self, pool: Address, token_in: Address, amount_in: Amount, rpc_url: Optional[str] = None
    ) -> Amount:
        """
        Estimate amount out.

        Args:
            pool: Pool address
            token_in: Token in address
            amount_in: Amount in
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            Estimated amount out
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        pool_address = self.web3.to_checksum_address(pool)
        token_in_address = self.web3.to_checksum_address(token_in)

        return await contract.functions.estimateAmountOut(
            pool_address, token_in_address, amount_in
        ).call()

    async def swap_exact_input_single(
        self,
        address_of_swap_router: Address,
        pool: Address,
        token_in: Address,
        amount_in: Amount,
        deadline: Deadline,
        amount_out_minimum: Amount,
        rpc_url: Optional[str] = None,
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
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            Amount out
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        router_address = self.web3.to_checksum_address(address_of_swap_router)
        pool_address = self.web3.to_checksum_address(pool)
        token_in_address = self.web3.to_checksum_address(token_in)

        return await contract.functions.swapExactInputSingle(
            router_address,
            pool_address,
            token_in_address,
            amount_in,
            deadline,
            amount_out_minimum,
        ).call()

    async def swap_exact_output_single(
        self,
        address_of_swap_router: Address,
        pool: Address,
        token_in: Address,
        amount_in_maximum: Amount,
        deadline: Deadline,
        amount_out: Amount,
        rpc_url: Optional[str] = None,
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
            rpc_url: Optional RPC URL. If None, uses the default from the Web3 provider.

        Returns:
            Amount in
        """
        actual_rpc_url = self._get_rpc_url(rpc_url)
        contract = await self._get_helper_contract(actual_rpc_url)
        router_address = self.web3.to_checksum_address(address_of_swap_router)
        pool_address = self.web3.to_checksum_address(pool)
        token_in_address = self.web3.to_checksum_address(token_in)

        return await contract.functions.swapExactOutputSingle(
            router_address,
            pool_address,
            token_in_address,
            amount_in_maximum,
            deadline,
            amount_out,
        ).call()
