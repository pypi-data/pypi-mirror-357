from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, cast


class BaseRouter[RT: Any, TT: Any](ABC):
    def __init__(
        self,
        *,
        default_target_resource: RT,
    ) -> None:
        self._default_target_resource: RT = default_target_resource

        self.targets: dict[TT, RT] = {}

    def register_targets(
        self,
        resource: RT,
        targets: Iterable[TT],
    ) -> None:
        self.targets.update(dict.fromkeys(targets, resource))

    @abstractmethod
    def _route_to_resource[DT: Any](
        self,
        data: Iterable[DT],
        resource: RT,
        target: TT,
    ) -> Iterable[Any]:
        ...

    def route_to_target[DT: Any](
        self,
        data: Iterable[DT],
        target: TT,
    ) -> Iterable[Any]:
        resource: RT = cast("RT", self.targets.get(target, self._default_target_resource))

        return self._route_to_resource(data, resource, target)
