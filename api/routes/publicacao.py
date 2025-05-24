from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api import model, schema
from api.database import get_db

router = APIRouter()

@router.post("/publicar", status_code=status.HTTP_201_CREATED)
def criar_publicacao(publicacao: schema.PublicacaoCreate, db: Session = Depends(get_db)):
    try:
        db_publicacao = model.Publicacao(**publicacao.dict())
        db.add(db_publicacao)
        db.commit()
        db.refresh(db_publicacao)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao salvar publicação."
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Publicação criada com sucesso.",
            "data": schema.PublicacaoResponse.model_validate(db_publicacao).model_dump()
        }
    )