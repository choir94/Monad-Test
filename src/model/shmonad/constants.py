SHMONAD_ADDRESS = "0x3a98250F98Dd388C211206983453837C8365BDc1"

# Policy ID для стейкинга
STAKE_POLICY_ID = 4

# ABI для стейкинга
STAKE_ABI = [
    {
        "type": "function",
        "name": "commitToPool",
        "inputs": [
            {"name": "poolId", "type": "uint256"},
            {"name": "account", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "stake",
        "inputs": [
            {"name": "poolId", "type": "uint256"},
            {"name": "account", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "bond",
        "inputs": [
            {"name": "policyID", "type": "uint64", "internalType": "uint64"},
            {"name": "bondRecipient", "type": "address", "internalType": "address"},
            {"name": "amount", "type": "uint256", "internalType": "uint256"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "commit",
        "inputs": [
            {"name": "poolId", "type": "uint256"},
            {"name": "account", "type": "address"},
            {"name": "amount", "type": "uint256"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "unbond",
        "inputs": [
            {"name": "policyID", "type": "uint64", "internalType": "uint64"},
            {"name": "amount", "type": "uint256", "internalType": "uint256"},
            {"name": "newMinBalance", "type": "uint256", "internalType": "uint256"},
        ],
        "outputs": [
            {"name": "unbondBlock", "type": "uint256", "internalType": "uint256"}
        ],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "balanceOfBonded",
        "inputs": [
            {"name": "policyID", "type": "uint64", "internalType": "uint64"},
            {"name": "account", "type": "address", "internalType": "address"},
        ],
        "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "claim",
        "inputs": [
            {"name": "policyID", "type": "uint64", "internalType": "uint64"},
            {"name": "amount", "type": "uint256", "internalType": "uint256"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
]

# Основное ABI для других операций
SHMONAD_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "type": "function",
        "name": "deposit",
        "inputs": [
            {"name": "assets", "type": "uint256", "internalType": "uint256"},
            {"name": "receiver", "type": "address", "internalType": "address"},
        ],
        "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}],
        "stateMutability": "payable",
    },
    # Добавляем методы из STAKE_ABI
    *STAKE_ABI,
    {
        "type": "function",
        "name": "redeem",
        "inputs": [
            {"name": "assets", "type": "uint256"},
            {"name": "receiver", "type": "address"},
            {"name": "owner", "type": "address"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
]
