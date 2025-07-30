from pyautd3_link_soem.native_methods.autd3_link_soem import ProcessPriority
from pyautd3_link_soem.native_methods.autd3capi_link_soem import NativeMethods as Soem

from .adapter import EtherCATAdapter
from .local import SOEM, SOEMOption
from .remote import RemoteSOEM
from .status import Status
from .thread_priority import ThreadPriority


def tracing_init() -> None:
    Soem().link_soem_tracing_init()


__all__ = [
    "SOEM",
    "EtherCATAdapter",
    "ProcessPriority",
    "RemoteSOEM",
    "SOEMOption",
    "Status",
    "ThreadPriority",
]


__version__ = "34.0.0"
