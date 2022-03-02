import contextlib
import socket
import urllib

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from tqdm import tqdm


class _PushGatewayIO:
    def __init__(self, *, task_name=None, gateway=None, timeout=3):
        self.gateway = gateway
        self.timeout = timeout

        self._registry = CollectorRegistry()
        self._task_name = task_name
        self._extra_info = {"instance": socket.gethostname()}
        self.percentage = Gauge(
            f"prom_tqdm_{self._task_name}_percentage",
            "Task completion percentage.",
            registry=self._registry,
        )

    def write(self, s):
        try:
            self.percentage.set(float(s))
        except ValueError:
            pass

    def flush(self):
        try:
            push_to_gateway(
                self.gateway,
                job=self._task_name,
                grouping_key=self._extra_info,
                registry=self._registry,
                timeout=self.timeout,
            )
        except urllib.error.URLError:
            pass


@contextlib.contextmanager
def prom_tqdm(*, task_name=None, push_gateway=None, timeout=3, **tqdm_kwargs):
    tqdm_kwargs.pop("file", None)
    tqdm_kwargs.pop("bar_format", None)
    mininterval = tqdm_kwargs.pop("mininterval", 5)

    prom_io = _PushGatewayIO(task_name=task_name, gateway=push_gateway, timeout=timeout)
    yield tqdm(
        file=prom_io, bar_format="{percentage}", mininterval=mininterval, **tqdm_kwargs
    )
