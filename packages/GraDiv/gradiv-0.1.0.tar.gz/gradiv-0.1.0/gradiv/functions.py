from sys import argv
from cloup import HelpFormatter, HelpTheme, Style, Context
import logging
from rich.logging import RichHandler
from rich.traceback import install
from gradiv.__init__ import __version__


# context settings for gradiv command
CONTEXT_SETTINGS = Context.settings(
    help_option_names=('-h', '--help'),
    ignore_unknown_options=False,
    align_option_groups=True,
    align_sections=True,
    show_constraints=True,
    formatter_settings=HelpFormatter.settings(
        max_width=120,
        col1_max_width=40,
        col2_min_width=60,
        indent_increment=2,
        col_spacing=1,
        row_sep=None,
        theme=HelpTheme.dark().with_(
            invoked_command=Style(fg='bright_yellow'),
            command_help=Style(fg='bright_cyan'),
            heading=Style(fg='green', bold=True),
            constraint=Style(fg='magenta'),
            section_help=Style(fg='red'),
            col1=Style(fg='bright_cyan'),
            col2=Style(fg='white'),
            epilog=Style(fg="bright_white", italic=True)
        )
    )
)

def init_log(verbosity:str="INFO") -> logging.Logger:
    """
    Initialize the logger and configure console and file output.
    :param str verbosity: Logging verbosity level.
    :return: Logger object.
    """
    verbosity = verbosity.upper()
    debug = False
    if verbosity == 'DEBUG':
        debug = True
        install(show_locals=True)

    # create console handler
    rich_handler = RichHandler(
        rich_tracebacks=True if debug else False,
        markup=True,
        show_time=False,
        show_level=False,
        show_path=True if debug else False,
        # console=shared_console
    )

    # create file handler (a: append / w: write)
    file_handler = logging.FileHandler('gradiv.log', mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # level debug and above

    # set format
    formatter = logging.Formatter(
        fmt=f'%(asctime)s | {"%(name)-8s | %(funcName)-22s |" if debug else ""} %(levelname)-8s | %(message)s',
        datefmt='%m-%d %H:%M'
    )
    file_handler.setFormatter(formatter)
    rich_handler.setFormatter(formatter)

    # initialize logger and set verbosity level
    logger = logging.getLogger("gradiv")
    logger.setLevel(getattr(logging, verbosity))

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(rich_handler)

    logger.info("Starting GraDiv")
    logger.info(f"GraDiv version: {__version__}")
    logger.info(f"Verbosity level: {verbosity}")
    logger.info(f"Command line run: {' '.join(argv)}")
    return logger



def format_stat_output(x) -> str:
    """Format statistics in output file for gradiv compute."""
    if isinstance(x, float): return format(x, '.2f')
    if x is None: return 'NA'
    if isinstance(x, (list, tuple)): return f'({" ".join(map(format_stat_output, x))})'
    return str(x)
