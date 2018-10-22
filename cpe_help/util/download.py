import os
import os.path
import subprocess

import click


@click.command()
@click.argument('url')
@click.argument('destination')
def CLI(url, destination):
    """Download a file to 'destination', if 'destination' doesn't exist yet
    """
    if not os.path.exists(destination):
        cmd = "http --ignore-stdin --check-status --timeout=3.0 --download '{}' --output '{}'".format(url, destination)
        returncode = subprocess.run(cmd, shell=True).returncode
        if returncode == 0:
            click.echo("Downloaded '{}' with success!".format(destination))
            return 0
        else:
            click.echo("Could not download '{}'.".format(destination))
            try:
                os.remove(destination)
            except OSError:
                pass
            return returncode
    else:
        click.echo("'{}' already exists!".format(destination))
        return 0


if __name__ == '__main__':
    CLI()
