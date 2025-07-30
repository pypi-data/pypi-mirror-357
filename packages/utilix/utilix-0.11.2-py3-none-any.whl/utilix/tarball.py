import os
import site
import tarfile
import importlib
from pathlib import Path
from git import Repo, InvalidGitRepositoryError


def filter_tarinfo(tarinfo, git_ignored_files, tarball_ignore_patterns=None):
    """Custom filter for tarfile to exclude Git-ignored files and .tarballignore patterns."""

    # Exclude Git-ignored files
    if any(f in tarinfo.name for f in git_ignored_files):
        return None

    if ".git" in Path(tarinfo.name).parts:
        return None

    # Exclude .tarballignore patterns if provided
    if tarball_ignore_patterns:
        for pattern in tarball_ignore_patterns:
            if pattern in tarinfo.name:
                return None

    # Include the file
    return tarinfo


class Tarball:
    def __init__(self, destination, package_name):
        """Class to tarball the editable user-installed from git repo.

        :param destination: the destination folder of the tarball
        :param package_name: the name of package

        """
        self.destination = destination
        self.package_name = package_name

    @property
    def tarball_name(self):
        return f"{self.package_name}.tar.gz"

    @property
    def tarball_path(self):
        return os.path.join(self.destination, self.tarball_name)

    def create_tarball(self, overwrite=False):
        """Create the tarball of package."""

        if os.path.exists(self.tarball_path) and not overwrite:
            raise RuntimeError(f"{self.tarball_path} already exists!")

        # Get the origin of the package source
        repo = Tarball.get_installed_git_repo(self.package_name)
        package_origin = repo.working_dir
        if not package_origin:
            raise RuntimeError(
                f"Can not make tarball of package {self.package_name},"
                "because it is not in user-installed editable mode."
            )

        # List ignored files
        git_ignored_files = repo.git.ls_files(
            "--others", "--ignored", "--exclude-standard"
        ).splitlines()

        # Check for .tarballignore file
        tarball_ignore_patterns = None
        tarball_ignore_file = os.path.join(package_origin, ".tarballignore")
        if os.path.exists(tarball_ignore_file):
            with open(tarball_ignore_file, "r") as f:
                tarball_ignore_patterns = [
                    line.strip() for line in f if line.strip() and not line.startswith("#")
                ]

        # Define the output tarball filename
        with tarfile.open(self.tarball_path, "w:gz") as tar:
            tar.add(
                package_origin,
                arcname=os.path.basename(package_origin),
                recursive=True,
                filter=lambda tarinfo: filter_tarinfo(
                    tarinfo, git_ignored_files, tarball_ignore_patterns
                ),
            )

    @staticmethod
    def get_installed_git_repo(package_name):
        """If a package is in editable user-installed mode, we can get its git working directory.

        The editable user-installed is usually installed by `pip install -e ./ --user`.

        """
        # Find the package's location
        mod = importlib.import_module(package_name)
        # Try initialize git repository
        try:
            repo = Repo(mod.__file__, search_parent_directories=True)
            return repo
        except (OSError, InvalidGitRepositoryError):
            return

    @staticmethod
    def is_user_installed(package_name):
        """Test if a package is in user-installed mode.

        The user-installed is usually installed by `pip install ./ --user`.

        """
        # Find the package's location using importlib
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            raise ModuleNotFoundError(f"Package {package_name} is not installed.")
        package_location = spec.origin

        # Get the user-specific package directory
        user_site_packages = site.getusersitepackages()

        # Check if the package is installed in the user-specific directory
        return package_location.startswith(user_site_packages)
