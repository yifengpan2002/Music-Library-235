"""Initialize Flask app."""

from flask import Flask
from pathlib import Path
from music.adapters.memory_repository import *
import music.adapters.repository as repo
from music.adapters.repository import AbstractRepository, RepositoryException
from music.domainmodel.track import Track
from music.adapters.orm import *
from music.adapters import database_repository
from music.adapters import repository_populate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.pool import NullPool

def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object('config.Config')

    # tests are conducted here
    if test_config is not None:
        app.config.from_mapping(test_config)
        data_path = app.config['TEST_DATA_PATH']
        repo.repo_instance = MemoryRepository(data_path)
    if app.config['REPOSITORY'] == 'memory':
        data_path = Path('music') / 'adapters' / 'data'
        repo.repo_instance = MemoryRepository(data_path)
    elif app.config['REPOSITORY'] == 'database':
        database_uri = app.config['SQLALCHEMY_DATABASE_URI']
        database_echo = app.config['SQLALCHEMY_ECHO']
        #need to install sqlalchemy package
        database_engine = create_engine(database_uri, connect_args={"check_same_thread": False}, poolclass=NullPool,
                                        echo=database_echo)
        seesion_factory = sessionmaker(autocommit=False, autoflush=True,bind=database_engine)
        repo.repo_instance = database_repository.SqlAlchemyRepository(seesion_factory)

        if app.config['TESTING'] == "True" or len(database_engine.table_names()) == 0:
            print("Repopulating Databse...")
            clear_mappers() #clear any object between our domain model and databse table
            #metadata is a global object that hold databse schema, this is in orm.py
            metadata.create_all(database_engine)
            data_path = Path('music') / 'adapters' / 'data'
            #delete the data in the table if it exist
            for table in reversed(metadata.sorted_tables):
                database_engine.execute(table.delete())
            map_model_to_tables() #this is the method we defined!!! orm mapping
            database_mode = True
            repository_populate.populate(data_path, repo.repo_instance)
        else:
            map_model_to_tables()



    # Register blueprints.
    with app.app_context():
        from .home import home
        app.register_blueprint(home.home_blueprint)

        from .authentication import authentication
        app.register_blueprint(authentication.authBlueprint)

        from .browse import browse
        app.register_blueprint(browse.browse_blueprint)

        from .search import search
        app.register_blueprint(search.searchBlueprint)

        from .favorites import favorites
        app.register_blueprint(favorites.favorite_blueprint)

    @app.before_request
    def before_flask_http_request_function():
        if isinstance(repo.repo_instance, database_repository.SqlAlchemyRepository):
            repo.repo_instance.reset_session()

    # Register a tear-down method that will be called after each request has been processed.
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if isinstance(repo.repo_instance, database_repository.SqlAlchemyRepository):
            repo.repo_instance.close_session()

    return app
