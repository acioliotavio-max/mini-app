from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "chave-secreta-tarefas"

DATABASE = "tarefas.db"


def conectar_banco():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela():
    conexao = conectar_banco()

    conexao.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            status TEXT NOT NULL DEFAULT 'Pendente'
        )
    """)

    conexao.commit()
    conexao.close()


@app.route("/")
def index():
    status_filtro = request.args.get("status", "Todas")

    conexao = conectar_banco()

    if status_filtro in ["Pendente", "Concluída"]:
        tarefas = conexao.execute(
            "SELECT * FROM tarefas WHERE status = ? ORDER BY id DESC",
            (status_filtro,)
        ).fetchall()
    else:
        tarefas = conexao.execute(
            "SELECT * FROM tarefas ORDER BY id DESC"
        ).fetchall()

    conexao.close()

    return render_template(
        "index.html",
        tarefas=tarefas,
        status_filtro=status_filtro
    )


@app.route("/adicionar", methods=["POST"])
def adicionar():
    titulo = request.form.get("titulo", "").strip()
    descricao = request.form.get("descricao", "").strip()

    if not titulo:
        flash("O título da tarefa é obrigatório.", "erro")
        return redirect(url_for("index"))

    conexao = conectar_banco()

    conexao.execute(
        """
        INSERT INTO tarefas (titulo, descricao, status)
        VALUES (?, ?, ?)
        """,
        (titulo, descricao, "Pendente")
    )

    conexao.commit()
    conexao.close()

    flash("Tarefa adicionada com sucesso!", "sucesso")
    return redirect(url_for("index"))


@app.route("/alterar-status/<int:tarefa_id>", methods=["POST"])
def alterar_status(tarefa_id):
    conexao = conectar_banco()

    tarefa = conexao.execute(
        "SELECT status FROM tarefas WHERE id = ?",
        (tarefa_id,)
    ).fetchone()

    if tarefa is None:
        conexao.close()
        flash("Tarefa não encontrada.", "erro")
        return redirect(url_for("index"))

    novo_status = (
        "Concluída"
        if tarefa["status"] == "Pendente"
        else "Pendente"
    )

    conexao.execute(
        "UPDATE tarefas SET status = ? WHERE id = ?",
        (novo_status, tarefa_id)
    )

    conexao.commit()
    conexao.close()

    flash("Status da tarefa atualizado!", "sucesso")
    return redirect(url_for("index"))


@app.route("/editar/<int:tarefa_id>", methods=["GET", "POST"])
def editar(tarefa_id):
    conexao = conectar_banco()

    tarefa = conexao.execute(
        "SELECT * FROM tarefas WHERE id = ?",
        (tarefa_id,)
    ).fetchone()

    if tarefa is None:
        conexao.close()
        flash("Tarefa não encontrada.", "erro")
        return redirect(url_for("index"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()

        if not titulo:
            conexao.close()
            flash("O título da tarefa é obrigatório.", "erro")
            return redirect(url_for("editar", tarefa_id=tarefa_id))

        conexao.execute(
            """
            UPDATE tarefas
            SET titulo = ?, descricao = ?
            WHERE id = ?
            """,
            (titulo, descricao, tarefa_id)
        )

        conexao.commit()
        conexao.close()

        flash("Tarefa alterada com sucesso!", "sucesso")
        return redirect(url_for("index"))

    conexao.close()

    return render_template("editar.html", tarefa=tarefa)


@app.route("/excluir/<int:tarefa_id>", methods=["POST"])
def excluir(tarefa_id):
    conexao = conectar_banco()

    tarefa = conexao.execute(
        "SELECT id FROM tarefas WHERE id = ?",
        (tarefa_id,)
    ).fetchone()

    if tarefa is None:
        conexao.close()
        flash("Tarefa não encontrada.", "erro")
        return redirect(url_for("index"))

    conexao.execute(
        "DELETE FROM tarefas WHERE id = ?",
        (tarefa_id,)
    )

    conexao.commit()
    conexao.close()

    flash("Tarefa excluída com sucesso!", "sucesso")
    return redirect(url_for("index"))


if __name__ == "__main__":
    criar_tabela()
    app.run(debug=True)