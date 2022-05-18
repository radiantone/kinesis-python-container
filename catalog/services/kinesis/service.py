from flask_restx import Namespace, Resource

api = Namespace("kinesis", "Kinesis service for Content Catalog")


@api.route("/")
class CatalogKinesisService(Resource):
    def get(self):
        return {"status": "ok"}
