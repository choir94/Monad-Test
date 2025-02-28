STAKE_ADDRESS = "0x2c9C959516e9AAEdB2C748224a41249202ca8BE7"

STAKE_ABI = [
    {
        "type": "function",
        "name": "stake",  # используем произвольное имя функции
        "inputs": [],
        "outputs": [],
        "stateMutability": "payable",
        "signature": "0xd5575982"  # важно: используем точную сигнатуру из успешной транзакции
    }
]

