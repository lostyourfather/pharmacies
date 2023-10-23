from fastapi import FastAPI


app = FastAPI()


async def start_up():
    pass

@app.get('/')
async def root():
    return "Hello"

