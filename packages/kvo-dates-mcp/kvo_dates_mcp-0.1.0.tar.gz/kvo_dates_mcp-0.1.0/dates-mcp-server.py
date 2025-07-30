import dotenv

dotenv.load_dotenv(verbose=True, override=True)

from kvo.datesmcp.cli import app


if __name__ == '__main__':
    app()
