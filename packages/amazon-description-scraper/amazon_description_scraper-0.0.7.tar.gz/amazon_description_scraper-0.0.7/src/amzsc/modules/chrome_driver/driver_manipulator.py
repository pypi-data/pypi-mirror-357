import selenium.common.exceptions as se
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from typing import Any, Callable, Tuple, Union
from amzsc.utils import CustomTypes


CONDITION_TYPE = Callable[
    [Tuple[str, str]], Callable[[WebDriver], Union[WebElement, bool]]
]


class ChromeManipulator:
    def __init__(self, driver: CustomTypes.DRIVER_TYPE) -> None:
        self.driver = driver

    def __str__(self) -> str:
        return "DriverManipulator"

    def get(self, url: str) -> None:
        self.driver.get(url)

    def refresh(self) -> None:
        self.driver.refresh()

    def quit(self) -> None:
        self.driver.quit()

    def wait(self, timeout: int = 10) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout)

    def error_handler(self, func: Callable, *args, **kwargs) -> Any:
        target = kwargs.get("target")
        try:
            return func(*args)
        except se.TimeoutException:
            raise TimeoutError(f"Timeout when accessing: '{target}'")
        except se.NoSuchElementException:
            raise KeyError(f"No such element: '{target}'")
        except se.ElementNotInteractableException:
            raise KeyError(f"Element not interactable: '{target}'")
        except se.ElementNotVisibleException:
            raise KeyError(f"Element not visible: '{target}'")
        except Exception as e:
            raise Exception(f"General error '{target}': {str(e)}")

    def get_element(
        self,
        strategy: str,
        target: str,
        condition: CONDITION_TYPE = EC.visibility_of_element_located,
        timeout: int = 10,
    ) -> WebElement:
        def foo():
            return self.wait(timeout).until(condition((strategy, target)))

        return self.error_handler(foo, target=target)

    def click_button(
        self,
        strategy: str,
        target: str,
        condition: CONDITION_TYPE = EC.element_to_be_clickable,
        timeout: int = 10,
    ) -> None:
        def foo():
            self.get_element(strategy, target, condition, timeout).click()

        return self.error_handler(foo, target=target)

    def force_click_button(
        self,
        strategy: str,
        target: str,
        condition: CONDITION_TYPE = EC.presence_of_element_located,
        timeout: int = 10,
    ):
        def func():
            button = self.get_element(strategy, target, condition, timeout)
            self.driver.execute_script("arguments[0].click();", button)

        return self.error_handler(func, target=target)

    def send_keys(
        self,
        strategy: str,
        target: str,
        keys_to_send: str,
        condition: CONDITION_TYPE = EC.presence_of_element_located,
        timeout: int = 10,
    ) -> None:
        def foo():
            elm = self.get_element(strategy, target, condition, timeout)
            try:
                elm.clear()
            except:
                pass
            elm.send_keys(keys_to_send)

        return self.error_handler(foo, target=target)

    def select_from_dropdown(
        self,
        strategy: str,
        dropdown_elmement: str,
        target: str,
        condition: CONDITION_TYPE = EC.presence_of_element_located,
        timeout: int = 10,
    ) -> None:
        def foo():
            element = self.get_element(strategy, dropdown_elmement, condition, timeout)
            select = Select(element)
            select.select_by_visible_text(target)

        return self.error_handler(foo, target=target)
