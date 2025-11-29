import google.generativeai as genai
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()

genai.configure(api_key=settings.GEMINI_API_KEY)

app = FastAPI()


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


@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meme Code Commenter</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
        }

        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2em;
        }

        .input-section, .output-section {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
            color: #555;
        }

        textarea {
            width: 100%;
            min-height: 250px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s;
        }

        textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        #output {
            background-color: #f8f9fa;
            color: #333;
        }

        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        button:active {
            transform: translateY(0);
        }

        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }

        .loading {
            text-align: center;
            color: #667eea;
            margin-top: 10px;
            font-weight: bold;
        }

        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 Meme Code Commenter 🎭</h1>

        <div class="input-section">
            <label for="input">Your Code:</label>
            <textarea id="input" placeholder="Paste your code here..."></textarea>
        </div>

        <button id="generateBtn" onclick="addComments()">Add Comments to Code</button>

        <div class="loading hidden" id="loading">⏳ Generating meme comments...</div>

        <div class="output-section">
            <label for="output">Commented Code:</label>
            <textarea id="output" readonly placeholder="Your beautifully commented code will appear here..."></textarea>
        </div>
    </div>

    <script>
        async function addComments() {
            const input = document.getElementById('input').value;
            const output = document.getElementById('output');
            const button = document.getElementById('generateBtn');
            const loading = document.getElementById('loading');

            if (!input.trim()) {
                alert('Please enter some code first!');
                return;
            }

            // Reset and prepare UI
            output.value = '';
            button.disabled = true;
            loading.classList.remove('hidden');

            try {
                const response = await fetch('/add-comments', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code: input })
                });

                if (!response.ok) {
                    throw new Error('Failed to generate comments');
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();

                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    output.value += chunk;
                    output.scrollTop = output.scrollHeight;
                }

            } catch (error) {
                console.error('Error:', error);
                output.value = 'Error generating comments. Please try again.';
            } finally {
                button.disabled = false;
                loading.classList.add('hidden');
            }
        }

        // Allow Enter key in textarea (Ctrl+Enter to submit)
        document.getElementById('input').addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                addComments();
            }
        });
    </script>
</body>
</html>
"""
