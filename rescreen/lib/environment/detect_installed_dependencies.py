from shutil import which


def is_executable_available(executable_name):
    """
    Check whether 'executable_name' is in PATH and marked as executable
    :param executable_name: Name of the executable to check
    :return: True if it is available, else False
    """

    return which(executable_name) is not None


def check_dependencies():
    dependencies = ["xrandr", "xev", "loginctl", "whoami"]

    unavailable_dependencies = [dependency for dependency in dependencies if not is_executable_available(dependency)]

    if len(unavailable_dependencies) > 0:
        raise EnvironmentError(f"The following dependencies are missing: {', '.join(unavailable_dependencies)}")
