from flask import Flask

from config import configure_app
from db import init_all

from modules.auth import bp as auth_bp
from modules.extratos import bp as extratos_bp
from modules.cadastros import bp as cadastros_bp
from modules.despesas_mensais import bp as despesas_mensais_bp
from modules.receitas_mensais import bp as receitas_mensais_bp
from modules.impostos import bp as impostos_bp
from modules.emprestimos import bp as emprestimos_bp
from modules.investimentos import bp as investimentos_bp
from modules.trader import bp as trader_bp
from modules.dashboard import bp as dashboard_bp
from modules.relatorios import bp as relatorios_bp


def create_app():
    app = Flask(__name__)
    configure_app(app)
    init_all()

    app.register_blueprint(auth_bp)
    app.register_blueprint(extratos_bp)
    app.register_blueprint(cadastros_bp)
    app.register_blueprint(despesas_mensais_bp)
    app.register_blueprint(receitas_mensais_bp)
    app.register_blueprint(impostos_bp)
    app.register_blueprint(emprestimos_bp)
    app.register_blueprint(investimentos_bp)
    app.register_blueprint(trader_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(relatorios_bp)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
