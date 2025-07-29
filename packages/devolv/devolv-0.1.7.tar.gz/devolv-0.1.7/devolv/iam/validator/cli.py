import typer
from typer import Exit
import os
from devolv.iam.validator.core import validate_policy_file
from devolv.iam.validator.folder import validate_policy_folder
from devolv import __version__


app = typer.Typer(help="IAM Policy Validator CLI")

@app.command("validate")
def validate(path: str):
    if not os.path.exists(path):
        typer.secho(f"❌ Path not found: {path}", fg=typer.colors.RED)
        raise Exit(code=1)

    if os.path.isfile(path):
        findings = validate_policy_file(path)
        if not findings:
            typer.secho("✅ Policy is valid and passed all checks.", fg=typer.colors.GREEN)
            raise Exit(code=0)
        for finding in findings:
            typer.secho(f"❌ {finding['level'].upper()}: {finding['message']}", fg=typer.colors.RED)
        raise Exit(code=1)

    elif os.path.isdir(path):
        findings = validate_policy_folder(path)
        if not findings:
            typer.secho("✅ All policies passed validation.", fg=typer.colors.GREEN)
            raise Exit(code=0)
        for finding in findings:
            typer.secho(f"❌ {finding['level'].upper()}: {finding['message']}", fg=typer.colors.RED)
        if any(f["level"] == "error" for f in findings):
            raise Exit(code=1)
        raise Exit(code=0)

    else:
        typer.secho(f"❌ Unsupported path type: {path}", fg=typer.colors.RED)
        raise Exit(code=1)  
    
