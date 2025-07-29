"""Command line entry point to the application.

"""
__author__ = 'Paul Landes'

from typing import List, Dict, Any
from pathlib import Path
import sys
import logging
import re
import plac
from zensols.relpo.app import Application

logger = logging.getLogger(__name__)
_LEVEL_DEFAULT: str = '[warn|info|debug]'
_OUT_DEFAULT: str = '<path>'
_FORMAT_DEFAULT: str = '<json|yaml>'
_MESSAGE_DEFAULT: str = '<comment>'


@plac.annotations(
    action=('task to execute (see actions)', 'positional', None, str),
    version=('print the version and exit', 'flag', 'v'),
    level=('level', 'option', 'l', str),
    config=('comma separated project configuration files', 'option', 'c', str),
    tmp=('temporary directory', 'option', 't', Path),
    out=('output path', 'option', 'o', str),
    format=('output format', 'option', 'f', str),
    message=('message comment used for new tags', 'option', 'm', str))
def invoke(action: str = None, version: bool = False,
           level: str = _LEVEL_DEFAULT,
           config: str = 'relpo.yml',
           tmp: Path = Path('temp'),
           out: str = _OUT_DEFAULT,
           format: str = _FORMAT_DEFAULT,
           message: str = _MESSAGE_DEFAULT):
    """\
Python project release with Git integration.

actions:
  config                output the synthesized build configuration
  meta [-o, -f]         output the project metadata
  pyproject             write the `pyproject.toml` file
  mktag [-m]            create a new tag using the last change log
  rmtag                 remove the most recent tag
  bumptag               move the latest tag to the last commit
  template              render standard in with: `date`, `project`, `config`
  check                 check for any issues with creating a release
  mkdoc [-o]            create site documentation
  mkenvdist [-o]        create the environment distribution

    """
    prog: str = Path(sys.argv[0]).name
    if version:
        action = 'version'
    fmt: str
    log_level: int = logging.WARNING
    if level == _LEVEL_DEFAULT:
        info_actions = 'check mktag rmtag bumptag doc mkdoc'
        if action in set(info_actions.split()):
            log_level = logging.INFO
        else:
            log_level = logging.WARNING
    else:
        log_level = {
            'warn': logging.WARNING,
            'info': logging.INFO,
            'debug': logging.DEBUG,
        }.get(level)
        if log_level is None:
            print(f'unknown log level: {log_level}', file=sys.stderr)
            sys.exit(1)
    if log_level == logging.DEBUG:
        fmt = '[%(levelname)s] %(module)s: %(message)s'
    else:
        fmt = f'{prog}: %(message)s'
    logging.basicConfig(format=fmt, level=logging.WARNING)
    logging.getLogger('zensols.relpo').setLevel(log_level)
    logging.getLogger('zensols.relpo.app').setLevel(log_level)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f'invoking action: {action}')
    out: str = None if out == _OUT_DEFAULT else out
    format: str = None if format == _FORMAT_DEFAULT else format
    message: str = 'minor release' if message == _MESSAGE_DEFAULT else message
    app = Application(
        config_files=tuple(map(Path, re.split(r'[\s,]+', config))),
        temporary_dir=tmp)
    kwargs: Dict[str, Any] = {}
    if out is not None:
        kwargs['out'] = Path(out)
    if action == 'mktag':
        kwargs['message'] = message
    if format is not None:
        kwargs['format'] = format
    try:
        if action is None:
            raise ValueError('missing action argument')
        if not hasattr(app, action):
            raise ValueError(f'no such action: {action}')
        meth = getattr(app, action)
        ret = meth(**kwargs)
        if isinstance(ret, int):
            sys.exit(ret)
    except Exception as e:
        print(f'{prog}: error: {e}', file=sys.stderr)
        if log_level <= logging.DEBUG:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main(args: List[str] = None):
    if args is not None:
        sys.argv = ['relpo'] + args
    plac.call(invoke)
