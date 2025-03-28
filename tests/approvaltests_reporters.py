import filecmp
import json
import os
import shutil
import subprocess
from pathlib import Path

import plotly.graph_objects as pgo
from approvaltests.reporters.first_working_reporter import FirstWorkingReporter
from approvaltests.reporters.generic_diff_reporter import GenericDiffReporter
from approvaltests.reporters.generic_diff_reporter_config import (
    GenericDiffReporterConfig,
)
from approvaltests.reporters.python_native_reporter import PythonNativeReporter


class BlockingGenericDiffReporter(GenericDiffReporter):
    @staticmethod
    def run_command(command_array: list[str]):
        subprocess.run(command_array)


class ReportWithPyCharmLinuxFlatpak(BlockingGenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithPyCharmLinuxFlatpak",
                path="/usr/bin/flatpak",
                extra_args=["run", "com.jetbrains.PyCharm-Community", "diff"],
            )
        )


class ReportWithPyCharmLinux(BlockingGenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithPyCharm",
                path="pycharm",
                extra_args=["diff"],
            )
        )


class ReportWithPyCharmProfessionalMacOS(BlockingGenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithPyCharmProfessionalMacOS",
                path="open",
                extra_args=[
                    # -W: Wait until the application is closed
                    "-W",
                    # -a: application
                    "-a",
                    "/Applications/PyCharm Professional Edition.app/Contents/MacOS/pycharm",  # noqa
                    "--args",
                    "diff",
                ],
            )
        )


class ReportWithPyCharmCommunityMacOS(BlockingGenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithPyCharmCommunityMacOS",
                path="open",
                extra_args=[
                    "-W",
                    "-a",
                    "/Applications/PyCharm CE.app/Contents/MacOS/pycharm",
                    "--args",
                    "diff",
                ],
            )
        )


class ReportWithVSCodeLinux(BlockingGenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithVSCodeLinux",
                path="code",
                extra_args=["--diff"],
            )
        )


class ReportWithVSCodeMacOS(BlockingGenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithVSCode",
                path="/Applications/Visual Studio Code.app/contents/Resources/app/bin/code",  # noqa
                extra_args=["-d"],
            )
        )


class PlotlyDiffReporter(FirstWorkingReporter):
    """Report the image representation of Plotly figures using diff tools.

    Plotly figures are compared using the JSON representation.
    This reporter reports the difference by showing the image representation of
    the Plotly figures in a diff tool.
    """

    def __init__(self):
        reporters = (
            ReportWithPyCharmLinux(),
            ReportWithPyCharmLinuxFlatpak(),
            # ReportWithPyCharmProfessionalMacOS(),
            # ReportWithPyCharmCommunityMacOS(),
            ReportWithVSCodeLinux(),
            ReportWithVSCodeMacOS(),
        )
        super().__init__(*reporters)

    def report(self, received_path: str, approved_path: str) -> bool:
        approved_path_image = str(Path(approved_path).with_suffix(".png"))
        received_path_image = str(Path(received_path).with_suffix(".png"))
        if os.path.exists(approved_path):
            with open(approved_path, "r") as file:
                raw = json.load(file)
            approved_figure = pgo.Figure(raw)
            approved_figure.write_image(approved_path_image)

        with open(received_path, "r") as file:
            raw = json.load(file)
        received_figure = pgo.Figure(raw)
        received_figure.write_image(received_path_image)

        try:
            # Use first working diff tool as reporter
            success = super().report(received_path_image, approved_path_image)
            if success is False:
                return PythonNativeReporter().report(received_path, approved_path)
            # After diff tool is closed are the images the same?
            if filecmp.cmp(received_path_image, approved_path_image):
                # The diff tools saves approved image but we also need to
                # create approved file for the JSON representation
                shutil.move(received_path, approved_path)
        finally:
            try:
                os.remove(approved_path_image)
                os.remove(received_path_image)
            except FileNotFoundError:
                pass
        return success
