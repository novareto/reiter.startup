import bjoern
import importscan
import pathlib
import logging
from zope.dottedname import resolve
from omegaconf import OmegaConf
from rutter.urlmap import URLMap
from reiter.startup.utils import environment, make_logger
from reiter.startup.tasker import AsyncioTasker
from pkg_resources import iter_entry_points


def server(config):

    logger = make_logger("reiter.startup")

    for plugin in iter_entry_points('reiter.application.wsgiapps'):
        app = plugin.load()

    app = URLMap()
    app['/'] = apps.browser
    app['/api'] = apps.api
    app['/backend'] = apps.backend

    for plugin in iter_entry_points('reiter.application.plugins'):
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
            #pprint.pprint(list(apps.browser.routes))
            bjoern.run(
                app, config.server.host,
                int(config.server.port), reuse_port=True)
        else:
            logger.info(
                f"Server started on socket {config.server.socket}.")
            bjoern.run(app, config.server.socket)
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
    baseconf = OmegaConf.load('config.yaml')
    override = OmegaConf.from_cli()
    config = OmegaConf.merge(baseconf, override)
    with environment(**config.environ):
        server(config)


if __name__ == "__main__":
    start()
