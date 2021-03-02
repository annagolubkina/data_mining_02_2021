from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Homeworks.database import models



class Database:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.maker = sessionmaker(bind=engine)

    def _get_or_create(self, session, model, uniq_field, uniq_value, **data):
        db_data = session.query(model).filter(uniq_field == uniq_value).first()
        if not db_data:
            db_data = model(**data)
            session.add(db_data)
            try:
                session.commit()
            except Exception as exc:
                print(exc)
                session.rollback()
        return db_data

    def _get_or_create_comments(self, session, data: list) -> list:
        result = []
        for comment in data:
            comment_author = self._get_or_create(
                session,
                models.Author,
                models.Author.url,
                comment["comment"]["user"]["url"],
                name=comment["comment"]["user"]["full_name"],
                url=comment["comment"]["user"]["url"],
            )
            db_comment = self._get_or_create(
                session,
                models.Comment,
                models.Comment.id,
                comment["comment"]["id"],
                **comment["comment"],
                author=comment_author,
            )

            result.append(db_comment)
            result.extend(self._get_or_create_comments(session, comment["comment"]["children"]))

        return result

    def create_post(self, data):
        session = self.maker()
        comments = self._get_or_create_comments(session, data["comments"])
        author = self._get_or_create(
            session,
            models.Author,
            models.Author.url,
            data["author"]["url"],
            **data["author"],
        )
        tags = map(
            lambda tag_data: self._get_or_create(
                session, models.Tag, models.Tag.url, tag_data["url"], **tag_data
            ),
            data["tags"],
        )
        post = self._get_or_create(
            session, models.Post, models.Post.url, "url", **data["post_data"], author=author
        )

        post.tags.extend(tags)
        post.comments.extend(comments)
        session.add(post)

        try:
            session.commit()
        except Exception as exc:
            print(exc)
            session.rollback()
        finally:
            session.close()
        print(1)