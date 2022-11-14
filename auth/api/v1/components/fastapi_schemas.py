from marshmallow import Schema, fields


class UserInfo(Schema):
    auth = fields.Boolean(metadata={'description': 'Свежесть токена'})
    is_super = fields.Boolean(metadata={'description': 'admin'})
    user = fields.Str(
        metadata={
            'description': 'User id',
            'required': True,
            'example': 'UUID',
        },
    )
    permissions = fields.List(
        fields.Integer(
            metadata={
                'description': 'code',
                'required': True,
                'example': 0,
            },
        ),
    )
