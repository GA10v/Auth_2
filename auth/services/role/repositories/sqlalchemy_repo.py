import uuid

import sqlalchemy.exc as sqlalch_exc

import services.role.layer_models as layer_models
import services.role.payload_models as payload_models
import services.role.repositories.protocol as protocol
import utils.exceptions as exc
from db import session_scope
from models.permissions import Permission, RolePermission
from models.role import Role


class RoleSqlalchemyRepository(protocol.RoleRepositoryProtocol):
    def get_multi(self) -> list[layer_models.Role]:
        roles = Role.query.all()
        return [layer_models.Role.from_orm(role) for role in roles]

    def get_by_id(self, role_id: uuid.UUID) -> tuple[layer_models.Role, list[layer_models.Permission]]:
        role = Role.query.filter(Role.id == role_id).first()
        if not role:
            raise exc.NotFoundError
        permissions = Permission.query.join(RolePermission).filter(RolePermission.role_id == role_id).all()
        permissions = [layer_models.Permission.from_orm(perm) for perm in permissions]
        return layer_models.Role.from_orm(role), permissions

    def update(self, role_id: uuid.UUID, updated_role: payload_models.RoleUpdate) -> layer_models.Role:
        try:
            with session_scope():
                role = Role.query.filter(Role.id == role_id)
                if role.count() != 1:
                    raise exc.NotFoundError
                role.update(updated_role.dict(exclude_none=True))
        except sqlalch_exc.IntegrityError as ex:
            raise exc.UniqueConstraintError from ex
        return layer_models.Role.from_orm(role.first())

    def create(self, new_role: payload_models.RoleCreate) -> layer_models.Role:
        new_role = Role(**new_role.dict())
        try:
            with session_scope() as db_session:
                db_session.add(new_role)
                db_session.flush()
                return layer_models.Role.from_orm(new_role)
        except sqlalch_exc.IntegrityError as ex:
            raise exc.UniqueConstraintError from ex

    def delete(self, role_id: uuid.UUID) -> None:
        with session_scope():
            role = Role.query.filter(Role.id == role_id).first()
            if not role:
                raise exc.NotFoundError
            if role.protected:
                raise exc.AttemptDeleteProtectedObjectError
            role.is_deleted = True

    def add_permission_for_role(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
        new_link = RolePermission(role_id=role_id, perm_id=permission_id)
        try:
            with session_scope() as db_session:
                db_session.add(new_link)
        except sqlalch_exc.IntegrityError as ex:
            if exc.INTEGRITY_KEY_DIDNT_EXIST_MSG in str(ex):
                raise exc.NotFoundError from ex
            if exc.INTEGRITY_UNIQUE_CONSTRAINT_MSG in str(ex):
                raise exc.UniqueConstraintError

    def delete_permission_from_role(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> None:
        with session_scope():
            role_permission = RolePermission.query.filter(
                RolePermission.role_id == role_id,
                RolePermission.perm_id == permission_id,
            )
            if role_permission.count() != 1:
                raise exc.NotFoundError
            role_permission.update({'is_deleted': True})
