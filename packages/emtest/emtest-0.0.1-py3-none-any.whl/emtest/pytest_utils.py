


import os
import sys
from typing import Any, Optional
from _pytest.terminal import TerminalReporter
from _pytest.config import Config
from _pytest.reports import TestReport
from termcolor import colored

class MinimalReporter(TerminalReporter):
    """Custom pytest reporter that provides clean, minimal output with colored symbols.
    
    This reporter suppresses most default pytest output and displays only:
    - ✓ for passed tests (green)
    - ✗ for failed tests (red) 
    - - for skipped tests (yellow)
    """
    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self._tw.hasmarkup = True  # enables colored output safely

    def _write_output(self, *args: Any, **kwargs: Any) -> None:
        """Override default output methods to suppress them."""
        pass  # override all default output methods

    def _write_summary(self) -> None:
        """Override summary writing to suppress it."""
        pass

    def pytest_sessionstart(self, session: Any) -> None:
        """Override session start to suppress 'collected x items' message."""
        # print("pytest_sessionstart")
        pass  # suppress "collected x items"

    def pytest_runtest_logstart(self, nodeid: str, location: Any) -> None:
        """Override test start logging to suppress it."""
        # print("pytest_runtest_logstart")
        pass  # suppress test start lines

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        """Display minimal test results with colored symbols."""
        if report.when != "call":
            return

        test_name = report.nodeid.split("::")[-1]
        if report.passed:
            symbol = colored("✓", "green")
        elif report.failed:
            symbol = colored("✗", "red")
        elif report.skipped:
            symbol = colored("-", "yellow")
        print(f"{symbol} {test_name}")

    def summary_stats(self) -> None:
        """Override result counts to suppress them."""
        pass  # suppress result counts

    def pytest_terminal_summary(self, terminalreporter: Any, exitstatus: int, config: Config) -> None:
        """Override final summary output to suppress it."""
        pass  # suppress final summary output


def configure_pytest_reporter(config: Config) -> None:
    """Configure the minimal reporter if terminalreporter plugin is disabled.
    
    Args:
        config: Pytest configuration object
    """
    # if terminalreporter plugin is disabled
    if "no:terminalreporter" in config.option.plugins:
        pluginmanager = config.pluginmanager
        pluginmanager.register(MinimalReporter(config), "minimal-reporter")


def run_pytest(test_path: str, breakpoints: bool, deactivate_pytest_output: bool = False, enable_print: bool = False) -> None:
    """Run pytest with customizable options for output control and debugging.
    
    Args:
        test_path: Path to the test file or directory to run
        breakpoints: If True, enables pytest debugger (--pdb) on failures
        deactivate_pytest_output: If True, uses minimal reporter instead of default output
        enable_print: If True, enables print statements in tests (-s flag)
    """
    args = []
    if deactivate_pytest_output:
        args += ["-p", "no:terminalreporter"]
    if enable_print:
        args.append("-s")  # -s disables output capturing
    if breakpoints:
        args.append("--pdb")
    os.system(f"{sys.executable} -m pytest {test_path} {' '.join(args)}")
