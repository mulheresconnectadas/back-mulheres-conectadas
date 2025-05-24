from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

from api.database import engine, Base
from api.routes import participante, publicacao

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #["http://localhost:3000"] para limitar ao front
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(participante.router, prefix="/participantes", tags=["Participantes"])
app.include_router(publicacao.router, prefix="/publicacoes", tags=["Publicações"])
