import logging
from flask import Flask
from flask_cors import CORS
from umai.routes.reservas import reservas_bp
<<<<<<< HEAD

=======
from umai.routes.reseñas import reseñas_bp
from umai.routes.platos import platos_bp
>>>>>>> feature/obtener_disponibilidad

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)

app.register_blueprint(reservas_bp, url_prefix="/reservas")
<<<<<<< HEAD

=======
app.register_blueprint(reseñas_bp, url_prefix="/reseñas")
app.register_blueprint(platos_bp, url_prefix="/platos")
>>>>>>> feature/obtener_disponibilidad

if __name__ == "__main__":
    app.run(port=5000, debug=True)