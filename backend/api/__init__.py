# Import routers from sub-modules and export them with aliases
from api.auth import router as auth  # noqa: F401
from api.projects import router as projects  # noqa: F401
from api.chat import router as chat  # noqa: F401
from api.requirements import router as requirements  # noqa: F401
from api.models_api import router as models_api  # noqa: F401
from api.uml import router as uml  # noqa: F401 # Added UML router