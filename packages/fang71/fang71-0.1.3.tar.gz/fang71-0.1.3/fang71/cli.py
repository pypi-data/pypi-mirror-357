"""Console script for fang71."""

import click


@click.command()
def main():
    """Main entrypoint."""
    click.echo("fang71")
    click.echo("=" * len("fang71"))
    click.echo("Skeleton project created by Cookiecutter PyPackage")


if __name__ == "__main__":
    main()  # pragma: no cover
