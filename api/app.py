from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import pika
import os

# Configuración crucial para trabajar detrás de Traefik
app = FastAPI(root_path="/api")

security = HTTPBasic()


class Message(BaseModel):
    content: str


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "david"
    correct_password = "9896"
    if not (credentials.username == correct_username and credentials.password == correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.post("/message")
async def post_message(message: Message, username: str = Depends(get_current_username)):
    try:
        credentials = pika.PlainCredentials('david', '9896')
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq', credentials=credentials))
        channel = connection.channel()

        channel.queue_declare(queue='messages', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='messages',
            body=message.content,
            properties=pika.BasicProperties(delivery_mode=2),
        )

        connection.close()
        return {"status": "Message published successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/openapi.json")
async def get_openapi():
    return app.openapi()