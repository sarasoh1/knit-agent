from pydantic import BaseModel


class DownloadLocation(BaseModel):
    type: str
    free: bool
    url: str

    def is_from_ravelry(self) -> bool:
        """
        Check if the download location is external
        """
        return True if self.type == "ravelry" else False

    def is_url_file(self) -> bool:
        """
        Check if the download location is a file
        """
        return True if self.url.split(".")[-1] in ["pdf", "html"] else False
