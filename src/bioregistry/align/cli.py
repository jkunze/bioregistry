# -*- coding: utf-8 -*-

"""CLI for alignment."""

import click

from .miriam import align_miriam
from .obofoundry import align_obofoundry
from .ols import align_ols
from ..utils import secho

__all__ = [
    'align',
]


@click.command()
def align():
    """Align all external registries."""
    secho('Aligning MIRIAM')
    align_miriam()

    secho('Aligning OBO Foundry')
    align_obofoundry()

    secho('Aligning OLS')
    align_ols()


if __name__ == '__main__':
    align()
