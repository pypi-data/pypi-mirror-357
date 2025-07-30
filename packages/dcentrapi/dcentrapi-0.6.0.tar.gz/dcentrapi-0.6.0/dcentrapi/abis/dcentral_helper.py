DCENTRA_UTILS_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "pool", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
        ],
        "name": "calculateReservesAmountsFromPair",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "tokenAddress",
                        "type": "address",
                    },
                    {"internalType": "uint256", "name": "decimals", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                ],
                "internalType": "struct DcentraLabTokensUtil.ReserveAsset",
                "name": "",
                "type": "tuple",
            },
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "tokenAddress",
                        "type": "address",
                    },
                    {"internalType": "uint256", "name": "decimals", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                ],
                "internalType": "struct DcentraLabTokensUtil.ReserveAsset",
                "name": "",
                "type": "tuple",
            },
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "dcentralabCongress",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "pool", "type": "address"},
            {"internalType": "address", "name": "tokenIn", "type": "address"},
            {"internalType": "uint128", "name": "amountIn", "type": "uint128"},
        ],
        "name": "estimateAmountOut",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "factoryAddress", "type": "address"},
            {"internalType": "uint256[]", "name": "indices", "type": "uint256[]"},
        ],
        "name": "getPairAndTokenDataFromFactory",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "pairAddress",
                        "type": "address",
                    },
                    {
                        "components": [
                            {
                                "internalType": "address",
                                "name": "tokenAddress",
                                "type": "address",
                            },
                            {
                                "internalType": "uint8",
                                "name": "decimals",
                                "type": "uint8",
                            },
                            {
                                "internalType": "string",
                                "name": "symbol",
                                "type": "string",
                            },
                            {
                                "internalType": "string",
                                "name": "name",
                                "type": "string",
                            },
                        ],
                        "internalType": "struct DcentraLabTokensUtil.TokenData",
                        "name": "token0",
                        "type": "tuple",
                    },
                    {
                        "components": [
                            {
                                "internalType": "address",
                                "name": "tokenAddress",
                                "type": "address",
                            },
                            {
                                "internalType": "uint8",
                                "name": "decimals",
                                "type": "uint8",
                            },
                            {
                                "internalType": "string",
                                "name": "symbol",
                                "type": "string",
                            },
                            {
                                "internalType": "string",
                                "name": "name",
                                "type": "string",
                            },
                        ],
                        "internalType": "struct DcentraLabTokensUtil.TokenData",
                        "name": "token1",
                        "type": "tuple",
                    },
                ],
                "internalType": "struct DcentraLabTokensUtil.PairAndTokenData[]",
                "name": "",
                "type": "tuple[]",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "factoryAddress", "type": "address"},
            {"internalType": "uint256[]", "name": "indices", "type": "uint256[]"},
        ],
        "name": "getPoolAndTokenDataFromFactoryCurve",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "poolAddress",
                        "type": "address",
                    },
                    {
                        "components": [
                            {
                                "internalType": "address",
                                "name": "tokenAddress",
                                "type": "address",
                            },
                            {
                                "internalType": "uint8",
                                "name": "decimals",
                                "type": "uint8",
                            },
                            {
                                "internalType": "string",
                                "name": "symbol",
                                "type": "string",
                            },
                            {
                                "internalType": "string",
                                "name": "name",
                                "type": "string",
                            },
                        ],
                        "internalType": "struct DcentraLabTokensUtil.TokenData[]",
                        "name": "tokens",
                        "type": "tuple[]",
                    },
                ],
                "internalType": "struct DcentraLabTokensUtil.PoolAndTokenData[]",
                "name": "",
                "type": "tuple[]",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "pool", "type": "address"}],
        "name": "getReservesFromPair",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "tokenAddress",
                        "type": "address",
                    },
                    {"internalType": "uint256", "name": "decimals", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                ],
                "internalType": "struct DcentraLabTokensUtil.ReserveAsset",
                "name": "",
                "type": "tuple",
            },
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "tokenAddress",
                        "type": "address",
                    },
                    {"internalType": "uint256", "name": "decimals", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                ],
                "internalType": "struct DcentraLabTokensUtil.ReserveAsset",
                "name": "",
                "type": "tuple",
            },
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address[]", "name": "pools", "type": "address[]"}],
        "name": "getReservesFromPairs",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "tokenAddress",
                        "type": "address",
                    },
                    {"internalType": "uint256", "name": "decimals", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                ],
                "internalType": "struct DcentraLabTokensUtil.ReserveAsset[]",
                "name": "",
                "type": "tuple[]",
            },
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "tokenAddress",
                        "type": "address",
                    },
                    {"internalType": "uint256", "name": "decimals", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount", "type": "uint256"},
                ],
                "internalType": "struct DcentraLabTokensUtil.ReserveAsset[]",
                "name": "",
                "type": "tuple[]",
            },
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address[]", "name": "pools", "type": "address[]"}],
        "name": "getSlot0Values",
        "outputs": [
            {
                "components": [
                    {"internalType": "bool", "name": "isValid", "type": "bool"},
                    {
                        "internalType": "uint160",
                        "name": "sqrtPriceX96",
                        "type": "uint160",
                    },
                    {"internalType": "int24", "name": "tick", "type": "int24"},
                    {
                        "internalType": "uint16",
                        "name": "observationIndex",
                        "type": "uint16",
                    },
                    {
                        "internalType": "uint16",
                        "name": "observationCardinality",
                        "type": "uint16",
                    },
                    {
                        "internalType": "uint16",
                        "name": "observationCardinalityNext",
                        "type": "uint16",
                    },
                    {"internalType": "uint32", "name": "feeProtocol", "type": "uint32"},
                    {"internalType": "bool", "name": "unlocked", "type": "bool"},
                ],
                "internalType": "struct DcentraLabTokensUtil.Slot0Data[]",
                "name": "",
                "type": "tuple[]",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "token", "type": "address"}],
        "name": "getTokenData",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "tokenAddress",
                        "type": "address",
                    },
                    {"internalType": "uint8", "name": "decimals", "type": "uint8"},
                    {"internalType": "string", "name": "symbol", "type": "string"},
                    {"internalType": "string", "name": "name", "type": "string"},
                ],
                "internalType": "struct DcentraLabTokensUtil.TokenData",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "token", "type": "address"}],
        "name": "getTotalSupply",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "nonfungiblePositionManager",
                "type": "address",
            },
            {"internalType": "uint256[]", "name": "tokenIds", "type": "uint256[]"},
        ],
        "name": "getUniV3LiquidityData",
        "outputs": [{"internalType": "int136[]", "name": "", "type": "int136[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "nonfungiblePositionManager",
                "type": "address",
            },
            {"internalType": "uint256[]", "name": "tokenIds", "type": "uint256[]"},
        ],
        "name": "getUniV3NFTPositionData",
        "outputs": [
            {
                "components": [
                    {"internalType": "bool", "name": "isPosition", "type": "bool"},
                    {"internalType": "uint96", "name": "nonce", "type": "uint96"},
                    {"internalType": "address", "name": "operator", "type": "address"},
                    {"internalType": "address", "name": "token0", "type": "address"},
                    {"internalType": "address", "name": "token1", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "int24", "name": "tickLower", "type": "int24"},
                    {"internalType": "int24", "name": "tickUpper", "type": "int24"},
                    {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
                    {
                        "internalType": "uint256",
                        "name": "feeGrowthInside0LastX128",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "feeGrowthInside1LastX128",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint128",
                        "name": "tokensOwed0",
                        "type": "uint128",
                    },
                    {
                        "internalType": "uint128",
                        "name": "tokensOwed1",
                        "type": "uint128",
                    },
                ],
                "internalType": "struct DcentraLabTokensUtil.UniswapNFTPositionData[]",
                "name": "",
                "type": "tuple[]",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_dcentralabCongress",
                "type": "address",
            },
            {
                "internalType": "address",
                "name": "_maintainersRegistry",
                "type": "address",
            },
        ],
        "name": "initialize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "maintainersRegistry",
        "outputs": [
            {
                "internalType": "contract IMaintainersRegistry",
                "name": "",
                "type": "address",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_dcentralabCongress",
                "type": "address",
            }
        ],
        "name": "setDcentralabCongress",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_maintainersRegistry",
                "type": "address",
            }
        ],
        "name": "setMaintainersRegistry",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "addrOfSwapRouter", "type": "address"},
            {"internalType": "address", "name": "pool", "type": "address"},
            {"internalType": "address", "name": "tokenIn", "type": "address"},
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
        ],
        "name": "swapExactInputSingle",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"}
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "addrOfSwapRouter", "type": "address"},
            {"internalType": "address", "name": "pool", "type": "address"},
            {"internalType": "address", "name": "tokenIn", "type": "address"},
            {"internalType": "uint256", "name": "amountInMaximum", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
        ],
        "name": "swapExactOutputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountIn", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "user", "type": "address"},
            {"internalType": "address", "name": "token", "type": "address"},
        ],
        "name": "tokenBalance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address[]", "name": "users", "type": "address[]"},
            {"internalType": "address", "name": "token", "type": "address"},
        ],
        "name": "tokenBalanceForUsers",
        "outputs": [
            {"internalType": "address[]", "name": "", "type": "address[]"},
            {"internalType": "uint256[]", "name": "", "type": "uint256[]"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address[]", "name": "users", "type": "address[]"},
            {"internalType": "address[]", "name": "tokens", "type": "address[]"},
        ],
        "name": "tokenBalances",
        "outputs": [{"internalType": "uint256[]", "name": "", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "user", "type": "address"},
            {"internalType": "address[]", "name": "tokens", "type": "address[]"},
        ],
        "name": "tokenBalancesForUser",
        "outputs": [
            {"internalType": "address[]", "name": "", "type": "address[]"},
            {"internalType": "int256[]", "name": "", "type": "int256[]"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address[]", "name": "tokens", "type": "address[]"}
        ],
        "name": "tokenSupplies",
        "outputs": [{"internalType": "int256[]", "name": "", "type": "int256[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {"stateMutability": "payable", "type": "receive"},
]
