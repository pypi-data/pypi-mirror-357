import typer
from . import encrypt as e, decrypt as d
from typing_extensions import Annotated

app = typer.Typer(help="An easy and fun encryption module.")

@app.command()
def encrypt(
    message: str,
    shift: Annotated[
        int,
        typer.Option(
            help="Shift database to make the ciphered text more difficult to decode"
        ),
    ] = 0
):
    """
    Encrypts a message
    """
    print(e(message, shift=shift))


@app.command()
def decrypt(
    message: str,
    shift: Annotated[
        int,
        typer.Option(
            help="Shift database if the message was encoded with a shifted database"
        ),
    ] = 0
):
    """
    Decrypts a SweeCrypt-encoded message
    """
    print(d(message, shift=shift))


if __name__ == "__main__":
    app()
