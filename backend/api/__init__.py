<<<<<<< HEAD
# Import routers from sub-modules using absolute paths for backend reliability
# We use aliases and # noqa: F401 to export them cleanly for main.py
from backend.api.auth import router as auth  # noqa: F401
from backend.api.projects import router as projects  # noqa: F401
from backend.api.chat import router as chat  # noqa: F401
from backend.api.requirements import router as requirements  # noqa: F401
from backend.api.models_api import router as models_api  # noqa: F401 
# from backend.api.uml import router as uml  # noqa: F401

# Note: Ensure the file backend/api/llm.py exists as we reviewed it earlier.
# If you renamed it to models_api.py, just update the import path accordingly.
=======
from api.auth import router as auth  # noqa: F401
from api.projects import router as projects  # noqa: F401
from api.chat import router as chat  # noqa: F401
from api.requirements import router as requirements  # noqa: F401
from api.models_api import router as models_api  # noqa: F401
>>>>>>> 5b97499 (chore: apply .gitignore and remove cached files)
