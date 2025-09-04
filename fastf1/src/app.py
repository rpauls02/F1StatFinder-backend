import importlib
import pkgutil
from pathlib import Path
from flask import Flask, Blueprint
import fastf1
fastf1.Cache.enable_cache('./cache')

app = Flask(__name__)

# Path to the routes folder
routes_path = Path(__file__).parent / "routes"

# Iterate over all Python files in routes folder
for module_info in pkgutil.iter_modules([str(routes_path)]):
    module_name = module_info.name
    module_path = f"routes.{module_name}"

    # Import the module dynamically
    module = importlib.import_module(module_path)

    # Register all Blueprint instances
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, Blueprint):
            app.register_blueprint(attr)
            print(f"Registered blueprint: {attr_name} from {module_path}")

if __name__ == "__main__":
    app.run(port=8000, debug=True)
