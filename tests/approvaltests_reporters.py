# TODO: support Windows
import filecmp
import json
import os
import shutil
from pathlib import Path

import plotly.graph_objects as pgo
from approvaltests.reporters.clipboard_reporter import CommandLineReporter
from approvaltests.reporters.first_working_reporter import FirstWorkingReporter
from approvaltests.reporters.generic_diff_reporter import (
    GenericDiffReporter,
    GenericDiffReporterConfig,
)
from approvaltests.reporters.report_with_vscode import ReportWithVSCodeMacOS


class ReportWithPyCharmLinuxFlatpak(GenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithPyCharmLinuxFlatpak",
                path="/usr/bin/flatpak",
                extra_args=["run", "com.jetbrains.PyCharm-Community", "diff"],
            )
        )


class ReportWithPyCharmLinux(GenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithPyCharm",
                path="pycharm",
                extra_args=["diff"],
            )
        )


class ReportWithPyCharmMacOS(GenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithPyCharmMacOS",
                path="/Applications/PyCharm CE.app/Contents/MacOS/pycharm",
                extra_args=["diff"],
            )
        )


class ReportWithVSCodeLinux(GenericDiffReporter):
    def __init__(self):
        super().__init__(
            config=GenericDiffReporterConfig(
                name="ReportWithVSCodeLinux",
                path="code",
                extra_args=["--diff"],
            )
        )


class PlotlyDiffReporter(FirstWorkingReporter):
    """Report the image representation of Plotly figures using diff tools.

    Plotly figures are compared using there JSON representation.
    This reporter reports the difference by showing the image representation of
    these Plotly figures in a diff tool.
    It creates additional approval files containing the image (.png).
    """

    def __init__(self):
        reporters = (
            ReportWithPyCharmLinux(),
            ReportWithPyCharmLinuxFlatpak(),
            ReportWithPyCharmMacOS(),
            ReportWithVSCodeLinux(),
            ReportWithVSCodeMacOS(),
            CommandLineReporter(),
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
