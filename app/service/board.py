from sqlalchemy import select, or_, update, values, insert, func
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
            # join을 사용하면 글과 댓글이 있는 경우에만 볼수 있게 출력 됨 때문에
            # outerjoin를 사용하여 댓글이 없는 글도 보이게 설정해야함
            # outerjoin: outer join
            # contains_eager : 관계 맺은 하위 객체의 내용 즉시 로딩
            stmt = select(Board).outerjoin(Board.replys)\
                .options(contains_eager(Board.replys))\
                .where(Board.bno == bno)\
                .order_by(Reply.rpno)

            result = db.execute(stmt)
            db.commit()  # 위 두작업이 모두 정상적으로 완료되면 commit

            return result.scalars().first()


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

    @staticmethod
    def insert_reply(db, rp):
        try:
            # 댓글 추가시 생성될 댓글번호 예측
            # select coalesce(max(rno), 0) + 1 from reply;  < coalesce: null일때 0으로 처리
            stmt = select(func.coalesce(func.max(Reply.rno), 0) + 1)
            next_rno = db.execute(stmt).scalar_one()  # .scalar_one(): 단일값

            stmt = insert(Reply).values(userid=rp.userid,
                    reply=rp.reply, bno=rp.bno, rpno=next_rno)
            result = db.execute(stmt)

            db.commit()
            return result

        except SQLAlchemyError as ex:
            print(f'▸▸▸insert_reply 오류발생 : {str(ex)}')
            db.rollback()