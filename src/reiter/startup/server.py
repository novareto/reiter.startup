import bjoern
import importscan
import pathlib
import logging

from minicli import cli, run
from zope.dottedname import resolve
from omegaconf import OmegaConf
from rutter.urlmap import URLMap
from reiter.startup.utils import environment, make_logger
from reiter.startup.tasker import AsyncioTasker
from pkg_resources import iter_entry_points


@cli
def bjoern_server(configfile: pathlib.Path):
    logger = make_logger("reiter.startup")
    config = OmegaConf.load(configfile
)
    with environment(**config.environ):
        root = URLMap()
        for app in iter_entry_points('reiter.application.wsgiapps'):
            wsgiapp = app.load()
            wsgiapp.configure(config)
            root[app.name] = wsgiapp

        for plugin in iter_entry_points('reiter.application.modules'):
            module = plugin.load()
            importscan.scan(module)
            log = logger is not None and logger.info or logging.info
            log(f"Plugin '{plugin.name}' loaded.")

        #tasker = uvcreha.tasker.Tasker.create(apps)
        #tasker.start()
        try:
            if not config.server.socket:
                logger.info(
                    "Server started on "
                    f"http://{config.server.host}:{config.server.port}")
                bjoern.run(
                    root, config.server.host,
                    int(config.server.port), reuse_port=True)
            else:
                logger.info(
                    f"Server started on socket {config.server.socket}.")
                bjoern.run(root, config.server.socket)
        except KeyboardInterrupt:
            pass
        finally:
            #tasker.stop()
            pass


def start():
    def resolve_path(path: str) -> str:
        path = pathlib.Path(path)
        return str(path.resolve())

    OmegaConf.register_resolver("path", resolve_path)
    OmegaConf.register_resolver("class", resolve.resolve)
    run()
