from subprocess import Popen
from time import sleep
from justserver.logging import logger
from typer import Typer

app = Typer()


@app.command()
def justniffer_ex(interface: str = 'any', log_format: str | None= None, filter: str| None = None, max_tcp_streams: int = 1024, truncated: bool = False, no_newline: bool = False, 
                  capture_in_the_middle: bool=False, encode: str | None = None):
    while True:
        logger.info(f'justniffer {interface=} {log_format=} {filter=} {max_tcp_streams=} {truncated=} {no_newline=} {capture_in_the_middle=} {encode=}')
        sleep(1)

if __name__ == '__main__':
    app()