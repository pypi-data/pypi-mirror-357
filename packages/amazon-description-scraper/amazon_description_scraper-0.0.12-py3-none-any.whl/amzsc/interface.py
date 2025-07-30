import logging
import pandas as pd

from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
from typing import Dict, List, Optional

from amzsc.modules.chrome_driver import AmazonDriver, ChromeDriverConfig
from amzsc.modules.proxy import get_proxy
from amzsc.utils import Constants
from amzsc.utils.file_worker import write_to_json
from amzsc.utils.marketplace import get_zone


logger = logging.getLogger(__name__)


def scrape_one(client: AmazonDriver, marketplace: str, asin: str) -> Dict[str, str]:
    data = {"asin": asin, "marketplace": marketplace}
    zone = get_zone(marketplace)
    url = f"https://www.amazon.{zone}/dp/{asin}"
    client.get(url)

    product_overview = client.get_product_overview()
    if product_overview:
        data = data | product_overview

    product_specs = client.get_product_specs()
    if product_specs:
        data = data | product_specs

    product_micro = client.get_product_micro()
    if product_micro:
        data = data | product_micro

    return data


def scrape_all(
    marketplaces: List[str],
    asins: List[str],
    thread_id: int,
    thread_count: int = 10,
    proxy_key: Optional[str] = None,
    headless: bool = True,
    is_remote: bool = False,
    remote_url: Optional[str] = None,
    jsonl_output_path: Optional[str] = None,
) -> List[Dict[str, str]]:
    client = None
    data: List[Dict[str, str]] = []
    try:
        proxy = get_proxy(proxy_key) if proxy_key else None
        position = ChromeDriverConfig.get_driver_position(thread_id, thread_count)
        options = ChromeDriverConfig.get_options(
            proxy=proxy,
            position=position,
            user_agent=UserAgent().random,
            headless=headless,
        )
        if is_remote:
            driver = ChromeDriverConfig.get_remote_driver(options, remote_url)
        else:
            driver = ChromeDriverConfig.get_chrome_driver(options)
        client = AmazonDriver(driver)
        for i in range(len(asins)):
            asin = asins[i]
            marketplace = marketplaces[i]
            row = scrape_one(client, marketplace, asin)
            if jsonl_output_path:
                write_to_json(jsonl_output_path, row)
            data.append(row)
    except Exception as e:
        logger.error(str(e))
    finally:
        if client is not None:
            client.quit()
        return data


class AmazonScraper:
    def __init__(
        self,
        proxy_key: Optional[str] = None,
        headless: bool = True,
        is_remote: bool = False,
        remote_url: Optional[str] = None,
        jsonl_output_path: Optional[str] = None,
        logging_level: str = "DEBUG",
    ) -> None:
        self.__proxy_key = proxy_key
        self.headless = headless
        self.is_remote = is_remote
        self.remote_url = remote_url

        # Set up output options
        self.jsonl_output_path = jsonl_output_path

        # Configure logging
        levels = Constants.LOGGING_LEVELS
        if logging_level not in levels:
            raise TypeError("logging_level must be one of: " + ", ".join(levels))
        logger.setLevel(logging_level)

    @property
    def proxy_key(self) -> Optional[str]:
        return self.__proxy_key

    def scrape(
        self,
        asins: List[str],
        marketplaces: Optional[List[str]] = None,
        marketplace: Optional[str] = None,
        thread_count: int = 10,
    ) -> pd.DataFrame:
        if len(asins) == 0:
            raise ValueError("asins must not be an empty list")
        if marketplace is not None and marketplaces is None:
            marketplaces = [marketplace] * len(asins)
        if marketplaces is None or len(marketplaces) != len(asins):
            raise ValueError("Invalid marketplaces array length")
        if thread_count <= 0:
            raise ValueError("thread_count must be a positive integer")

        chunk_size = len(asins) // thread_count + (len(asins) % thread_count > 0)
        chunks = [
            (marketplaces[i : i + chunk_size], asins[i : i + chunk_size])
            for i in range(0, len(asins), chunk_size)
        ]
        args = [
            self.proxy_key,
            self.headless,
            self.is_remote,
            self.remote_url,
            self.jsonl_output_path,
        ]
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = [
                executor.submit(
                    scrape_all, chunk[0], chunk[1], thread_id + 1, thread_count, *args
                )
                for thread_id, chunk in enumerate(chunks)
            ]
            results = []
            for future in futures:
                results.extend(future.result())
            df_output = pd.DataFrame(results)
        return df_output
