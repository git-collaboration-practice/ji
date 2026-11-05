
from flask import Flask, request, jsonify
from pathlib import Path
import sqlite3

app = Flask(__name__)

# Git 저장소 외부에 데이터베이스 보관
DATA_DIR = Path("/home/ubuntu/todo-data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "todo.db"


# 데이터베이스 초기화
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        """)


# 1. Todo 전체 조회
@app.route("/api/todos", methods=["GET"])
def get_todos():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT id, title, completed
            FROM todos
            ORDER BY id DESC
        """)

        todos = [
            {
                "id": row[0],
                "title": row[1],
                "completed": bool(row[2])
            }
            for row in cursor.fetchall()
        ]

    return jsonify(todos)


# 2. Todo 추가
@app.route("/api/todos", methods=["POST"])
def add_todo():
    data = request.get_json(silent=True) or {}
    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        return jsonify({
            "error": "할 일을 입력하세요."
        }), 400

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO todos (title) VALUES (?)",
            (title.strip(),)
        )
        todo_id = cursor.lastrowid

    return jsonify({
        "success": True,
        "id": todo_id
    }), 201


# 3. Todo 삭제
@app.route("/api/todos/<int:todo_id>",
           methods=["DELETE"])
def delete_todo(todo_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "DELETE FROM todos WHERE id = ?",
            (todo_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "error": "존재하지 않는 할 일입니다."
            }), 404

    return jsonify({"success": True})


# Gunicorn 실행 시에도 DB 초기화
init_db()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
