import base64
import re

import requests


class GitHubService:

    API_BASE_URL = "https://api.github.com"

    def _parse_repository_url(self, repository_url):
        pattern = (
            r"github\.com/"
            r"([^/]+)/"
            r"([^/#]+)"
        )

        match = re.search(
            pattern,
            repository_url,
        )

        if not match:
            raise ValueError(
                "Invalid GitHub repository URL."
            )

        owner = match.group(1)
        repository = match.group(2)

        repository = repository.removesuffix(".git")

        return owner, repository

    def get_repository_files(
        self,
        repository_url,
    ):
        owner, repository = (
            self._parse_repository_url(
                repository_url
            )
        )

        url = (
            f"{self.API_BASE_URL}"
            f"/repos/{owner}/{repository}/git/trees/HEAD"
        )

        response = requests.get(
            url,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        return [
            item
            for item in data.get("tree", [])
            if item.get("type") == "blob"
        ]

    def get_file_content(
        self,
        repository_url,
        file_path,
    ):
        owner, repository = (
            self._parse_repository_url(
                repository_url
            )
        )

        url = (
            f"{self.API_BASE_URL}"
            f"/repos/{owner}/{repository}"
            f"/contents/{file_path}"
        )

        response = requests.get(
            url,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        if data.get("encoding") != "base64":
            raise ValueError(
                "GitHub returned an unsupported file encoding."
            )

        decoded = base64.b64decode(
            data["content"]
        )

        return decoded.decode(
            "utf-8",
            errors="replace",
        )