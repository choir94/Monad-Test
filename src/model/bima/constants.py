from web3 import Web3

FAUCET_ADDRESS = "0x15e47CF518073bd980f10a1064231db14238858A"
bmBTC = Web3.to_checksum_address("0x0bb0aa6aa3a3fd4f7a43fb5e3d90bf9e6b4ef799")
SPENDER_ADDRESS = Web3.to_checksum_address("0x07c4b0db9c020296275dceb6381397ac58bbf5c7")

# Стандартный ABI для ERC20 токена
TOKEN_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]

FAUCET_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "_tokenAddress", "type": "address"}
        ],
        "name": "getTokens",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

# Параметры для supplyCollateral
MARKET_PARAMS = (
    Web3.to_checksum_address("0x01a4b3221e078106f9eb60c5303e3ba162f6a92e"),  # loanToken
    bmBTC,  # collateralToken
    Web3.to_checksum_address("0x7c47e0c69fb30fe451da48185c78f0c508b3e5b8"),  # oracle
    Web3.to_checksum_address("0xc2d07bd8df5f33453e9ad4e77436b3eb70a09616"),  # irm
    900000000000000000,  # lltv (0.9 в wei)
)

LENDING_ABI = [
    {
        "type": "function",
        "name": "supplyCollateral",
        "inputs": [
            {
                "name": "marketParams",
                "type": "tuple",
                "components": [
                    {"name": "loanToken", "type": "address"},
                    {"name": "collateralToken", "type": "address"},
                    {"name": "oracle", "type": "address"},
                    {"name": "irm", "type": "address"},
                    {"name": "lltv", "type": "uint256"},
                ],
            },
            {"name": "assets", "type": "uint256"},
            {"name": "onBehalf", "type": "address"},
            {"name": "data", "type": "bytes"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    }
]
