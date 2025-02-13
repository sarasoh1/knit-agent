from typing import List, Optional
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import re
from models.helpers.download_location import DownloadLocation
from models.helpers.gauge import Gauge
from models.helpers.ratings import Ratings
from models.helpers.pattern_features import PatternAttribute, PatternCategories


class Pattern(BaseModel):
    """
    A pattern is a JSON response from Ravelry's API
    """

    id: int
    name: str
    permalink: str
    craft: str
    download_location: DownloadLocation
    ratings: Ratings
    gauge: Gauge
    pattern_attributes: Optional[List[PatternAttribute]]
    pattern_categories: Optional[List[PatternCategories]]

    def retrieve_pattern_url(self) -> tuple[str, str]:
        """
        Finds the pattern and returns the link to the file and the extension
        """
        if not self.download_location.is_from_ravelry():
            # First, do a check if the download link is already the file
            is_file = self.download_location.is_url_file()
            if is_file:
                return "pdf", self.download_location.url
            else:
                link_response = requests.get(self.download_location.url, timeout=20)
                soup = BeautifulSoup(link_response.text, "html.parser")
                # Try to find a pdf file link
                links = soup.find_all(
                    "a",
                    attrs={"href": re.compile(r"^https:\/\/cdn.*\.pdf", re.IGNORECASE)},
                )

                if not links or len(links) == 0:
                    return "html", self.download_location.url
                else:
                    return "pdf", links[0].get("href")
        else:
            response = requests.get(self.download_location.url, timeout=20)
            soup = BeautifulSoup(response.text, "html.parser")
            # print("soup:", soup)
            links = soup.find_all(
                "a", attrs={"href": re.compile(r"^https:\/\/.*\.pdf", re.IGNORECASE)}
            )
            links2 = soup.find_all(
                "a", attrs={"href": re.compile(r"^http:\/\/.*\.pdf", re.IGNORECASE)}
            )
            links = links + links2

            if not links or len(links) == 0:
                return "pdf", self.download_location.url
            else:
                return "pdf", links[0].get("href")
