from typing import cast
from dataclasses import dataclass
from justniffer.extractors import BaseExtractor
from justniffer.model import Connection, Event
from justserver.daemon.ip_mapper import IPMApper, MokedIPMapper, KType, Resolved
from justserver.daemon.settings import settings

ip_mapper = MokedIPMapper() if settings.mocked_ip_mapper else IPMApper()


@dataclass
class ResolvedIP:
    name: str | None = None
    type: KType | None = None


class KubernetesNameBase(BaseExtractor):
    index: int

    def value(self, connection: Connection, events: list[Event], time: float | None) -> ResolvedIP | Resolved | None:
        ip = connection.conn[self.index][0]
        res = ip_mapper.map_ip(ip)
        if res is None:
            return ResolvedIP(name=None, type=None)
        return res


class SourceKubernetesName(KubernetesNameBase):
    index = 0


class DestKubernetesName(KubernetesNameBase):
    index = 1
