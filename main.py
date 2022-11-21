import datetime
import random

from PIL import Image
import PIL.ImageOps
import uvicorn
from fastapi import FastAPI, Header, Request, File, UploadFile
from typing import Union
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse
import io

app = FastAPI()
templates = Jinja2Templates(directory="templates")

users_database = {
    "user1": "1305485a712608fdc4d2fd1780c72919f2f54cf288525814bff7120737f6ddad"  # password - qweasdzxc
}


@app.get("/")
def redirect_to_docs():
    return RedirectResponse(url='/docs')


@app.get("/today/")
async def todays_date(username: Union[str, None] = Header(default=None),
                      password: Union[str, None] = Header(default=None)):
    if username not in users_database:
        return "Something went wrong during authentication"
    if password != users_database[username]:
        return "Something went wrong during authentication - password"
    return str(datetime.datetime.now())


@app.get("/primenumber/{n}")
async def prime_number(n: int) -> bool:
    if not isinstance(n, int):
        return {"Please pass an integer"}

    elif n <= 0 or n > 9223372036854775807:
        return {"Please pass a number ranging from 1 to 9223372036854775807"}

    def binpower(a, b, n):
        if b == 0:
            return 1
        if b % 2 == 0:
            return binpower(a * a % n, b // 2, n)
        else:
            return a * binpower(a * a % n, b // 2, n) % n

    def check_composite(n, a, d, s):
        x = binpower(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for r in range(1, s):
            x = binpower(x, 2, n)
            if x == n - 1:
                return False
        return True

    def MillerRabin_PrimalityTesting(n, iter=5):
        if n < 4:
            return n == 2 or n == 3
        s = 0

        d = n - 1
        while d % 2 == 0:
            d //= 2
            s += 1

        for i in range(iter):
            a = 2 + random.randint(0, n - 3)
            if check_composite(n, a, d, s):
                return False
        return True

    return True if MillerRabin_PrimalityTesting(n) else False


@app.get("/picture/invert_form/", response_class=FileResponse)
async def invert_image_form(request: Request):
    return templates.TemplateResponse("revert_picture_form.html", {"request": request})


@app.post("/invert_image")
async def invert_image(file: UploadFile = File()):
    image = Image.open(io.BytesIO(file.file.read()))
    inverted_image = PIL.ImageOps.invert(image)
    responseImage = io.BytesIO()
    inverted_image.save(responseImage, "JPEG")
    responseImage.seek(0)
    return StreamingResponse(responseImage, media_type="image/jpeg")


if __name__ == '__main__':
    uvicorn.run(app, limit_max_requests=50)
