from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "geovanny-gk-chave-secreta"

DATABASE = "curso_geovanny.db"


def criar_banco():
    conexao = sqlite3.connect(DATABASE)
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilizadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            nascimento TEXT NOT NULL,
            genero TEXT NOT NULL,
            telefone_email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    mensagem = ""

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        nascimento = request.form.get("nascimento", "").strip()
        genero = request.form.get("genero", "").strip()
        telefone_email = request.form.get("telefone_email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirmar = request.form.get("confirmar", "")

        if not all([
            nome,
            nascimento,
            genero,
            telefone_email,
            username,
            password,
            confirmar
        ]):
            mensagem = "Preencha todos os campos."

        elif password != confirmar:
            mensagem = "As palavras-passe não coincidem."

        elif len(password) < 6:
            mensagem = "A palavra-passe deve ter pelo menos 6 caracteres."

        else:
            conexao = sqlite3.connect(DATABASE)
            cursor = conexao.cursor()

            try:
                password_segura = generate_password_hash(password)

                cursor.execute("""
                    INSERT INTO utilizadores
                    (nome, nascimento, genero, telefone_email, username, password)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    nome,
                    nascimento,
                    genero,
                    telefone_email,
                    username,
                    password_segura
                ))

                conexao.commit()
                conexao.close()

                return redirect(url_for("login"))

            except sqlite3.IntegrityError:
                conexao.close()
                mensagem = "Este telefone/e-mail ou nome de utilizador já está registado."

    return render_template("cadastro.html", mensagem=mensagem)


@app.route("/login", methods=["GET", "POST"])
def login():
    mensagem = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conexao = sqlite3.connect(DATABASE)
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT id, nome, username, password
            FROM utilizadores
            WHERE username = ?
        """, (username,))

        utilizador = cursor.fetchone()
        conexao.close()

        if utilizador and check_password_hash(utilizador[3], password):
            session["utilizador_id"] = utilizador[0]
            session["nome"] = utilizador[1]
            session["username"] = utilizador[2]

            return redirect(url_for("cursos"))

        mensagem = "Nome de utilizador ou palavra-passe incorretos."

    return render_template("login.html", mensagem=mensagem)


@app.route("/cursos")
def cursos():
    if "utilizador_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "cursos.html",
        nome=session.get("nome")
    )


@app.route("/sair")
def sair():
    session.clear()
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    criar_banco()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
