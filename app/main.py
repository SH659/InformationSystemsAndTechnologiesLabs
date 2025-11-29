import google.generativeai as genai
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()

genai.configure(api_key=settings.GEMINI_API_KEY)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class CodeRequest(BaseModel):
    code: str


COMMENT_PROMPT = """You are a meme comment generator. Add absurd, satirical one-liner comments to the provided code.

RULES:
1. Return ONLY the code with added comments - NO explanations, NO conversation, NO markdown formatting
2. Keep ALL comments SHORT (max 60 characters) - one shot, one hit jokes only
3. MUST fit within 120 character total line width (code + comment)
4. Comment themes (use variety):
   - Divine prayers to save code from bugs ("// Lord have mercy on this function")
   - Satirical jabs at ALL nationalities and genders equally ("// Written by a confused Apache helicopter")
   - Mock ALL operating systems ("// Works on my machine (Linux cultist cope)")
   - Conspiracy theories ("// Reptilians wrote this in 1947")
   - Absurd observations ("// This line runs on vibes only")
5. Keep original code structure intact, only add inline comments
6. Do NOT wrap output in markdown code blocks
7. Place comments at END of lines when possible to save vertical space

User's code to comment:

{code}"""


async def generate_stream(code: str):
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = COMMENT_PROMPT.format(code=code)

    response = await model.generate_content_async(prompt, stream=True)

    async for chunk in response:
        if chunk.text:
            yield chunk.text


@app.post("/add-comments")
async def add_comments(request: CodeRequest):
    return StreamingResponse(
        generate_stream(request.code),
        media_type="text/plain"
    )


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
