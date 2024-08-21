from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError

from app.model.member import Member


class MemberService:
    @staticmethod
    def insert_member(db, member):
        try:
            stmt = insert(Member).values(
                userid=member.userid, passwd=member.passwd,
                name=member.name, email=member.email)
            result = db.execute(stmt)
            db.flush()
            db.commit()  # 정상처리될 경우 commit후 return
            return result

        except SQLAlchemyError as ex:   # 예외처리 코드
            print(f'▶▶▶ insert_member 오류발생: {str(ex)}')
            db.rollback()      # 정상처리되지 않을 경우 rollback
