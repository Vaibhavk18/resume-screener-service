
from app.models.database import Base, engine
from app.models import entities
from app.models.database import engine

print("Using DB URL:", engine.url)
print("Dropping and recreating all tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ Done!")

