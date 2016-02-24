import click
import ConfigParser
import imp
import os
import pyarkosclient

from utils import CLIException


VERSION = "0.1"
frameworks_folder = os.path.join(os.path.dirname(__file__), 'frameworks')


def get_sources():
    for x in os.listdir(frameworks_folder):
        if x == "__init__.py" or not x.endswith(".py"):
            continue
        mod = x.split(".py")[0]
        fmwk = imp.load_module(mod, *imp.find_module(mod, [frameworks_folder]))
        for y in fmwk.GROUPS:
            main.add_command(y)

def get_arkosrc():
    default_map = {}
    if os.path.exists(os.path.join(os.path.expanduser("~"), ".arkosrc")):
        cfg = ConfigParser.SafeConfigParser()
        cfg.read(os.path.join(os.path.expanduser("~"), ".arkosrc"))
        for n, v in cfg.items("arkosrc"):
            default_map[n] = v
    return default_map


@click.group()
@click.option("--local", envvar="ARKOS_CLI_FORCE_LOCAL", type=bool, default=None, help="Use in local context")
@click.option("--host", envvar="ARKOS_CLI_HOST", default="", help="Connect to remote arkOS server (host:port)")
@click.option("--user", envvar="ARKOS_CLI_USER", default="", help="Username for remote connection")
@click.option("--password", envvar="ARKOS_CLI_PASS", default="", help="Password for remote connection")
@click.option("--apikey", envvar="ARKOS_CLI_APIKEY", default="", help="API key for remote connection")
@click.pass_context
def main(ctx, local, host, user, password, apikey):
    ctx.obj = {"version": VERSION}
    if host and ((user and password) or apikey):
        ctx.obj["conn_method"] = "remote"
        ctx.obj["host"] = host
        try:
            ctx.obj["client"] = pyarkosclient.arkOS(host, user, password, api_key=apikey)
        except Exception, e:
            raise CLIException(e)
    elif local or not host:
        ctx.obj["conn_method"] = "local"
        try:
            import arkos
            arkos.init()
        except:
            raise CLIException("arkOS not installed locally, and no host specified")
    else:
        raise CLIException("arkOS not installed locally, and no connection information specified for remote host.")


# FIXME remove after testing
if __name__ == "__main__":
    get_sources()
    main(default_map=get_arkosrc())
