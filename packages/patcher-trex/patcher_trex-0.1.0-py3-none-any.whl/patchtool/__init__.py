from .sos import sso 
from .acllm import full_file, Query
from .acllm import AddComments, modif, extract_raw_code
import typer

app = typer.Typer()

@app.command()
def searcherr(filepath: str):
    """Search errors related to the file on Stack Overflow and open them."""
    sso(filepath=filepath)

@app.command()
def fix(filepath: str):
    """Run the file and auto-correct errors using AI."""
    full_file(filepath=filepath)

@app.command()
def modify(filepath: str):
    """Modify the code based on user input instructions."""
    modif(filepath=filepath)

@app.command()
def query(filetype: str):
    """Generate code based on user input query and save it as filetype."""
    Query(filetype)

@app.command()
def addComments(filepath: str):
    """Add comments to the code without changing functionality."""
    AddComments(filepath)

if __name__ == "__main__":
    app()
