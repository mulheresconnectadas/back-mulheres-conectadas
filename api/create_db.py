from api.database import Base, engine
from api.model import Participante, Publicacao
from api.database import DATABASE_URL

print("Conectando em:", DATABASE_URL)

#Base.metadata.drop_all(bind=engine)  # Apaga tudo
Base.metadata.create_all(bind=engine)  # Cria tudo do zero
