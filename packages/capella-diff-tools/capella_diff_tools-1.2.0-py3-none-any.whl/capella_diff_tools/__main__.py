# Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
"""Main entry point into capella_diff_tools."""

from __future__ import annotations

import datetime
import logging
import os
import pathlib
import sys
import typing as t

import capellambse
import capellambse.filehandler.git
import capellambse.model as m
import click
import markupsafe
import yaml
from capellambse import filehandler as fh

import capella_diff_tools

from . import compare, report, types

logger = logging.getLogger(__name__)

_T = t.TypeVar("_T", bound=m.ModelElement)


@click.command()
@click.version_option(
    version=capella_diff_tools.__version__,
    prog_name="Capella Diff Tools",
    message="%(prog)s %(version)s",
)
@click.argument("model", type=capellambse.ModelInfoCLI())
@click.argument("old_version")
@click.argument("new_version")
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.File("w", encoding="utf-8"),
    help="Write the diff report as YAML",
)
@click.option(
    "-r",
    "--report",
    "report_file",
    type=click.File("w", encoding="utf-8"),
    help="Generate a human-readable HTML report",
)
def main(
    model: dict[str, t.Any],
    old_version: str,
    new_version: str,
    output_file: t.IO[str] | None,
    report_file: t.IO[str] | None,
) -> None:
    """Generate the diff summary between two model versions.

    If neither '--output' nor '--report' are specified, the result is
    written in YAML format to stdout.
    """
    logging.basicConfig(level="DEBUG")
    model.pop("revision", None)
    model["path"] = _ensure_git(model["path"])
    old_model = capellambse.MelodyModel(**model, revision=old_version)
    new_model = capellambse.MelodyModel(**model, revision=new_version)

    metadata: types.Metadata = {
        "model": model,
        "old_revision": _get_revision_info(old_model, old_version),
        "new_revision": _get_revision_info(new_model, new_version),
    }
    objects = compare.compare_all_objects(old_model, new_model)
    diagrams = compare.compare_all_diagrams(old_model, new_model)

    result: types.ChangeSummaryDocument = {
        "metadata": metadata,
        "diagrams": diagrams,
        "objects": objects,
    }

    if output_file is report_file is None:
        output_file = sys.stdout

    if output_file is not None:
        yaml.dump(result, output_file, Dumper=CustomYAMLDumper)
    if report_file is not None:
        report_file.write(report.generate_html(result))


def _ensure_git(path: str | os.PathLike[str]) -> str:
    proto, path = fh.split_protocol(path)
    if proto == "file":
        assert isinstance(path, pathlib.Path)
        path = "git+" + path.resolve().as_uri()

    proto, _ = fh.split_protocol(path)
    if proto != "git":
        raise click.Abort("The 'model' must point to a git repository")

    assert isinstance(path, str)
    return path


def _get_revision_info(
    model: capellambse.MelodyModel,
    revision: str,
) -> types.RevisionInfo:
    """Return the revision info of the given model."""
    res = model._loader.resources["\x00"]
    assert isinstance(res, fh.git.GitFileHandler)
    info = res.get_model_info()
    assert isinstance(info, fh.git.GitHandlerInfo)
    assert t.assert_type(info.rev_hash, str) is not None
    author, date_str, description = res._git(
        "log",
        "-1",
        "--format=%aN%x00%aI%x00%B",
        info.rev_hash,
        encoding="utf-8",
    ).split("\x00")
    return {
        "hash": info.rev_hash,
        "revision": revision,
        "author": author,
        "date": datetime.datetime.fromisoformat(date_str),
        "description": description.rstrip(),
    }


class CustomYAMLDumper(yaml.SafeDumper):
    """A custom YAML dumper that can serialize markupsafe.Markup."""

    def represent_markup(self, data: t.Any) -> t.Any:
        """Represent markupsafe.Markup with the '!html' tag."""
        return self.represent_scalar("!html", str(data))


CustomYAMLDumper.add_representer(
    markupsafe.Markup, CustomYAMLDumper.represent_markup
)


if __name__ == "__main__":
    main()
