from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import datetime

# Creación de la aplicación FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de la base de datos
DATABASE_URL = ""
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Gestión de datos con Sqlalchemy",
        version="0.0.1",
        summary="🍐️ Validamos un crud basico usando FASTAPI y Sqlalchemy",
        description="🥥️ Esta aplicación es una app pequeña y corta nos permitirá definir en codigo todo lo que respecta a la docuementación del backend usando FASTAPI y Swagger usamos esto como base",
        contact={
            "name": "Contact: Aquicreamos",
            "url": "http://aquicreamos.com",
            "email": "wsgestor@gmail.com",
        },
        terms_of_service= "/",
        license_info={
            "name": "License Info Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
        routes=app.routes
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://scontent.feoh1-1.fna.fbcdn.net/v/t39.30808-6/299327973_488450629952156_8325044600034121460_n.jpg?_nc_cat=110&ccb=1-7&_nc_sid=5f2048&_nc_eui2=AeH2AWV-EnD-9C5qXdSr3xYd8PhIscsJTzDw-EixywlPMMGjv9JUFdbkjac6ZKGOyh8&_nc_ohc=G-VGxMRzSdsQ7kNvgF0afiY&_nc_ht=scontent.feoh1-1.fna&oh=00_AYCwDLcEb_xyjbVA693QEYz24ufMo67XFnCtI6scOMHrXw&oe=6642E981"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
# Modelo de la tabla
class Persona(Base):
    __tablename__ = "personas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    edad = Column(Integer, nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(Date, default=datetime.datetime.now)

# Modelo de Pydantic para entrada
class PersonaCreate(BaseModel):
    nombre: str
    apellido: str
    edad: int
    activo: bool = True

# Modelo de Pydantic para respuesta
class PersonaResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    edad: int
    activo: bool
    fecha_creacion: datetime.date

    class Config:
        orm_mode = True

# Creación de la tabla
#Base.metadata.create_all(bind=engine)

# Obtener todos los registros
@app.get("/personas", response_model=list[PersonaResponse], tags=['Personas'])
def get_personas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=0),
):
    with SessionLocal() as db:
        personas = db.query(Persona).offset(skip).limit(limit).all()
        return personas

# Obtener un registro por ID
@app.get("/personas/{persona_id}", response_model=PersonaResponse, tags=['Personas'])
def get_persona(persona_id: int):
    with SessionLocal() as db:
        persona = db.query(Persona).filter(Persona.id == persona_id).first()
        if persona is None:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        return persona

# Crear un nuevo registro
@app.post("/personas", response_model=PersonaResponse, tags=['Personas'])
def create_persona(persona: PersonaCreate):
    with SessionLocal() as db:
        db_persona = Persona(**persona.dict())
        db.add(db_persona)
        db.commit()
        db.refresh(db_persona)
        return db_persona

# Actualizar un registro
@app.put("/personas/{persona_id}", response_model=PersonaResponse, tags=['Personas'])
def update_persona(persona_id: int, persona: PersonaCreate):
    with SessionLocal() as db:
        persona_db = db.query(Persona).filter(Persona.id == persona_id).first()
        if persona_db is None:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        for key, value in persona.dict().items():
            setattr(persona_db, key, value)
        db.commit()
        db.refresh(persona_db)
        return persona_db

# Eliminar un registro
@app.delete("/personas/{persona_id}", tags=['Personas'])
def delete_persona(persona_id: int):
    with SessionLocal() as db:
        persona = db.query(Persona).filter(Persona.id == persona_id).first()
        if persona is None:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        db.delete(persona)
        db.commit()
        return JSONResponse(status_code=204)

# Filtrar por nombre
@app.get("/personas/nombre/{nombre}", response_model=list[PersonaResponse], tags=['Personas'])
def get_personas_by_nombre(nombre: str):
    with SessionLocal() as db:
        personas = db.query(Persona).filter(Persona.nombre == nombre).all()
        return personas

# Filtrar por apellido
@app.get("/personas/apellido/{apellido}", response_model=list[PersonaResponse], tags=['Personas'])
def get_personas_by_apellido(apellido: str):
    with SessionLocal() as db:
        personas = db.query(Persona).filter(Persona.apellido == apellido).all()
        return personas

# Filtrar por edad
@app.get("/personas/edad/{edad}", response_model=list[PersonaResponse], tags=['Personas'])
def get_personas_by_edad(edad: int):
    with SessionLocal() as db:
        personas = db.query(Persona).filter(Persona.edad == edad).all()
        return personas

# Filtrar por activo
@app.get("/personas/activo/{activo}", response_model=list[PersonaResponse], tags=['Personas'])
def get_personas_by_activo(activo: bool):
    with SessionLocal() as db:
        personas = db.query(Persona).filter(Persona.activo == activo).all()
        return personas

# Filtrar por fecha de creación
@app.get("/personas/fecha_creacion/{fecha_creacion}", response_model=list[PersonaResponse], tags=['Personas'])
def get_personas_by_fecha_creacion(fecha_creacion: datetime.date):
    with SessionLocal() as db:
        personas = db.query(Persona).filter(Persona.fecha_creacion == fecha_creacion).all()
        return personas
