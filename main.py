from fastapi import FastAPI

#----------------------ROUTES-----------------------#

from models.auth.login import router as login_router
from models.auth.register import router as auth_router
from models.bank.me import router as me_router
from models.bank.transfer import router as transfer_router

#----------------------ROUTES-----------------------#

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from models.security.ratelimiter import custom_rate_limit_handler, limiter


from slowapi.errors import RateLimitExceeded

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)

app.add_middleware(SlowAPIMiddleware)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)
app.add_middleware(SlowAPIMiddleware)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"bank": "NTH-BANK"}


app.include_router(login_router)
app.include_router(auth_router)
app.include_router(me_router)
app.include_router(transfer_router)