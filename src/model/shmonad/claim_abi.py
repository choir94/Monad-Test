contract_abi = [
    {
        "type": "constructor",
        "inputs": [{
            "name": "addressHub",
            "type": "address",
            "internalType": "address"
        }],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "ADDRESS_HUB",
        "inputs": [],
        "outputs": [{
            "name": "",
            "type": "address",
            "internalType": "address"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "DOMAIN_SEPARATOR",
        "inputs": [],
        "outputs": [{
            "name": "",
            "type": "bytes32",
            "internalType": "bytes32"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "addPolicyAgent",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "agent",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "agentExecuteWithSponsor",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "payor",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "recipient",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "msgValue",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "gasLimit",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "callTarget",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "callData",
            "type": "bytes",
            "internalType": "bytes"
        }],
        "outputs": [{
            "name": "actualPayorCost",
            "type": "uint128",
            "internalType": "uint128"
        }, {
            "name": "success",
            "type": "bool",
            "internalType": "bool"
        }, {
            "name": "returnData",
            "type": "bytes",
            "internalType": "bytes"
        }],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "agentTransferFromBonded",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "from",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "to",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "fromReleaseAmount",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "inUnderlying",
            "type": "bool",
            "internalType": "bool"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "agentUnbond",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "from",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "fromReleaseAmount",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "inUnderlying",
            "type": "bool",
            "internalType": "bool"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "agentWithdrawFromBonded",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "from",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "to",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "fromReleaseAmount",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "inUnderlying",
            "type": "bool",
            "internalType": "bool"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "allowance",
        "inputs": [{
            "name": "owner",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "spender",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "approve",
        "inputs": [{
            "name": "spender",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "value",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [{
            "name": "",
            "type": "bool",
            "internalType": "bool"
        }],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "asset",
        "inputs": [],
        "outputs": [{
            "name": "",
            "type": "address",
            "internalType": "address"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "balanceOf",
        "inputs": [{
            "name": "account",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "balanceOfBonded",
        "inputs": [{
            "name": "account",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "balanceOfBonded",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "account",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "balanceOfUnbonding",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "account",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "batchHold",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "accounts",
            "type": "address[]",
            "internalType": "address[]"
        }, {
            "name": "amounts",
            "type": "uint256[]",
            "internalType": "uint256[]"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "batchRelease",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "accounts",
            "type": "address[]",
            "internalType": "address[]"
        }, {
            "name": "amounts",
            "type": "uint256[]",
            "internalType": "uint256[]"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "bond",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "bondRecipient",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "bondedTotalSupply",
        "inputs": [],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "boostYield",
        "inputs": [{
            "name": "shMonAmount",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "from",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "boostYield",
        "inputs": [],
        "outputs": [],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "claim",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "amount",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "claimAndRebond",
        "inputs": [{
            "name": "fromPolicyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "toPolicyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "bondRecipient",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "claimAndWithdraw",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "amount",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [{
            "name": "shares",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "convertToAssets",
        "inputs": [{
            "name": "shares",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "convertToShares",
        "inputs": [{
            "name": "assets",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "createPolicy",
        "inputs": [{
            "name": "escrowDuration",
            "type": "uint48",
            "internalType": "uint48"
        }],
        "outputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "policyERC20Wrapper",
            "type": "address",
            "internalType": "address"
        }],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "decimals",
        "inputs": [],
        "outputs": [{
            "name": "",
            "type": "uint8",
            "internalType": "uint8"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "deposit",
        "inputs": [{
            "name": "assets",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "receiver",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "depositAndBond",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "bondRecipient",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "shMonToBond",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "disablePolicy",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "eip712Domain",
        "inputs": [],
        "outputs": [{
            "name": "fields",
            "type": "bytes1",
            "internalType": "bytes1"
        }, {
            "name": "name",
            "type": "string",
            "internalType": "string"
        }, {
            "name": "version",
            "type": "string",
            "internalType": "string"
        }, {
            "name": "chainId",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "verifyingContract",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "salt",
            "type": "bytes32",
            "internalType": "bytes32"
        }, {
            "name": "extensions",
            "type": "uint256[]",
            "internalType": "uint256[]"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getHoldAmount",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "account",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getPolicy",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }],
        "outputs": [{
            "name": "",
            "type": "tuple",
            "internalType": "struct Policy",
            "components": [{
                "name": "escrowDuration",
                "type": "uint48",
                "internalType": "uint48"
            }, {
                "name": "active",
                "type": "bool",
                "internalType": "bool"
            }]
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getPolicyAgents",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }],
        "outputs": [{
            "name": "",
            "type": "address[]",
            "internalType": "address[]"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "hold",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "account",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "initialize",
        "inputs": [{
            "name": "deployer",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "isPolicyAgent",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "agent",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "bool",
            "internalType": "bool"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "maxDeposit",
        "inputs": [{
            "name": "",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "maxMint",
        "inputs": [{
            "name": "",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "maxRedeem",
        "inputs": [{
            "name": "owner",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "maxWithdraw",
        "inputs": [{
            "name": "owner",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "mint",
        "inputs": [{
            "name": "shares",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "receiver",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "name",
        "inputs": [],
        "outputs": [{
            "name": "",
            "type": "string",
            "internalType": "string"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "nonces",
        "inputs": [{
            "name": "owner",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "permit",
        "inputs": [{
            "name": "owner",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "spender",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "value",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "deadline",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "v",
            "type": "uint8",
            "internalType": "uint8"
        }, {
            "name": "r",
            "type": "bytes32",
            "internalType": "bytes32"
        }, {
            "name": "s",
            "type": "bytes32",
            "internalType": "bytes32"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "policyCount",
        "inputs": [],
        "outputs": [{
            "name": "",
            "type": "uint64",
            "internalType": "uint64"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "previewDeposit",
        "inputs": [{
            "name": "assets",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "previewMint",
        "inputs": [{
            "name": "shares",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "previewRedeem",
        "inputs": [{
            "name": "shares",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "previewWithdraw",
        "inputs": [{
            "name": "assets",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "redeem",
        "inputs": [{
            "name": "shares",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "receiver",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "owner",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "release",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "account",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "removePolicyAgent",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "agent",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "setMinBondedBalance",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "minBonded",
            "type": "uint128",
            "internalType": "uint128"
        }, {
            "name": "maxTopUpPerPeriod",
            "type": "uint128",
            "internalType": "uint128"
        }, {
            "name": "topUpPeriodDuration",
            "type": "uint32",
            "internalType": "uint32"
        }],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "symbol",
        "inputs": [],
        "outputs": [{
            "name": "",
            "type": "string",
            "internalType": "string"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "totalAssets",
        "inputs": [],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "totalSupply",
        "inputs": [],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "transfer",
        "inputs": [{
            "name": "to",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "value",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [{
            "name": "",
            "type": "bool",
            "internalType": "bool"
        }],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "transferFrom",
        "inputs": [{
            "name": "from",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "to",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "value",
            "type": "uint256",
            "internalType": "uint256"
        }],
                "outputs": [{
            "name": "",
            "type": "bool",
            "internalType": "bool"
        }],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "unbond",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "amount",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "newMinBalance",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "outputs": [{
            "name": "unbondBlock",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "unbondingCompleteBlock",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "account",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "withdraw",
        "inputs": [{
            "name": "assets",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "receiver",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "owner",
            "type": "address",
            "internalType": "address"
        }],
        "outputs": [{
            "name": "",
            "type": "uint256",
            "internalType": "uint256"
        }],
        "stateMutability": "nonpayable"
    },
    {
        "type": "event",
        "name": "AddPolicyAgent",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "indexed": True,
            "internalType": "uint64"
        }, {
            "name": "agent",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "AgentExecuteWithSponsor",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "indexed": True,
            "internalType": "uint64"
        }, {
            "name": "payor",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "agent",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "recipient",
            "type": "address",
            "indexed": False,
            "internalType": "address"
        }, {
            "name": "msgValue",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }, {
            "name": "gasLimit",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }, {
            "name": "actualPayorCost",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "AgentTransferFromBonded",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "indexed": True,
            "internalType": "uint64"
        }, {
            "name": "from",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "to",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "AgentUnbonded",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "indexed": True,
            "internalType": "uint64"
        }, {
            "name": "from",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "AgentWithdrawFromBonded",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "indexed": True,
            "internalType": "uint64"
        }, {
            "name": "from",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "to",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Approval",
        "inputs": [{
            "name": "owner",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "spender",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "value",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Bond",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "indexed": True,
            "internalType": "uint64"
        }, {
            "name": "account",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Claim",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "indexed": True,
            "internalType": "uint64"
        }, {
            "name": "account",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "CreatePolicy",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "indexed": True,
            "internalType": "uint64"
        }, {
            "name": "creator",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "escrowDuration",
            "type": "uint48",
            "indexed": False,
            "internalType": "uint48"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Deposit",
        "inputs": [{
            "name": "sender",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "owner",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "assets",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }, {
            "name": "shares",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "DisablePolicy",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "indexed": True,
            "internalType": "uint64"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "EIP712DomainChanged",
        "inputs": [],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Initialized",
        "inputs": [{
            "name": "version",
            "type": "uint64",
            "indexed": False,
            "internalType": "uint64"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "RemovePolicyAgent",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "indexed": True,
            "internalType": "uint64"
        }, {
            "name": "agent",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "SetTopUp",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "indexed": True,
            "internalType": "uint64"
        }, {
            "name": "account",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "minBonded",
            "type": "uint128",
            "indexed": False,
            "internalType": "uint128"
        }, {
            "name": "maxTopUpPerPeriod",
            "type": "uint128",
            "indexed": False,
            "internalType": "uint128"
        }, {
            "name": "topUpPeriodDuration",
            "type": "uint32",
            "indexed": False,
            "internalType": "uint32"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Transfer",
        "inputs": [{
            "name": "from",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "to",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "value",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Unbond",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "indexed": True,
            "internalType": "uint64"
        }, {
            "name": "account",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "amount",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }, {
            "name": "expectedUnbondBlock",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Withdraw",
        "inputs": [{
            "name": "sender",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "receiver",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "owner",
            "type": "address",
            "indexed": True,
            "internalType": "address"
        }, {
            "name": "assets",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }, {
            "name": "shares",
            "type": "uint256",
            "indexed": False,
            "internalType": "uint256"
        }],
        "anonymous": False
    },
    {
        "type": "error",
        "name": "AgentSelfUnbondingDisallowed",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "agent",
            "type": "address",
            "internalType": "address"
        }]
    },
    {
        "type": "error",
        "name": "ECDSAInvalidSignature",
        "inputs": []
    },
    {
        "type": "error",
        "name": "ECDSAInvalidSignatureLength",
        "inputs": [{
            "name": "length",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "ECDSAInvalidSignatureS",
        "inputs": [{
            "name": "s",
            "type": "bytes32",
            "internalType": "bytes32"
        }]
    },
    {
        "type": "error",
        "name": "ERC20InsufficientAllowance",
        "inputs": [{
            "name": "spender",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "allowance",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "needed",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "ERC20InsufficientBalance",
        "inputs": [{
            "name": "sender",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "balance",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "needed",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "ERC20InvalidApprover",
        "inputs": [{
            "name": "approver",
            "type": "address",
            "internalType": "address"
        }]
    },
    {
        "type": "error",
        "name": "ERC20InvalidReceiver",
        "inputs": [{
            "name": "receiver",
            "type": "address",
            "internalType": "address"
        }]
    },
    {
        "type": "error",
        "name": "ERC20InvalidSender",
        "inputs": [{
            "name": "sender",
            "type": "address",
            "internalType": "address"
        }]
    },
    {
        "type": "error",
        "name": "ERC20InvalidSpender",
        "inputs": [{
            "name": "spender",
            "type": "address",
            "internalType": "address"
        }]
    },
    {
        "type": "error",
        "name": "ERC2612ExpiredSignature",
        "inputs": [{
            "name": "deadline",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "ERC2612InvalidSigner",
        "inputs": [{
            "name": "signer",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "owner",
            "type": "address",
            "internalType": "address"
        }]
    },
    {
        "type": "error",
        "name": "ERC4626ExceededMaxDeposit",
        "inputs": [{
            "name": "receiver",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "assets",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "max",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "ERC4626ExceededMaxMint",
        "inputs": [{
            "name": "receiver",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "shares",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "max",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "ERC4626ExceededMaxRedeem",
        "inputs": [{
            "name": "owner",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "shares",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "max",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "ERC4626ExceededMaxWithdraw",
        "inputs": [{
            "name": "owner",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "assets",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "max",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "ForwardingError",
        "inputs": [{
            "name": "nestedError",
            "type": "bytes4",
            "internalType": "bytes4"
        }]
    },
    {
        "type": "error",
        "name": "InsufficientBondedForHold",
        "inputs": [{
            "name": "bonded",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "holdRequested",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "InsufficientFunds",
        "inputs": [{
            "name": "bonded",
            "type": "uint128",
            "internalType": "uint128"
        }, {
            "name": "unbonding",
            "type": "uint128",
            "internalType": "uint128"
        }, {
            "name": "held",
            "type": "uint128",
            "internalType": "uint128"
        }, {
            "name": "requested",
            "type": "uint128",
            "internalType": "uint128"
        }]
    },
    {
        "type": "error",
        "name": "InsufficientNativeTokenSent",
        "inputs": []
    },
    {
        "type": "error",
        "name": "InsufficientUnbondedBalance",
        "inputs": [{
            "name": "available",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "requested",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "InsufficientUnbondingBalance",
        "inputs": [{
            "name": "available",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "requested",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "InsufficientUnheldBondedBalance",
        "inputs": [{
            "name": "bonded",
            "type": "uint128",
            "internalType": "uint128"
        }, {
            "name": "held",
            "type": "uint128",
            "internalType": "uint128"
        }, {
            "name": "requested",
            "type": "uint128",
            "internalType": "uint128"
        }]
    },
    {
        "type": "error",
        "name": "InvalidAccountNonce",
        "inputs": [{
            "name": "account",
            "type": "address",
            "internalType": "address"
        }, {
            "name": "currentNonce",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "InvalidInitialization",
        "inputs": []
    },
    {
        "type": "error",
        "name": "MsgDotValueExceedsMsgValueArg",
        "inputs": [{
            "name": "msgDotValue",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "msgValueArg",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "MsgGasLimitTooLow",
        "inputs": [{
            "name": "gasLeft",
            "type": "uint256",
            "internalType": "uint256"
        }, {
            "name": "gasLimit",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "NotInitializing",
        "inputs": []
    },
    {
        "type": "error",
        "name": "NotPolicyAgent",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "caller",
            "type": "address",
            "internalType": "address"
        }]
    },
    {
        "type": "error",
        "name": "PolicyAgentAlreadyExists",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "agent",
            "type": "address",
            "internalType": "address"
        }]
    },
    {
        "type": "error",
        "name": "PolicyAgentNotFound",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }, {
            "name": "agent",
            "type": "address",
            "internalType": "address"
        }]
    },
    {
        "type": "error",
        "name": "PolicyInactive",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }]
    },
    {
        "type": "error",
        "name": "PolicyNeedsAtLeastOneAgent",
        "inputs": [{
            "name": "policyID",
            "type": "uint64",
            "internalType": "uint64"
        }]
    },
    {
        "type": "error",
        "name": "SafeCastOverflowedUintDowncast",
        "inputs": [{
            "name": "bits",
            "type": "uint8",
            "internalType": "uint8"
        }, {
            "name": "value",
            "type": "uint256",
            "internalType": "uint256"
        }]
    },
    {
        "type": "error",
        "name": "TopUpPeriodDurationTooShort",
        "inputs": [{
            "name": "requestedPeriodDuration",
            "type": "uint32",
            "internalType": "uint32"
        }, {
            "name": "minPeriodDuration",
            "type": "uint32",
            "internalType": "uint32"
        }]
    },
    {
        "type": "error",
        "name": "UnbondingPeriodIncomplete",
        "inputs": [{
            "name": "unbondingCompleteBlock",
            "type": "uint256",
            "internalType": "uint256"
        }]
    }
]