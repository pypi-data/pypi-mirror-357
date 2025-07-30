import os
import json
import sys
from abc import ABCMeta
from rich.pretty import Pretty
from aiwb.utils.console import console, err_console


class ServiceModel(metaclass=ABCMeta):
    service_name = None

    def __init__(self, client, output):
        self._client = client
        self._cloud = os.getenv("AIWB_CLOUD", "aws")
        self._url = os.getenv(
            "AIWB_URL",
            f"https://ai.{self._cloud}.renesasworkbench.com",
        )
        self.output = output

    @staticmethod
    def _console(data, output="text", stderr=False, pretty=True):
        _console = console
        if stderr:
            _console = err_console
            pretty = False
            if isinstance(data, dict) and output != "json":
                data = data.get("message")
        if output == "json":
            try:
                data = json.dumps(data)
            except (TypeError, ValueError):
                _console = _console.print
                data = Pretty(data, indent_guides=False, expand_all=True)
            else:
                _console = _console.print_json
        elif output == "text":
            _console = _console.out
            pretty = False
        else:
            _console = _console.print
            if pretty:
                data = Pretty(data, indent_guides=False, expand_all=True)
        _console(data)

    def stdout(self, data):
        self._console(data, self.output)
        sys.exit(0)

    def stderr(self, data):
        self._console(data, self.output, stderr=True)
        sys.exit(1)

    def process(self, path, method="GET", **kwargs):
        res, err = self._client.request(f"{self._url}/{path}", method, **kwargs)
        if err:
            self.stderr(res)
        self.stdout(res)

    @classmethod
    def is_service(cls, service_name):
        if not cls.service_name:
            raise TypeError("Subclass of ServiceModel needs to have the `service_name` class attribute.")
        return service_name == cls.service_name
