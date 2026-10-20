import os
import sys

# Ensure root folder is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

app = create_app()

# Auto-initialize database tables and demo seed data on serverless startup
with app.app_context():
    try:
        db.create_all()
        from app.models.ngo import NGO
        if NGO.query.count() == 0:
            from seed_db import seed_data
            seed_data()
    except Exception as e:
        app.logger.warning(f"Database auto-init notice: {e}")
