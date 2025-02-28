from loguru import logger
import primp
import random
import asyncio

from src.model.magiceden.instance import MagicEden
from src.model.monadking_mint.instance import Monadking
from src.model.demask_mint.instance import Demask
from src.model.lilchogstars_mint.instance import Lilchogstars
from src.model.kintsu.instance import Kintsu
from src.model.orbiter.instance import Orbiter
from src.model.accountable.instance import Accountable
from src.model.shmonad.instance import Shmonad
from src.model.gaszip.instance import Gaszip
from src.model.monadverse_mint.instance import MonadverseMint
from src.model.bima.instance import Bima
from src.model.owlto.instance import Owlto
from src.model.magma.instance import Magma
from src.model.apriori import Apriori
from src.model.monad_xyz.instance import MonadXYZ
from src.model.nad_domains.instance import NadDomains
from src.utils.client import create_client
from src.utils.config import Config
from src.model.help.stats import WalletStats


class Start:
    def __init__(
        self,
        account_index: int,
        proxy: str,
        private_key: str,
        discord_token: str,
        email: str,
        config: Config,
    ):
        self.account_index = account_index
        self.proxy = proxy
        self.private_key = private_key
        self.discord_token = discord_token
        self.email = email
        self.config = config

        self.session: primp.AsyncClient | None = None

    async def initialize(self):
        try:
            self.session = await create_client(self.proxy)

            return True
        except Exception as e:
            logger.error(f"[{self.account_index}] | Error: {e}")
            return False

    async def flow(self):
        try:
            monad = MonadXYZ(
                self.account_index,
                self.proxy,
                self.private_key,
                self.discord_token,
                self.config,
                self.session,
            )

            if "farm_faucet" in self.config.FLOW.TASKS:
                await monad.faucet()
                return True

            # Заранее определяем все задачи
            planned_tasks = []
            task_plan_msg = []
            for i, task_item in enumerate(self.config.FLOW.TASKS, 1):
                if isinstance(task_item, list):
                    selected_task = random.choice(task_item)
                    planned_tasks.append((i, selected_task, task_item))
                    task_plan_msg.append(f"{i}. {selected_task}")
                else:
                    planned_tasks.append((i, task_item, None))
                    task_plan_msg.append(f"{i}. {task_item}")

            # Выводим план выполнения одним сообщением
            logger.info(
                f"[{self.account_index}] Task execution plan: {' | '.join(task_plan_msg)}"
            )

            # Выполняем задачи по плану
            for _, task, _ in planned_tasks:
                task = task.lower()
                # Выполняем выбранную задачу
                if task == "faucet":
                    if self.config.FAUCET.MONAD_XYZ:
                        await monad.faucet()

                elif task == "swaps":
                    await monad.swaps(type="swaps")

                elif task == "ambient":
                    await monad.swaps(type="ambient")

                elif task == "bean":
                    await monad.swaps(type="bean")
                
                elif task == "izumi":
                    await monad.swaps(type="izumi")

                elif task == "collect_all_to_monad":
                    await monad.swaps(type="collect_all_to_monad")

                elif task == "gaszip":
                    gaszip = Gaszip(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                    )
                    await gaszip.refuel()

                elif task == "apriori":
                    apriori = Apriori(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await apriori.stake_mon()

                elif task == "magma":
                    magma = Magma(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await magma.stake_mon()

                elif task == "owlto":
                    owlto = Owlto(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await owlto.deploy_contract()

                elif task == "bima":
                    bima = Bima(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await bima.get_faucet_tokens()
                    await self.sleep("bima_faucet")

                    if self.config.BIMA.LEND:
                        await bima.lend()

                elif task == "monadverse_mint":
                    monadverse_mint = MonadverseMint(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await monadverse_mint.mint()

                elif task == "shmonad":
                    shmonad = Shmonad(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await shmonad.swaps()

                elif task == "accountable":
                    accountable = Accountable(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await accountable.mint()

                elif task == "orbiter":
                    orbiter = Orbiter(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await orbiter.bridge()

                elif task == "logs":
                    wallet_stats = WalletStats(self.config)
                    await wallet_stats.get_wallet_stats(
                        self.private_key, self.account_index
                    )

                elif task == "nad_domains":
                    nad_domains = NadDomains(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await nad_domains.register_random_domain()

                elif task == "kintsu":
                    kintsu = Kintsu(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await kintsu.stake_mon()

                elif task == "lilchogstars":
                    lilchogstars = Lilchogstars(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await lilchogstars.mint()

                elif task == "demask":
                    demask = Demask(
                        self.account_index,
                        self.proxy,
                        self.private_key,
                        self.config,
                        self.session,
                    )
                    await demask.mint()

                elif task == "monadking":
                    monadking = Monadking(
                        self.account_index,
                        self.private_key,
                        self.config,
                    )
                    await monadking.mint()

                elif task == "monadking_unlocked":
                    monadking_unlocked = Monadking(
                        self.account_index,
                        self.private_key,
                        self.config,
                    )
                    await monadking_unlocked.mint_unlocked()
                
                elif task == "magiceden":
                    magiceden = MagicEden(
                        self.account_index,
                        self.config,
                        self.private_key,
                        self.session,
                    )
                    await magiceden.mint()
                
                await self.sleep(task)

            return True
        except Exception as e:
            # import traceback
            # traceback.print_exc()
            logger.error(f"[{self.account_index}] | Error: {e}")
            return False

    async def sleep(self, task_name: str):
        """Делает рандомную паузу между действиями"""
        pause = random.randint(
            self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[0],
            self.config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACTIONS[1],
        )
        logger.info(
            f"[{self.account_index}] Sleeping {pause} seconds after {task_name}"
        )
        await asyncio.sleep(pause)
