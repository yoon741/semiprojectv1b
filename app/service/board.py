from sqlalchemy import select, or_, update, values
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, contains_eager

from app.model.board import Board, Reply


class BoardService:
    @staticmethod
    def select_board(db, cpg):
        try:
            stbno = (cpg - 1) * 25
            stmt = select(Board.bno, Board.title, Board.userid,
                          Board.regdate, Board.views)\
                    .order_by(Board.bno.desc())\
                    .offset(stbno).limit(25)
            result = db.execute(stmt)

            return result

        except SQLAlchemyError as ex:
            print(f'▸▸▸select_board 오류발생 : {str(ex)}')


    @staticmethod
    def selectone_board(bno, db):
        try:
            # 본문글에 대한 조회수 증가
            # update board sey views = views + 1
            # where bno = ?
            stmt = update(Board).where(Board.bno == bno)\
                    .values(views = Board.views + 1)
            db.execute(stmt)

            # 본문글 + 댓글 읽어오기
            stmt = select(Board).join(Board.replys)\
                .options(contains_eager(Board.replys))\
                .where(Board.bno == bno)\
                .order_by(Reply.rpno)

            result = db.execute(stmt).scalars().first()

            db.commit()  # 위 두작업이 모두 정상적으로 완료되면 commit
            return result


        except SQLAlchemyError as ex:
            print(f'▸▸▸selectone_board 오류발생 : {str(ex)}')
            db.rollback()


    @staticmethod
    def find_select_board(db, ftype, fkey, cpg):
        try:
            stbno = (cpg - 1) * 25
            stmt = select(Board.bno, Board.title, Board.userid,
                          Board.regdate, Board.views)

            # 동적 쿼리 작성 - 조건에 따라 where 절이 바뀜
            # 제목 : where title = ?
            # 작성자 : where userid = ?
            # 본문 : where contents = ?
            # 제목 + 본문 : where title = ? or contents = ?
            myfilter = Board.title.like(fkey)
            if ftype == 'userid': myfilter = Board.userid.like(fkey)
            elif ftype == 'contents': myfilter = Board.contents.like(fkey)
            elif ftype == 'titcont': myfilter = \
                or_(Board.title.like(fkey), Board.contents.like(fkey))

            stmt = stmt.filter(myfilter)\
                .order_by(Board.bno.desc()) \
                .offset(stbno).limit(25)
            result = db.execute(stmt)

            return result

        except SQLAlchemyError as ex:
            print(f'▸▸▸find_select_board 오류발생 : {str(ex)}')

