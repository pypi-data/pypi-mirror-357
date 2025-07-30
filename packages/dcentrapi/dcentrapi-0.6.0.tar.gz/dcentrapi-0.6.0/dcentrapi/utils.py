from typing import List, Union, Tuple, Sequence, Optional, TypedDict
from decimal import Decimal
import logging
from web3.contract.async_contract import AsyncContract

# Constants for status and factory types
STATUS_OK = "OK"
STATUS_ERROR = "ERROR"
FACTORY_TYPE_UNI_V2 = "UNI_V2"
FACTORY_TYPE_UNI_V3 = "UNI_V3"  
FACTORY_TYPE_CURVE = "CURVE"

# Setup logger
logger = logging.getLogger(__name__)

# Type definitions
Address = str
ChainId = int
Amount = int

# TypedDict classes based on smart contract structures
class TokenReserveDict(TypedDict):
    """Token reserve data structure."""
    index: int
    address: str
    decimals: int
    amount_wei: int
    amount_units: float

class TokenDict(TypedDict):
    """Token data structure based on TokenData struct."""
    index: int
    address: str
    decimals: int
    symbol: str
    name: str

class PoolDict(TypedDict):
    """Pool data structure."""
    index: int
    pool: str
    tokens: List[TokenDict]

class ReserveDict(TypedDict):
    """Reserve data for a pool."""
    pool: str
    tokens: List[TokenReserveDict]

class ReservesResponseDict(TypedDict):
    """Response structure for reserves data."""
    status: str
    msg: str
    network: Union[str, int]
    factory_type: str
    pools: List[str]
    reserves: List[ReserveDict]

class PoolsResponseDict(TypedDict):
    """Response structure for pools data."""
    status: str
    msg: str
    network: Union[str, int]
    factory_type: str
    factory: str
    pools: List[PoolDict]
    indices: List[int]
    version: int


def from_wei(wei_amount=None, decimals=18):
    """Convert wei amount to human readable units."""
    if decimals < 0:
        raise Exception("from_wei decimals < 0")

    if wei_amount is None:
        raise Exception("from_wei eth_wei is None")

    int_eth_wei = int(wei_amount)
    res = int_eth_wei / (10**decimals)
    return res


# Reserve Asset is a tuple (tokenAddress, decimals, amount)
# Make a new tuple with a fourth item, which is amount after converting from wei,
# i.e. the amount the user sees
def append_amount_in_units(reserve_asset):
    """Add human readable amount to reserve asset tuple."""
    new_asset = reserve_asset + (from_wei(reserve_asset[2], reserve_asset[1]),)
    return new_asset


# response is [ReserveAsset, ReserveAsset]
def reserve_asset_pair_helper(response):
    """Helper to process reserve asset pairs."""
    for i in [0, 1]:
        response[i] = append_amount_in_units(response[i])
    return response


def get_token_reserve_dict(index: int, reserve: Tuple) -> TokenReserveDict:
    """Create token reserve dictionary."""
    return {
        "index": index,
        "address": reserve[0],
        "decimals": reserve[1],
        "amount_wei": reserve[2],
        "amount_units": reserve[3],
    }


def get_reserves_res_dict(
    status: str, 
    msg: str = "", 
    network: Union[str, int] = "", 
    factory_type: str = "", 
    pools: Optional[List[Address]] = None, 
    reserves: Optional[List[ReserveDict]] = None
) -> ReservesResponseDict:
    """Create reserves response dictionary."""
    fname = get_reserves_res_dict.__name__
    logger.info(fname)
    
    return {
        "status": status,
        "msg": msg,
        "network": network,
        "factory_type": factory_type,
        "pools": pools or [],
        "reserves": reserves or [],
    }


def get_reserves_res_err_dict(msg: str, network: Union[str, int] = "", factory_type: str = "") -> ReservesResponseDict:
    """Create error response dictionary for reserves."""
    fname = get_reserves_res_err_dict.__name__
    logger.info(fname)
    
    return get_reserves_res_dict(status=STATUS_ERROR, msg=msg, network=network, factory_type=factory_type)


def get_reserves_from_pools_helper(
    factory_type: str, 
    network: Union[str, int], 
    pools: List[Address], 
    response: List[List[Tuple]]
) -> ReservesResponseDict:
    """Helper to process reserves from multiple pools."""
    for i in [0, 1]:
        for j in range(len(response[i])):
            response[i][j] = append_amount_in_units(response[i][j])

    reserves = []
    for j in range(len(pools)):
        reserves.append(
            {
                "pool": pools[j],
                "tokens": [
                    get_token_reserve_dict(0, response[0][j]),
                    get_token_reserve_dict(1, response[1][j]),
                ],
            }
        )

    res = get_reserves_res_dict(
        status=STATUS_OK, network=network, factory_type=factory_type, pools=pools, reserves=reserves
    )
    return res


async def get_reserves_data_uni_pair(
    chain_id: ChainId, 
    contract: AsyncContract, 
    pools: Sequence[Address], 
    factory_type: str
) -> ReservesResponseDict:
    """Get reserves data for Uniswap pairs."""
    fname = get_reserves_data_uni_pair.__name__
    logger.info(fname)
    
    try:
        response = await contract.functions.getReservesFromPairs(pools).call()
        res = get_reserves_from_pools_helper(
            factory_type=factory_type, network=chain_id, pools=list(pools), response=response
        )
    except Exception as e:
        res = get_reserves_res_err_dict(
            msg=f"Contract call failed for getReservesFromPairs: {str(e)}",
            network=chain_id,
            factory_type=factory_type,
        )

    return res


def get_token_dict(index: int, token_data: Tuple) -> TokenDict:
    """Create token dictionary."""
    return {
        "index": index,
        "address": token_data[0],
        "decimals": token_data[1],
        "symbol": token_data[2],
        "name": token_data[3],
    }


def get_pool_dict(index: int, pool: Address, tokens: List[TokenDict]) -> PoolDict:
    """Create pool dictionary."""
    return {
        "index": index,
        "pool": pool,
        "tokens": tokens,
    }


def get_pools_res_dict(
    status: str, 
    msg: str = "", 
    network: Union[str, int] = "", 
    factory_type: str = "", 
    factory: Address = "", 
    pools: Optional[List[PoolDict]] = None, 
    indices: Optional[List[int]] = None, 
    version: int = 1
) -> PoolsResponseDict:
    """Create pools response dictionary."""
    fname = get_pools_res_dict.__name__
    logger.info(fname)

    return {
        "status": status,
        "msg": msg,
        "network": network,
        "factory_type": factory_type,
        "factory": factory,
        "pools": pools or [],
        "indices": indices or [],
        "version": version,
    }


def get_pools_res_err_dict(
    msg: str, 
    network: Union[str, int] = "", 
    factory_type: str = "", 
    factory: Address = ""
) -> PoolsResponseDict:
    """Create error response dictionary for pools."""
    fname = get_pools_res_err_dict.__name__
    logger.info(fname)

    return get_pools_res_dict(status=STATUS_ERROR, msg=msg, network=network, factory_type=factory_type, factory=factory)


def get_uni_v2_pair_and_token_data_from_factory_helper(
    factory_type: str, 
    network: Union[str, int], 
    factory: Address, 
    indices: List[int], 
    response: List[Tuple]
) -> PoolsResponseDict:
    """Helper for Uniswap V2 pair and token data."""
    fname = get_uni_v2_pair_and_token_data_from_factory_helper.__name__
    logger.info(fname)
    version = 2

    pools = []
    for i in range(len(indices)):
        index = indices[i]
        pair_and_token_data = response[i]
        pair_address = pair_and_token_data[0]
        token_data_0 = pair_and_token_data[1]
        token_data_1 = pair_and_token_data[2]
        token0 = get_token_dict(0, token_data_0)
        token1 = get_token_dict(1, token_data_1)
        pools.append(get_pool_dict(index=index, pool=pair_address, tokens=[token0, token1]))

    res = get_pools_res_dict(
        status=STATUS_OK,
        network=network,
        factory_type=factory_type,
        factory=factory,
        pools=pools,
        indices=indices,
        version=version,
    )
    return res


async def get_pool_data_uni_v2(
    chain_id: ChainId, 
    contract: AsyncContract, 
    factory: Address, 
    indices: List[int]
) -> PoolsResponseDict:
    """Get pool data for Uniswap V2."""
    fname = get_pool_data_uni_v2.__name__
    logger.info(fname)

    factory_type = FACTORY_TYPE_UNI_V2
    res = None
    try:
        response = await contract.functions.getPairAndTokenDataFromFactory(factory, indices).call()
        res = get_uni_v2_pair_and_token_data_from_factory_helper(
            factory_type=factory_type, network=chain_id, factory=factory, indices=indices, response=response
        )

    except Exception as e:
        res = get_pools_res_err_dict(
            msg=f"Contract call failed for getPairAndTokenDataFromFactory: {str(e)}",
            network=chain_id,
            factory_type=factory_type,
            factory=factory,
        )

    return res


def get_curve_pool_data_from_factory_helper(
    factory_type: str, 
    network: Union[str, int], 
    factory: Address, 
    indices: List[int], 
    response: List[Tuple]
) -> PoolsResponseDict:
    """Helper for Curve pool data."""
    fname = get_curve_pool_data_from_factory_helper.__name__
    logger.info(fname)

    pools = []
    for i in range(len(indices)):
        index = indices[i]
        pool_and_token_data = response[i]
        pool_address = pool_and_token_data[0]
        token_data_list = pool_and_token_data[1]
        tokens = []
        for idx in range(len(token_data_list)):
            token_data = token_data_list[idx]
            tokens.append(get_token_dict(idx, token_data))

        pools.append(get_pool_dict(index=index, pool=pool_address, tokens=tokens))

    res = get_pools_res_dict(
        status=STATUS_OK, network=network, factory_type=factory_type, factory=factory, pools=pools, indices=indices
    )
    return res


async def get_pool_data_curve(
    chain_id: ChainId, 
    contract: AsyncContract, 
    factory: Address, 
    indices: List[int]
) -> PoolsResponseDict:
    """Get pool data for Curve."""
    fname = get_pool_data_curve.__name__
    logger.info(fname)

    factory_type = FACTORY_TYPE_CURVE
    res = None
    try:
        response = await contract.functions.getPoolAndTokenDataFromFactoryCurve(factory, indices).call()
        res = get_curve_pool_data_from_factory_helper(
            factory_type=factory_type, network=chain_id, factory=factory, indices=indices, response=response
        )

    except Exception as e:
        res = get_pools_res_err_dict(
            msg=f"Contract call failed for getPoolAndTokenDataFromFactoryCurve: {str(e)}",
            network=chain_id,
            factory_type=factory_type,
            factory=factory,
        )

    return res


def get_usd_value_of_token(network: Union[str, int]) -> Decimal:
    """Get USD value of native token for the network."""
    # This is a placeholder implementation
    # In the original code, this would fetch actual USD values
    return Decimal("1.0")
