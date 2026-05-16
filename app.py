import logging
from flask import Flask
from flask_cors import CORS
from umai.routes.reservas import reservas_bp
from umai.routes.reseñas import reseñas_bp
from umai.routes.servicios import servicios_bp

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)

app.register_blueprint(reservas_bp, url_prefix="/reservas")
app.register_blueprint(reseñas_bp, url_prefix="/reseñas")
app.register_blueprint(servicios_bp, url_prefix="/servicios")

if __name__ == "__main__":
    app.run(port=5000, debug=True)