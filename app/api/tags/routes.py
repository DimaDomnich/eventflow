from flask.views import MethodView
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.tag import TagModel
from app.schemas.tag import TagSchema
from app.utils.decorators import role_required
from flask_smorest import abort

from . import tags_blp


@tags_blp.route("")
class TagsList(MethodView):
    @jwt_required()
    @tags_blp.response(200, TagSchema(many=True))
    def get(self):
        return TagModel.query.all()

    @jwt_required()
    @role_required("organizer")
    @tags_blp.arguments(TagSchema)
    @tags_blp.response(201, TagSchema)
    def post(self, validated_data):
        if TagModel.query.filter_by(name=validated_data["name"]).first():
            abort(400, message="Tag with this name already exists.")

        tag = TagModel(**validated_data)

        db.session.add(tag)
        db.session.commit()

        return tag
