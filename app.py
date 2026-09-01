"""
IntelliSQL - Intelligent SQL Querying with LLMs using Gemini Pro
Main Flask Application Entry Point
"""

from flask import Flask, render_template, request, jsonify, session
from gemini_handler import GeminiHandler
from database import DatabaseManager
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize core components
db_manager = DatabaseManager()
gemini = GeminiHandler()


@app.route("/")
def index():
    """Render main UI page."""
    schema = db_manager.get_schema_summary()
    return render_template("index.html", schema=schema)


@app.route("/query", methods=["POST"])
def query():
    """
    Main endpoint: Takes natural language → generates SQL → executes → returns results.
    """
    data = request.get_json()
    user_question = data.get("question", "").strip()

    if not user_question:
        return jsonify({"error": "Please enter a question."}), 400

    try:
        # Step 1: Get database schema to give Gemini context
        schema = db_manager.get_schema_text()

        # Step 2: Ask Gemini to generate SQL
        sql_query = gemini.generate_sql(user_question, schema)

        if not sql_query:
            return jsonify({"error": "Could not generate SQL. Try rephrasing your question."}), 400

        # Step 3: Execute the SQL on the database
        results, columns, row_count = db_manager.execute_query(sql_query)

        # Step 4: Ask Gemini to explain the results (optional but impressive)
        explanation = gemini.explain_results(user_question, sql_query, results[:3])

        # Step 5: Save to query history in session
        if "history" not in session:
            session["history"] = []

        session["history"].append({
            "id": str(uuid.uuid4())[:8],
            "question": user_question,
            "sql": sql_query
        })
        session.modified = True

        return jsonify({
            "success": True,
            "sql": sql_query,
            "columns": columns,
            "rows": results,
            "row_count": row_count,
            "explanation": explanation
        })

    except Exception as e:
        # Ask Gemini to explain the error too!
        error_hint = gemini.explain_error(str(e), user_question)
        return jsonify({
            "error": str(e),
            "hint": error_hint
        }), 500


@app.route("/history", methods=["GET"])
def history():
    """Return query history for current session."""
    return jsonify(session.get("history", []))


@app.route("/history", methods=["DELETE"])
def clear_history():
    """Clear query history."""
    session["history"] = []
    return jsonify({"success": True})


@app.route("/schema", methods=["GET"])
def schema():
    """Return full schema details for sidebar display."""
    return jsonify(db_manager.get_schema_dict())


@app.route("/execute-raw", methods=["POST"])
def execute_raw():
    """
    Execute a manually edited SQL query (user can tweak Gemini's output).
    """
    data = request.get_json()
    sql = data.get("sql", "").strip()

    if not sql:
        return jsonify({"error": "No SQL provided."}), 400

    # Safety check: only allow SELECT statements
    if not sql.upper().lstrip().startswith("SELECT"):
        return jsonify({"error": "Only SELECT queries are allowed for safety."}), 403

    try:
        results, columns, row_count = db_manager.execute_query(sql)
        return jsonify({
            "success": True,
            "columns": columns,
            "rows": results,
            "row_count": row_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Initialize database
db_manager.initialize()

if __name__ == "__main__":
    print("✅ IntelliSQL is running at http://localhost:5000")
    app.run(debug=True)
