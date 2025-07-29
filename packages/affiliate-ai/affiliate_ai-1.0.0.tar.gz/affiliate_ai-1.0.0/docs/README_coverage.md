
# 🧩 Pour activer la route /coverage :
# 1. Ajouter dans server.py après création de app :
#     from api.routes.coverage_patch import coverage_bp
#     app.register_blueprint(coverage_bp)
#
# 2. Lancer le serveur :
#     python3 api/server.py
#
# 3. Accéder à :
#     http://localhost:5000/coverage
