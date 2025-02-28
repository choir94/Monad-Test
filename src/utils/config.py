from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import yaml
from pathlib import Path
import asyncio


@dataclass
class SettingsConfig:
    THREADS: int
    ATTEMPTS: int
    ACCOUNTS_RANGE: Tuple[int, int]
    EXACT_ACCOUNTS_TO_USE: List[int]
    PAUSE_BETWEEN_ATTEMPTS: Tuple[int, int]
    PAUSE_BETWEEN_SWAPS: Tuple[int, int]
    RANDOM_PAUSE_BETWEEN_ACCOUNTS: Tuple[int, int]
    RANDOM_PAUSE_BETWEEN_ACTIONS: Tuple[int, int]
    BROWSER_PAUSE_MULTIPLIER: float
    RANDOM_INITIALIZATION_PAUSE: Tuple[int, int]


@dataclass
class FlowConfig:
    TASKS: List[str]
    NUMBER_OF_SWAPS: Tuple[int, int]
    PERCENT_OF_BALANCE_TO_SWAP: Tuple[int, int]


@dataclass
class AprioriConfig:
    AMOUNT_TO_STAKE: Tuple[float, float]


@dataclass
class MagmaConfig:
    AMOUNT_TO_STAKE: Tuple[float, float]


@dataclass
class KintsuConfig:
    AMOUNT_TO_STAKE: Tuple[float, float]


@dataclass
class BimaConfig:
    LEND: bool
    PERCENT_OF_BALANCE_TO_LEND: Tuple[int, int]


@dataclass
class FaucetConfig:
    MONAD_XYZ: bool
    CAPSOLVER_API_KEY: str
    PROXY_FOR_CAPTCHA: str


@dataclass
class WalletInfo:
    account_index: int
    private_key: str
    address: str
    balance: float
    transactions: int


@dataclass
class WalletsConfig:
    wallets: List[WalletInfo] = field(default_factory=list)


@dataclass
class GaszipConfig:
    NETWORKS_TO_REFUEL_FROM: List[str]
    AMOUNT_TO_REFUEL: Tuple[float, float]
    MINIMUM_BALANCE_TO_REFUEL: float
    WAIT_FOR_FUNDS_TO_ARRIVE: bool
    MAX_WAIT_TIME: int


@dataclass
class ShmonadConfig:
    PERCENT_OF_BALANCE_TO_SWAP: Tuple[int, int]
    BUY_AND_STAKE_SHMON: bool
    UNSTAKE_AND_SELL_SHMON: bool


@dataclass
class AccountableConfig:
    NFT_PER_ACCOUNT_LIMIT: int


@dataclass
class OrbiterConfig:
    AMOUNT_TO_BRIDGE: Tuple[float, float]
    BRIDGE_ALL: bool
    WAIT_FOR_FUNDS_TO_ARRIVE: bool
    MAX_WAIT_TIME: int


@dataclass
class DisperseConfig:
    MIN_BALANCE_FOR_DISPERSE: Tuple[float, float]


@dataclass
class LilchogstarsConfig:
    MAX_AMOUNT_FOR_EACH_ACCOUNT: Tuple[int, int]

@dataclass
class DemaskConfig:
    MAX_AMOUNT_FOR_EACH_ACCOUNT: Tuple[int, int]


@dataclass
class MonadkingConfig:
    MAX_AMOUNT_FOR_EACH_ACCOUNT: Tuple[int, int]

@dataclass
class MagicEdenConfig:
    NFT_CONTRACTS: List[str]


@dataclass
class Config:
    SETTINGS: SettingsConfig
    FLOW: FlowConfig
    APRIORI: AprioriConfig
    MAGMA: MagmaConfig
    KINTSU: KintsuConfig
    BIMA: BimaConfig
    FAUCET: FaucetConfig
    GASZIP: GaszipConfig
    SHMONAD: ShmonadConfig
    ACCOUNTABLE: AccountableConfig
    ORBITER: OrbiterConfig
    DISPERSE: DisperseConfig
    LILCHOGSTARS: LilchogstarsConfig
    DEMASK: DemaskConfig
    MONADKING: MonadkingConfig
    MAGICEDEN: MagicEdenConfig
    WALLETS: WalletsConfig = field(default_factory=WalletsConfig)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    @classmethod
    def load(cls, path: str = "config.yaml") -> "Config":
        """Load configuration from yaml file"""
        with open(path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        return cls(
            SETTINGS=SettingsConfig(
                THREADS=data["SETTINGS"]["THREADS"],
                ATTEMPTS=data["SETTINGS"]["ATTEMPTS"],
                ACCOUNTS_RANGE=tuple(data["SETTINGS"]["ACCOUNTS_RANGE"]),
                EXACT_ACCOUNTS_TO_USE=data["SETTINGS"]["EXACT_ACCOUNTS_TO_USE"],
                PAUSE_BETWEEN_ATTEMPTS=tuple(
                    data["SETTINGS"]["PAUSE_BETWEEN_ATTEMPTS"]
                ),
                PAUSE_BETWEEN_SWAPS=tuple(data["SETTINGS"]["PAUSE_BETWEEN_SWAPS"]),
                RANDOM_PAUSE_BETWEEN_ACCOUNTS=tuple(
                    data["SETTINGS"]["RANDOM_PAUSE_BETWEEN_ACCOUNTS"]
                ),
                RANDOM_PAUSE_BETWEEN_ACTIONS=tuple(
                    data["SETTINGS"]["RANDOM_PAUSE_BETWEEN_ACTIONS"]
                ),
                RANDOM_INITIALIZATION_PAUSE=tuple(
                    data["SETTINGS"]["RANDOM_INITIALIZATION_PAUSE"]
                ),
                BROWSER_PAUSE_MULTIPLIER=data["SETTINGS"]["BROWSER_PAUSE_MULTIPLIER"],
            ),
            FLOW=FlowConfig(
                TASKS=data["FLOW"]["TASKS"],
                NUMBER_OF_SWAPS=tuple(data["FLOW"]["NUMBER_OF_SWAPS"]),
                PERCENT_OF_BALANCE_TO_SWAP=tuple(
                    data["FLOW"]["PERCENT_OF_BALANCE_TO_SWAP"]
                ),
            ),
            APRIORI=AprioriConfig(
                AMOUNT_TO_STAKE=tuple(data["APRIORI"]["AMOUNT_TO_STAKE"]),
            ),
            MAGMA=MagmaConfig(
                AMOUNT_TO_STAKE=tuple(data["MAGMA"]["AMOUNT_TO_STAKE"]),
            ),
            KINTSU=KintsuConfig(
                AMOUNT_TO_STAKE=tuple(data["KINTSU"]["AMOUNT_TO_STAKE"]),
            ),
            BIMA=BimaConfig(
                LEND=data["BIMA"]["LEND"],
                PERCENT_OF_BALANCE_TO_LEND=tuple(
                    data["BIMA"]["PERCENT_OF_BALANCE_TO_LEND"]
                ),
            ),
            FAUCET=FaucetConfig(
                MONAD_XYZ=data["FAUCET"]["MONAD_XYZ"],
                CAPSOLVER_API_KEY=data["FAUCET"]["CAPSOLVER_API_KEY"],
                PROXY_FOR_CAPTCHA=data["FAUCET"]["PROXY_FOR_CAPTCHA"],
            ),
            GASZIP=GaszipConfig(
                NETWORKS_TO_REFUEL_FROM=data["GASZIP"]["NETWORKS_TO_REFUEL_FROM"],
                AMOUNT_TO_REFUEL=tuple(data["GASZIP"]["AMOUNT_TO_REFUEL"]),
                MINIMUM_BALANCE_TO_REFUEL=data["GASZIP"]["MINIMUM_BALANCE_TO_REFUEL"],
                WAIT_FOR_FUNDS_TO_ARRIVE=data["GASZIP"]["WAIT_FOR_FUNDS_TO_ARRIVE"],
                MAX_WAIT_TIME=data["GASZIP"]["MAX_WAIT_TIME"],
            ),
            SHMONAD=ShmonadConfig(
                PERCENT_OF_BALANCE_TO_SWAP=tuple(
                    data["SHMONAD"]["PERCENT_OF_BALANCE_TO_SWAP"]
                ),
                BUY_AND_STAKE_SHMON=data["SHMONAD"]["BUY_AND_STAKE_SHMON"],
                UNSTAKE_AND_SELL_SHMON=data["SHMONAD"]["UNSTAKE_AND_SELL_SHMON"],
            ),
            ACCOUNTABLE=AccountableConfig(
                NFT_PER_ACCOUNT_LIMIT=data["ACCOUNTABLE"]["NFT_PER_ACCOUNT_LIMIT"],
            ),
            ORBITER=OrbiterConfig(
                AMOUNT_TO_BRIDGE=tuple(data["ORBITER"]["AMOUNT_TO_BRIDGE"]),
                BRIDGE_ALL=data["ORBITER"]["BRIDGE_ALL"],
                WAIT_FOR_FUNDS_TO_ARRIVE=data["ORBITER"]["WAIT_FOR_FUNDS_TO_ARRIVE"],
                MAX_WAIT_TIME=data["ORBITER"]["MAX_WAIT_TIME"],
            ),
            DISPERSE=DisperseConfig(
                MIN_BALANCE_FOR_DISPERSE=tuple(
                    data["DISPERSE"]["MIN_BALANCE_FOR_DISPERSE"]
                ),
            ),
            LILCHOGSTARS=LilchogstarsConfig(
                MAX_AMOUNT_FOR_EACH_ACCOUNT=tuple(
                    data["LILCHOGSTARS"]["MAX_AMOUNT_FOR_EACH_ACCOUNT"]
                ),
            ),
            DEMASK=DemaskConfig(
                MAX_AMOUNT_FOR_EACH_ACCOUNT=tuple(
                    data["DEMASK"]["MAX_AMOUNT_FOR_EACH_ACCOUNT"]
                ),
            ),
            MONADKING=MonadkingConfig(
                MAX_AMOUNT_FOR_EACH_ACCOUNT=tuple(
                    data["MONADKING"]["MAX_AMOUNT_FOR_EACH_ACCOUNT"]
                ),
            ),
            MAGICEDEN=MagicEdenConfig(
                NFT_CONTRACTS=data["MAGICEDEN"]["NFT_CONTRACTS"],
            ),
        )


# Singleton pattern
def get_config() -> Config:
    """Get configuration singleton"""
    if not hasattr(get_config, "_config"):
        get_config._config = Config.load()
    return get_config._config
