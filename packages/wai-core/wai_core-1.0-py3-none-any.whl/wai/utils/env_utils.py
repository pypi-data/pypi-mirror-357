import pkg_resources


def check_environment_sync(spec: str = "wai"):
    """
    Check if the current environment is in sync with the setup.py file.

    This function compares the installed packages with the required packages
    specified in the setup.py file. If any discrepancies are found, it prints
    out the missing or extra packages.

    Args:
        spec (str): The specification to use when checking the environment.
            Defaults to "wai", but could also be "wai[all]" for a full check.

    Raises:
        RuntimeError: If there are missing packages.
    """

    # Get the required packages from the setup.py file
    required_packages = pkg_resources.require(spec)

    # Get the installed packages
    installed_packages = pkg_resources.working_set

    # Initialize sets to store missing and extra packages
    missing_packages = set()

    # Iterate over the required packages
    for package in required_packages:
        # If the package is not installed, add it to the missing packages set
        if package not in installed_packages:
            missing_packages.add(package.project_name)

    # Print out the missing and extra packages
    # Raise an error if there are missing packages
    if missing_packages:
        error_message = (
            f"Environment is not in sync with setup.py file ({spec=}).\n"
            f"Missing packages:\n - {'\n - '.join(missing_packages)}"
        )
        raise RuntimeError(error_message)
