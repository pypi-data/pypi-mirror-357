import time

import gruel
import loggi
import quickpool
from seleniumuser.seleniumuser import User
from typing_extensions import Self

from rebay.geckodriver_installer import GeckodriverInstaller


class Browser:
    """
    Singleton class for making requests through a selenium browser instance.
    """

    user: User
    instance: Self

    def __new__(cls) -> Self:
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
            cls._install_driver()
            cls.user = User(headless=True)
        return cls.instance

    @classmethod
    def _install_driver(cls) -> None:
        """
        Install 'geckodriver' if it can't be found.
        """
        installer = GeckodriverInstaller()
        if not installer.is_installed():
            quickpool.update_and_wait(installer.install, "Installing geckodriver...")
            print("Geckodriver successfully installed.")

    @classmethod
    def get(cls, url: str, logger: loggi.Logger) -> gruel.Response | None:
        """
        Request the resource at the given url.

        Args:
            url (str): The url to request.
            logger (loggi.Logger): A logger to use.

        Returns:
            gruel.Response | None: Returns `None` if the request was unsuccessful.
        """
        # ensure the instance has been created
        c = cls()
        logger.info(f"Sending a request to '{url}'.")
        try:
            cls.user.get(url)
            while "splashui" in cls.user.current_url():
                logger.debug("Attempting to bypass captcha...")
                time.sleep(1)
        except Exception as e:
            logger.exception(f"Failed to get page at `{url}`.")
            return None
        response = gruel.requests.SeleniumResponse.from_selenium_user(cls.user)
        response.status_code = 200
        return response

    @classmethod
    def close(cls) -> None:
        """
        Close down the browser.
        """
        if hasattr(cls, "user"):
            cls.user.close_browser()
