import typing
import uuid

import services.role.layer_models as layer_models
import services.role.payload_models as payload_models


class RoleRepositoryProtocol(typing.Protocol):
    def get_multi(self) -> list[layer_models.Role]:
        ...

    def get_by_id(self, role_id: uuid.UUID) -> tuple[layer_models.Role, list[layer_models.Permission]]:
        """
        :raises NotFoundError:
        """
        ...

    def update(self, role_id: uuid.UUID, updated_role: payload_models.RoleUpdate) -> layer_models.Role:
        """
        :raises NotFoundError:
        :raises UniqueConstraintError: если роль с указанным именем уже существует
        """
        ...

    def create(self, new_role: payload_models.RoleCreate) -> layer_models.Role:
        """
        :raises UniqueConstraintError: если роль с указанным именем уже существует
        """
        ...

    def delete(self, role_id: uuid.UUID) -> None:
        """
        :raises NotFoundError:
        """
        ...

    def add_permission_for_role(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
        """
        :raises NotFoundError:
        :raises UniqueConstraintError: если связь между указанной ролью и пермишоном уже существует
        """
        ...

    def delete_permission_from_role(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
        """
        :raises NotFoundError:
        """
        ...
