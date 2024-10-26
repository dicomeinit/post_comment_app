from django.conf import settings
from vertexai import init as vertexai_init
from vertexai.generative_models import GenerativeModel

_model = None


def get_model():
    global _model
    if not _model:
        vertexai_init(project=settings.VERTEXAI_PROJECT_ID, location=settings.VERTEXAI_LOCATION)

        _model = GenerativeModel(settings.VERTEXAI_MODEL_NAME)
    return _model
