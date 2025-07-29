# cli/main.py
import typer
from app.commands import create, fix, list_drivers, initialize, login, update_driver

DEBUG = False

if DEBUG:
    app = typer.Typer(pretty_exceptions_short=False)
else:
    app = typer.Typer(pretty_exceptions_show_locals=False)

app.command("list_drivers")(list_drivers.run)
app.command("create")(create.run)
app.command("fix")(fix.run)  # placeholder if you reimplement fix later
app.command("login")(login.run)
app.command("initialize")(initialize.run)
app.command("update_driver")(update_driver.run)


if __name__ == "__main__":
    app()