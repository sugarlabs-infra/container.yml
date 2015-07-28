# Copyright (C) Sam Parkinson 2015
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import yaml
import click
from subprocess import call, check_call, check_output


PATH_ARG = dict(required=False, default='.')


def container_name(path):
    return os.path.basename(path)


def image_exsists(image):
    images = check_output(['docker', 'images', '-q', image])
    return images.strip() != ''


def container_running(name):
    ps = check_output(['docker', 'ps', '-q', '-f', 'name=' + name])
    return ps.strip() != ''


def do_stop(image):
    call(['docker', 'kill', '-s', '9', image])
    call(['docker', 'rm', image])


@click.group()
def cli():
    pass


@cli.command(help='Start a container')
@click.argument('path', **PATH_ARG)
@click.option('-d', is_flag=True,
              help='Run in the background')
def start(path, d):
    path = os.path.abspath(path)
    name = container_name(path)
    do_stop(name)
    if not image_exsists(name):
        click.secho('No image {} found'.format(name), fg='red')
        click.echo('Build the image before continuing')
        sys.exit(1)

    with open(os.path.join(path, 'container.yml')) as f:
        config = yaml.load(f.read())

    options = ['docker', 'run', '--name', name]
    for key, value in config.iteritems():
        if key in ('volumes', 'ports', 'env'):
            option = '-' + key[0]
            for i in value:
                options.extend([option, i])
            continue

        if key in ('privileged'):
            # Some flags are only boolean
            options.append('--' + key)
            continue

        if key == 'cpu':
            # This is actually a fake flag that proxys to --cpu-quota
            # and is set in percentages instead of 0000s
            key = 'cpu-quota'
            value = int(value) * 1000

        if key == 'memory':
            # Add a swap limit equal to the memory
            options.extend(['--memory-swap', str(value)])

        if key == 'env-file':
            with open(value) as f:
                envs = yaml.load(f)
            for k, v in envs.iteritems():
                options.extend(['-e', k + '=' + v])

        options.extend(['--' + key, str(value)])

    if d:
        options.extend(['-d', '--restart=always')
    else:
        options.append('-it')

    check_call(options + [name])


@cli.command(help='Kill a container (SIGKILL)')
@click.argument('path', **PATH_ARG)
def stop(path):
    path = os.path.abspath(path)
    name = container_name(path)
    do_stop(name)


@cli.command(help='Build the image for a container')
@click.argument('path', **PATH_ARG)
@click.option('-l', is_flag=True,
              help='Limit build process to container resources')
def build(path, l):
    path = os.path.abspath(path)
    name = container_name(path)
    options = ['docker', 'build', '--tag=' + name]

    if l:
        with open(os.path.join(path, 'container.yml')) as f:
            config = yaml.load(f.read())
        for key, value in config.iteritems():
            if key == 'cpu':
                # This is actually a fake flag that proxys to --cpu-quota
                # and is set in percentages instead of 0000s
                key = 'cpu-quota'
                value = int(value) * 1000

            if key in ('cpu-quota', 'memory'):
                options.extend(['--' + key, str(value)])

    check_call(options + [path])


@cli.command(help='View container output')
@click.argument('path', **PATH_ARG)
def logs(path):
    path = os.path.abspath(path)
    name = container_name(path)
    if not container_running(name):
        click.secho('Container not running', fg='red')
        sys.exit(1)
    call(['docker', 'logs', '--tail=20', '-f', name])


@cli.command(help='View container resource usage')
@click.argument('path', **PATH_ARG)
def stats(path):
    path = os.path.abspath(path)
    name = container_name(path)
    if not container_running(name):
        click.secho('Container not running', fg='red')
        sys.exit(1)
    call(['docker', 'stats', name])


if __name__ == '__main__':
    cli()
