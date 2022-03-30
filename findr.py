from app import create_app, db
from app.Model.models import Post, Language, Field, Class
from config import Config

app = create_app(Config)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Post': Post}

@app.before_first_request
def initDB(*args, **kwargs):
    db.create_all()
    if Language.query.count() == 0:
        languages = ['C', 'C++', 'Java', 'Haskell', 'Python']
        for t in languages:
            db.session.add(Language(name=t))
        db.session.commit()
    if Field.query.count() == 0:
        fields = ['Math', 'Physics', 'Artificial Intelligence', 'Memes']
        for f in fields:
            db.session.add(Field(name=f))
        db.session.commit()
    if Class.query.count() == 0:
        classes = [('HIST395', 'History of Drugs'),
                   ('MUS262', 'History of Rock and Roll'),
                   ('ASTRONOM450', 'Life in the Universe')]
        for c in classes:
            newClass = Class(coursenum = c[0], title = c[1])
            db.session.add(newClass)
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)
