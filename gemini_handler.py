"""
IntelliSQL - Gemini Pro Handler
Manages all interactions with Google's Gemini Pro LLM.
"""

import google.generativeai as genai
import os
import re


class GeminiHandler:
    """
    Handles all Gemini Pro API calls:
    - Natural language → SQL conversion
    - Result explanation
    - Error diagnosis
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")

        genai.configure(api_key=api_key)

        # Use Gemini Pro model
        self.model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config={
                "temperature": 0.1,      # Low = more deterministic SQL output
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024
            }
        )

    # ─────────────────────────────────────────────
    # 1. NATURAL LANGUAGE → SQL
    # ─────────────────────────────────────────────

    def generate_sql(self, user_question: str, schema: str) -> str:
        """
        Converts a plain English question to a valid SQL query.

        Args:
            user_question: What the user wants to know
            schema: Database schema text so Gemini knows table/column names

        Returns:
            Clean SQL query string
        """

        prompt = f"""
You are an expert SQL assistant. Your job is to convert natural language questions 
into accurate SQLite SQL queries based on the provided database schema.

DATABASE SCHEMA:
{schema}

RULES:
1. Return ONLY the SQL query — no explanation, no markdown, no backticks.
2. Use only table and column names that exist in the schema above.
3. Always use proper SQL syntax compatible with SQLite.
4. Use table aliases for readability (e.g., c for customers).
5. Add LIMIT 100 if the query may return many rows.
6. Use LOWER() for case-insensitive text comparisons.
7. For date queries, use SQLite date functions like DATE(), strftime().

USER QUESTION:
{user_question}

SQL QUERY:
"""

        response = self.model.generate_content(prompt)
        sql = response.text.strip()

        # Clean up any accidental markdown formatting
        sql = self._clean_sql(sql)
        return sql

    # ─────────────────────────────────────────────
    # 2. EXPLAIN RESULTS IN PLAIN ENGLISH
    # ─────────────────────────────────────────────

    def explain_results(self, question: str, sql: str, sample_rows: list) -> str:
        """
        Explains what the query results mean in plain English.

        Args:
            question: Original user question
            sql: The SQL that was generated
            sample_rows: First few rows of results (to keep prompt short)

        Returns:
            Human-readable explanation of results
        """

        if not sample_rows:
            return "The query returned no results."

        prompt = f"""
You are a data analyst explaining database query results to a non-technical user.

Original question: "{question}"
SQL used: {sql}
Sample results (first few rows): {sample_rows}

In 2-3 sentences, explain what these results mean in simple, friendly language.
Do not repeat the SQL. Focus on what the data tells us.
"""

        response = self.model.generate_content(prompt)
        return response.text.strip()

    # ─────────────────────────────────────────────
    # 3. DIAGNOSE SQL ERRORS
    # ─────────────────────────────────────────────

    def explain_error(self, error_msg: str, question: str) -> str:
        """
        When a SQL query fails, Gemini explains what went wrong and suggests a fix.

        Args:
            error_msg: The SQLite error message
            question: Original user question

        Returns:
            Friendly error explanation with suggested fix
        """

        prompt = f"""
A SQL query failed with this error: "{error_msg}"
The user was asking: "{question}"

In 1-2 sentences, explain what went wrong in simple terms and suggest how 
the user could rephrase their question to get better results.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return "Please try rephrasing your question with more specific details."

    # ─────────────────────────────────────────────
    # HELPER: Clean SQL output
    # ─────────────────────────────────────────────

    def _clean_sql(self, sql: str) -> str:
        """
        Strips markdown formatting that Gemini sometimes adds.
        e.g., removes ```sql ... ``` wrappers
        """
        # Remove markdown code blocks
        sql = re.sub(r"```sql\s*", "", sql)
        sql = re.sub(r"```\s*", "", sql)

        # Remove any leading/trailing whitespace
        sql = sql.strip()

        # If Gemini added explanation text before the SQL, extract just the SQL
        lines = sql.split("\n")
        sql_lines = []
        capture = False

        for line in lines:
            upper = line.strip().upper()
            if upper.startswith("SELECT") or upper.startswith("WITH"):
                capture = True
            if capture:
                sql_lines.append(line)

        if sql_lines:
            return "\n".join(sql_lines).strip()

        return sql
