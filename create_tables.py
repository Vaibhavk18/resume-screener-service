
from app.models.database import Base, engine
from app.models import entities

print("Creating tables on RDS...")
Base.metadata.create_all(bind=engine)
print("Done ✅")
