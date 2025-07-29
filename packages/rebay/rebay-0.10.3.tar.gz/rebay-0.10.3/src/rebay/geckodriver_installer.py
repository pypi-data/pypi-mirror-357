import os
import platform
import tarfile
import zipfile

import gruel
import loggi
from bs4 import BeautifulSoup, Tag
from pathier import Pathier


class TagNotFoundException(Exception):
    def __init__(self, description: str):
        """
        Creates an exception with a formatted message that includes `description`.
        i.e. "Could not find tag for {description}."

        Args:
            description (str): A string the can be used to identify what element was being searched for when this exception was thrown.

        Returns:
            TagNotFoundException
        """
        super().__init__(f"Could not find tag for {description}.")


class FailedToInstallGeckodriverException(Exception):
    def __init__(self, message: str) -> None:
        """
        Creates an exception to be raised when geckodriver installation failed.

        Args:
            message (str): The reason the install failed.
        """
        super().__init__(message)


class GeckodriverInstaller:
    _gh_url = gruel.Url("https://github.com/mozilla/geckodriver/releases")
    _logger = loggi.getLogger("geckodriver_installer", Pathier.cwd() / "logs")

    def __init__(self):
        self._release_version: str

    @property
    def release_version(self) -> str:
        """
        Returns:
            str: The release version of geckodriver that is being installed.
        """
        return self._release_version

    def is_in_PATH(self) -> bool:
        """
        Returns:
            bool: Whether 'geckodriver' was found in the system's PATH variable.
        """
        sep = ";" if "win" in platform.system().lower() else ":"
        paths = [Pathier(path) for path in os.environ["PATH"].split(sep)]
        for path in paths:
            try:
                if len(
                    list(path.glob("*geckodriver"))
                    + list(path.glob("*geckodriver.exe"))
                ):
                    return True
            except PermissionError:
                pass
        return False

    def is_in_cwd(self) -> bool:
        """
        Returns:
            bool: Whether 'geckodriver' was found in the current directory.
        """
        path = Pathier.cwd()
        return (
            len(list(path.glob("*geckodriver")) + list(path.glob("*geckodriver.exe")))
            > 0
        )

    def is_installed(self) -> bool:
        """
        Returns:
            bool: Whether 'geckodriver' is found in the current directory or system PATH.
        """
        return self.is_in_cwd() or self.is_in_PATH()

    def _get_release_download_links(self, soup: BeautifulSoup) -> list[gruel.Url]:
        """
        Finds the download links for the most recent release of geckodriver.

        Args:
            soup (BeautifulSoup): A `BeautifulSoup` instance of the geckodriver github releases page.

        Raises:
            TagNotFoundException: If the version or parent info tags can't be found.

        Returns:
            list[gruel.Url]: A list of geckodriver download urls for various platforms.
        """
        release = soup.find("a", class_="Link--primary Link")
        if not isinstance(release, Tag):
            raise TagNotFoundException("most recent release")
        self._release_version = release.text

        infobox = release.find_parent(
            "div", {"class": "Box", "data-view-component": "true"}
        )
        if not isinstance(infobox, Tag):
            raise TagNotFoundException("parent box of release")

        assets = infobox.find_all("li", {"data-view-component": "true"})
        asset_links: list[gruel.Url] = []
        for asset in assets:
            a = asset.find("a", {"data-view-component": "true"})
            if isinstance(a, Tag):
                url = gruel.Url("")
                url.scheme = self._gh_url.scheme
                url.netloc = self._gh_url.netloc
                url.path = str(a.get("href"))
                if "archive/refs" not in url.path:
                    asset_links.append(url)
        return asset_links

    def _get_download_link_for_system(self, urls: list[gruel.Url]) -> gruel.Url | None:
        """
        Tries to match one of the asset urls to the current machine.

        Args:
            urls (list[gruel.Url]): The urls from the "assets" section of a geckodriver release.

        Returns:
              gruel.Url | None: A url if matching was successful, `None` if not.
        """
        os = platform.system().lower()
        machine = platform.machine().lower()
        arch = platform.architecture()
        for url in urls:
            if ".asc" in url.address:
                continue
            if os == "linux" and "linux" in url.path:
                if machine == "x86_64" and "linux64" in url.path:
                    return url
                if "arm" in machine and "linux-aarch64" in url.path:
                    return url
                if arch[0] == "32bit" and "linux32" in url.path:
                    return url
            if os == "darwin" and "macos" in url.path:
                if "arm" in machine and "aarch64" in url.path:
                    return url
                if "arm" not in machine and "macos.tar" in url.path:
                    return url
            if "win" in os and "win" in url.path:
                if "arm" in machine and "aarch64" in url.path:
                    return url
                if "amd" in machine and "win32.zip" in url.path:
                    return url
        return None

    def _extract(self, path: Pathier) -> None:
        """
        Extract the contents of the provided archive.

        Only handles '.zip' or '.tar.gz'.

        Args:
            path (Pathier): The path to the archive.

        Raises:
            NotImplementedError: If the file is something other than '.zip' or '.tar.gz'.
        """
        if path.name.endswith(".zip"):
            f = zipfile.ZipFile(path, "r")
        elif path.name.endswith(".tar.gz"):
            f = tarfile.open(path, "r:gz")
        else:
            raise NotImplementedError()
        f.extractall()
        f.close()

    def _download_driver(self, url: gruel.Url) -> None:
        """
        Downloads and extracts a file.

        Args:
            url (gruel.Url): The url of the file.
        """
        archive_path = Pathier.cwd() / url.path[url.path.rfind("/") + 1 :]
        response = gruel.request(url.address, logger=self._logger)
        response.raise_for_status()
        archive_path.write_bytes(response.content)
        self._extract(archive_path)

    def install(self) -> None:
        """
        Download the most recent version of geckodriver that's compatible with this system.

        Raises:
            TagNotFoundException: If the install fails because version or parent info Tags can't be found when looking for download links.

            FailedToInstallGeckodriverException: If the installation fails for another reason.

        """
        response = gruel.request(self._gh_url.address)
        try:
            response.raise_for_status()
        except Exception as e:
            message = f"Releases page returned a '{response.status_code}' status"
            self._logger.error(message)
            raise FailedToInstallGeckodriverException(message)

        soup = response.get_soup()
        release_urls = self._get_release_download_links(soup)
        download_url = self._get_download_link_for_system(release_urls)
        if not download_url:
            message = "Couldn't match a download url to this system."
            self._logger.error(message)
            raise FailedToInstallGeckodriverException(message)
        try:
            self._download_driver(download_url)
        except Exception as e:
            message = "Downloading geckodriver file failed."
            self._logger.exception(message)
            raise FailedToInstallGeckodriverException(f"{message}\n{e}")
