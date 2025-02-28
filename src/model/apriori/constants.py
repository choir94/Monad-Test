
STAKE_ADDRESS = "0xb2f82D0f38dc453D596Ad40A37799446Cc89274A"

STAKE_ABI = [
    {
        "type": "function",
        "name": "deposit",
        "inputs": [
            {
                "name": "assets",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "receiver",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "shares",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "payable",
    }
]
