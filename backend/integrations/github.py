import base64
import re

import requests


class GitHubService:

    API_BASE_URL = "https://api.github.com"

    MAX_FILE_SIZE = 100_000
    MAX_TOTAL_CODE_SIZE = 1_000_000

    # File extensions that CodeReview AI can review
    REVIEWABLE_EXTENSIONS = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".php",
        ".go",
        ".rs",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".cs",
        ".rb",
        ".swift",
        ".kt",
        ".kts",
        ".dart",
        ".sql",
    }

    # Directories that should never be reviewed
    IGNORED_DIRECTORIES = {
        "node_modules",
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".next",
        "dist",
        "build",
        "coverage",
    }

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
            params={
                "recursive": "1",
            },
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        files = []

        for item in data.get("tree", []):

            if item.get("type") != "blob":
                continue

            file_path = item.get("path", "")

            if self._should_ignore_file(file_path):
                continue

            files.append(item)

        return files

    def _should_ignore_file(self, file_path):
        parts = file_path.split("/")

        # Ignore files inside unwanted directories
        for part in parts[:-1]:
            if part in self.IGNORED_DIRECTORIES:
                return True

        # Only return supported source-code files
        filename = parts[-1]

        if "." not in filename:
            return True

        extension = "." + filename.rsplit(".", 1)[1].lower()

        return extension not in self.REVIEWABLE_EXTENSIONS

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