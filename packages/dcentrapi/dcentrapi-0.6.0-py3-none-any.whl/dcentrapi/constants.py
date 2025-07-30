from typing import Dict

# Dictionary mapping chain_id to utils_contract address
UTILS_CONTRACT_ADDRESSES: Dict[int, str] = {
    1: "0x1159a7F493FDD145172bFDFF4764Bb89E6A99B68",  # ETHEREUM
    10: "0x3C3e9B7A3Fd6Ff61ed61e919369a2FF35308cFC2",  # OP MAINNET
    56: "0x7Af469c5a4ba5BF749866bcFC84F96026Ae50b92",  # BSC
    137: "0xA0745c764F6C3A56A305aa95e9aA83A9eb92AA8e",  # POLYGON
    250: "0xF6345c54161Dc1E1D08c48f908573E4918bBa3Df",  # FANTOM
    1030: "0x2976d522c15a86E69E608C06aAFB464EF6584FA3",  # CONFLUX
    2001: "0xe1D8F21f251413fC664084d46cC01f7Cca51852D",  # MILKOMEDA
    8453: "0x930d7f12f787266e92dfDA9Bb6c60BC149951A1F",  # BASE
    42161: "0x74EA85e968783AD211de4b6a535cfcd5618E2477",  # ARBITRUM
    43114: "0x0ce10C0f0FE9ad8Dadb639ca478cC3cA7E5d9E87",  # AVALANCHE
    59144: "0xe1D8F21f251413fC664084d46cC01f7Cca51852D",  # LINEA
}

# Dictionary mapping chain_id to curve helper contract address  
CURVE_CONTRACT_ADDRESSES: Dict[int, str] = {
    1: "0x23eD44EFdF2e1e43933f5d81Ec5Cbd3663e1f8F4",  # ETHEREUM (placeholder)
    10: "0x23eD44EFdF2e1e43933f5d81Ec5Cbd3663e1f8F4",  # OP MAINNET (placeholder)
    56: "0x23eD44EFdF2e1e43933f5d81Ec5Cbd3663e1f8F4",  # BSC (placeholder)
    137: "0x23eD44EFdF2e1e43933f5d81Ec5Cbd3663e1f8F4",  # POLYGON (placeholder)
    250: "0x23eD44EFdF2e1e43933f5d81Ec5Cbd3663e1f8F4",  # FANTOM (placeholder)
    1030: "0x23eD44EFdF2e1e43933f5d81Ec5Cbd3663e1f8F4",  # CONFLUX (placeholder)
    2001: "0x23eD44EFdF2e1e43933f5d81Ec5Cbd3663e1f8F4",  # MILKOMEDA (placeholder)
    8453: "0x23eD44EFdF2e1e43933f5d81Ec5Cbd3663e1f8F4",  # BASE (placeholder)
    42161: "0x23eD44EFdF2e1e43933f5d81Ec5Cbd3663e1f8F4",  # ARBITRUM (placeholder)
    43114: "0x23eD44EFdF2e1e43933f5d81Ec5Cbd3663e1f8F4",  # AVALANCHE (placeholder)
    59144: "0x23eD44EFdF2e1e43933f5d81Ec5Cbd3663e1f8F4",  # LINEA (placeholder)
}


def get_helper_address(chain_id: int) -> str:
    """
    Get the helper contract address for a specific blockchain.

    Args:
        chain_id: The chain ID of the blockchain.

    Returns:
        The helper contract address.

    Raises:
        ValueError: If the chain_id is not supported or doesn't have a helper contract.
    """

    address = UTILS_CONTRACT_ADDRESSES[chain_id]
    if not address:
        raise ValueError(
            f"No helper contract address available for chain ID {chain_id}"
        )

    return address


def get_curve_address(chain_id: int) -> str:
    """
    Get the curve helper contract address for a specific blockchain.

    Args:
        chain_id: The chain ID of the blockchain.

    Returns:
        The curve helper contract address.

    Raises:
        ValueError: If the chain_id is not supported or doesn't have a curve contract.
    """

    address = CURVE_CONTRACT_ADDRESSES.get(chain_id)
    if not address:
        raise ValueError(
            f"No curve contract address available for chain ID {chain_id}"
        )

    return address


FACTORY_TYPE_BALANCER = "BALANCER"
FACTORY_TYPE_CURVE = "CURVE"
FACTORY_TYPE_UNI_V2 = "UNI_V2"
FACTORY_TYPE_UNI_V3 = "UNI_V3"
