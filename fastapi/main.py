from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from io import StringIO
from pandas import read_csv

from validation import validate, accuracy, ValidationError


app = FastAPI()
templates = Jinja2Templates(directory='templates')


@app.exception_handler(404)
async def not_found_exception(request: Request, error: HTTPException):
    return HTMLResponse(
        content=templates.TemplateResponse(
            'error.html', 
            {
                'request': request,
                'error': '404 Page Not Found',
            },
        ).body,
        status_code=404,
    )


@app.get('/', response_class=HTMLResponse)
async def render_upload_page(request: Request):
    return templates.TemplateResponse(
        'upload.html',
        { 'request': request },
    )


@app.post('/judge', response_class=HTMLResponse)
async def judge(request: Request, csv_file: UploadFile = File(...)):
    try:
        content = await csv_file.read()
        decoded = content.decode('utf-8')
        df      = read_csv(StringIO(decoded))

        validate(df)

        return templates.TemplateResponse(
            'result.html',
            {
                'request': request,
                'accuracy': accuracy(df),
            },
        )

    except ValidationError as error:
        return templates.TemplateResponse(
            'error.html',
            {
                'request': request,
                'error': str(error),
            },
            status_code=400,
        )


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8080)
