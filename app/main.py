from fastapi import FastAPI

app = FastAPI(title="Gerenciador de Campanhas")


@app.get("/health")
def health():
    return {"status": "ok"}
