from fastapi import FastAPI, File, UploadFile

from handler import detect_waldo


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Exist-Waldo"],
)

@app.post("/detect")
async def detect_route(file: UploadFile = File(...)):
    return await detect_waldo(file)
