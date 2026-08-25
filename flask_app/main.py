from flask import Flask, render_template, request, redirect, url_for, flash
from flask_limiter.util import get_remote_address
from flask_login import login_required, current_user
from shared.database_file.set_up import Setup
from flask_app.statistics import analytics
from flask_app.login_flask import login_bp
from flask_app.registering import registering_bp
from flask_app.weather_route import weather_bp
from shared.database_file.oltp_models import Weatherforecast, login_manager, db, bcrypt, Pilot
from datetime import datetime, time, date as date_type
from sqlalchemy import text
from threading import Thread
from bokeh.server.server import Server
from dashboard.dashboard import create_dashboard
from bokeh.embed import server_document
import os
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from shared.database_file.extensions import limiter, csrf


logging.basicConfig(level=logging.DEBUG)
logging.getLogger('bokeh').setLevel(logging.DEBUG)
logging.getLogger('tornado').setLevel(logging.DEBUG)


def start_embedded_bokeh():
    try:
        def bokeh_app(doc):
            print("[BOKEH_APP] Début", flush=True)
            try:
                panel = create_dashboard()
                print("[BOKEH_APP] create_dashboard() terminé", flush=True)
                panel.server_doc(doc)
                print("[BOKEH_APP] server_doc() terminé avec succès", flush=True)
            except Exception as e:
                import traceback
                print(f"[BOKEH_APP ERROR] {e}", flush=True)
                traceback.print_exc()

        server = Server(
            {"/dashboard": bokeh_app},
            port=5006,
            allow_websocket_origin=["vayora.be", "vayora.be:443", "www.vayora.be", "www.vayora.be:443"],
            address="0.0.0.0",
            use_xheaders=True,
            session_token_expiration = 3600
        )
        server.start()
        server.io_loop.start()
    except Exception as e:
        import traceback
        print(f"[BOKEH ERROR] {e}", flush=True)
        traceback.print_exc()


# Démarrage automatique du thread
if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not os.environ.get("FLASK_ENV") == "development":
    t = Thread(target=start_embedded_bokeh, daemon=True)
    t.start()


def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    app.config.from_object(Setup)
    csrf.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = "login_bp.login"

    @app.route("/")
    def home():

        raw_places = (
            db.session.query(Weatherforecast.weather_place)
            .distinct()
            .order_by(Weatherforecast.weather_place)
            .all()
        )
        locations = [{"name": row[0]} for row in raw_places]

        selected_place = request.args.get("place", "").strip()
        selected_date = request.args.get("date", "").strip() or date_type.today().isoformat()

        predictions = []
        selected_ai_date = request.args.get("ai_date", "").strip()
        selected_ai_place = request.args.get("ai_place", "").strip()

        panel_script = server_document(f"{request.scheme}://{request.host}/dashboard")

        return render_template(
            "home.html",
            locations=locations,
            selected_place=selected_place,
            selected_date=selected_date,
            predictions=predictions,
            selected_ai_date=selected_ai_date,
            selected_ai_place=selected_ai_place,
            panel_script=panel_script,
        )

    app.register_blueprint(analytics)
    app.register_blueprint(login_bp)
    app.register_blueprint(registering_bp)
    app.register_blueprint(weather_bp)
    return app
app = create_app()
if __name__ == "__main__":
    app.run()
