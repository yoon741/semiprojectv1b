import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.dbfactory import get_db
from app.schema.gallery import NewGallery
# from app.service.gallery import GalleryService

gallery_router = APIRouter()
templates = Jinja2Templates(directory='views/templates')


@gallery_router.get('/list/{cpg}', response_class=HTMLResponse)
async def list(req: Request,db: Session = Depends(get_db)):
    try:
        return templates.TemplateResponse('gallery/list.html', {'request': req})


    except Exception as ex:
        print(f'▶▶▶list 오류 발생 : {str(ex)}')
        return RedirectResponse(url='/member/error', status_code=303)

@gallery_router.get('/write', response_class=HTMLResponse)
async def write(req: Request):
    return templates.TemplateResponse('gallery/write.html', {'request': req})

@gallery_router.post('/write', response_class=HTMLResponse)
async def write(req: Request, title: str = Form(...), userid: str = Form(...),
                contents: str = Form(...), files: List[UploadFile] = File(...) ): # 맞는 형식으로 post되었는지 확인
    print(title, userid, contents)
    print(files)

    UPLOAD_PATH = 'C:/Java/nginx-1.26.2/html/cdn/img/'  # 저장경로
    attachs = []  # 업로드된 파일정보를 저장하기 위해 리스트 생성
    today = datetime.today().strftime('%Y%m%d%H%M%S')  # UUID 생성 유니크한 고유식별코드
                                            # 내가올린 파일과 다른사람이 올린 파일이름이 같을 경우 겹치지 않기 위해 날짜시간 붙여서 생성
    for file in files:
        if file.filename != '' and file.size > 0:
            nfname = f'{today}{file.filename}'  # new file name
            # os.path.join(A,B) => A/B (경로생성 함수)
            fname = os.path.join(UPLOAD_PATH, nfname)   # 업로드할 파일경로 생성
            content = await file.read()     # 업로드할 파일의 내용을 비동기로 읽음
            with open(fname, 'wb') as f:    # 바이너리 형식으로 저장되어 기록됨
                f.write(content)    # 기록
            attach = [nfname, file.size]    # 업로드된 파일 정보를 리스트에 저장
            attachs.append(attach)

    print(attachs)

    return templates.TemplateResponse('gallery/write.html', {'request': req})

@gallery_router.get('/view', response_class=HTMLResponse)
async def view(req: Request):
    return templates.TemplateResponse('gallery/view.html', {'request': req})