# Copyright (C) Izhar Ahmad 2025-2026
# This project is under the MIT license

from __future__ import annotations

from typing import TYPE_CHECKING
from prept.cli import outputs
from prept.cli.status import StatusUpdate
from prept.cli.params import BOILERPLATE

import click
import shutil
import os
import pathlib

if TYPE_CHECKING:
    from prept.boilerplate import BoilerplateInfo
    from types import TracebackType

__all__ = (
    'new',
)


class _OutputDirectory:
    def __init__(self, bp: BoilerplateInfo, output: pathlib.Path | None) -> None:
        self._bp = bp
        self._owned = False
        self.output = output

    def __enter__(self) -> _OutputDirectory:
        outputs.echo_info(f'Generating project from boilerplate: {self._bp.name}')

        if self.output is None:
            self.output = pathlib.Path(self._bp.default_generate_directory)

        out_abs = self.output.absolute()  # for outputs
        if self.output.exists():
            outputs.echo_warning(f'Directory \'{out_abs}\' already exists!')
            click.echo(outputs.cli_msg('Previous content that can be overwritten will be lost if you proceed.'))

            if not click.confirm(outputs.cli_msg('Do you wish to overwrite existing directory content?')):
                self.output = None
                outputs.echo_info('Exited without making any changes.')
        else:
            outputs.echo_info(f'No existing directory found. Creating project directory at \'{out_abs}\'')
            self._owned = True
            try:
                self.output.mkdir()
            except Exception as e:
                # Directory not created, we will not try to delete in __exit__
                self.output = None
                raise outputs.wrap_exception(
                    e,
                    'Project directory creation failed with following error:',
                    'Ensure proper permissions are granted to create directory at given path',
                ) from None
            else:
                outputs.echo_info(f'Successfully created project directory at {out_abs}')

        return self

    def __exit__(self, exc_type: type[Exception] | None, exc: Exception | None, tb: TracebackType | None) -> None:
        if not exc:
            return
        if self._owned and self.output:
            try:
                shutil.rmtree(self.output)
            except Exception:
                # XXX: raise exception here?
                return

@click.command()
@click.pass_context
@click.argument(
    'boilerplate',
    required=True,
    type=BOILERPLATE,
)
@click.option(
    '--output', '-O',
    required=False,
    default=None,
    type=click.Path(file_okay=False, dir_okay=True, readable=True, writable=True, path_type=pathlib.Path),
    help=(
        'The output directory in which the generated files are put into.\n\n'
        'This defaults to default_generate_directory in preptconfig.json if set otherwise '
        'the name of boilerplate is used as default. If the directory does not exist, it is '
        'created by Prept.'
    )
)
@click.option(
    '--var', '-V',
    nargs=2,
    multiple=True,
    required=False,
    default=None,
    help=(
        'The name/value pair of template variables in "-V <name> <value>" format.\n\n'
        'This takes variables corresponding to ``template_variables`` setting in preptconfig.json. If '
        'some variables are not provided through this option, input for them is prompted when command is ran.\n\n'
        'If allow_extra_variables setting is set to true in configuration, this option allows passing '
        'variables that are not defined in template variables. If setting is false (default), this causes an error '
        'to be thrown.'
    )
)
def new(
    ctx: click.Context,
    boilerplate: BoilerplateInfo,
    output: pathlib.Path | None = None,
    var: list[tuple[str, str]] | None = None,
):
    """Bootstrap project from a boilerplate.

    BOILERPLATE is the name or path of boilerplate (containing preptconfig.json) to
    generate the project from.
    """
    with _OutputDirectory(boilerplate, output) as output_mgr:
        output = output_mgr.output

        if output is None:
            return

        variables = boilerplate._resolve_variables(var or [])
        genctx = boilerplate._get_generation_context(
            output=output,
            variables=variables,
        )
        tp = boilerplate.template_provider(**boilerplate.template_provider_params) if boilerplate.template_provider else None
        engine = boilerplate.engine

        if engine:
            outputs.echo_info('Calling the pre-generation hook')
            engine._call_hook(genctx, pre=True)

        outputs.echo_info(f'Creating project files at \'{output.absolute()}\'')
        click.echo()

        for file in boilerplate._get_generated_files():
            file_inst = genctx._set_current_file(file.name, boilerplate.path / file, output / file)

            if engine:
                # If _call_processors() returns false, this means some processor
                # returned false indicating to stop generation of the current file.
                if not engine._call_processors(str(file), genctx):
                    click.echo(outputs.cli_msg(f'├── Skipping generation of {file} (processor signal)'))
                    continue
            
            if tp and file_inst.process_path_template and boilerplate._is_template(file, path=True):
                with StatusUpdate(
                    outputs.cli_msg(f'├── Processing template path {file_inst.output_path}'),
                    error_message=f'An error occured while processing template path {file_inst.output_path}:'
                ):
                    output_path = tp.process_path(file_inst.output_path, genctx)
            else:
                output_path = file_inst.output_path

            with StatusUpdate(
                outputs.cli_msg(f'├── Creating {output_path}'),
                error_message=f'Copying of {file_inst.path} to installation directory at {output_path} failed with following error:',
            ):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                shutil.copy2(file_inst.path, output_path)

            if tp is not None and file_inst.process_content_template and boilerplate._is_template(file):
                with StatusUpdate(
                    outputs.cli_msg(f'├── Processing template content {output_path}'),
                    error_message=f'An error occured while processing template content of {output_path}:'
                ):
                    content = tp.process_content(genctx.current_file, genctx)

                mode = 'wb' if isinstance(content, bytes) else 'w'

                with open(output_path, mode) as f:
                    f.write(content)  # type: ignore

    click.echo()

    if engine:
        outputs.echo_info('Calling the post-generation hook')
        engine._call_hook(genctx, pre=False)

    outputs.echo_success(f'Successfully generated project from {boilerplate.name!r} boilerplate at \'{output.absolute()}\'')
