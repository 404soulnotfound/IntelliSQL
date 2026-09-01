# ⚡ IntelliSQL — Intelligent SQL Querying with LLMs
## SmartBridge Generative AI with Google — Course Project

---

## 🎯 What Is This Project?

IntelliSQL is a web application that lets anyone query a database using
plain English — no SQL knowledge required.

You type: "Show me top 5 customers by total spending"
Gemini Pro writes the SQL, executes it, and explains what the results mean.

---

## 🔑 Why It's Unique

| Feature                  | Description                                               |
|--------------------------|-----------------------------------------------------------|
| Gemini Pro integration   | Uses Google's state-of-the-art LLM to write SQL           |
| Schema-aware prompting   | Sends real table/column names to Gemini for accuracy      |
| Result explanation       | Gemini explains what the results mean in plain English    |
| Error diagnosis          | If SQL fails, Gemini tells you why and how to fix it      |
| Editable SQL             | User can edit Gemini's output and re-run it               |
| Query history            | Session-based history of all your questions               |
| CSV export               | Download results with one click                           |
| Real database            | Uses SQLite with realistic e-commerce + HR sample data    |

---

## 🏗️ Architecture

```
User Question (English)
       │
       ▼
  Flask Backend (app.py)
       │
       ├──► GeminiHandler.generate_sql()
       │         │
       │         ▼
       │    Gemini Pro API
       │    (Natural Language → SQL)
       │         │
       │         ▼
       ├──► DatabaseManager.execute_query()
       │         │
       │         ▼
       │    SQLite Database
       │    (Runs the SQL)
       │         │
       │         ▼
       └──► GeminiHandler.explain_results()
                 │
                 ▼
            Response to Frontend
            (SQL + Results + Explanation)
```

---


---

## 🚀 How to Run

### Step 1: Get Gemini API Key
Go to: https://makersuite.google.com/app/apikey
Create a key and copy it.

### Step 2: Set up the project
```bash
cd intellisql
pip install -r requirements.txt
```

### Step 3: Create .env file
```
GEMINI_API_KEY=your_key_here
```

### Step 4: Run the app
```bash
python app.py
```

### Step 5: Open browser
Go to: http://localhost:5000

---

## 🗄️ Database Tables

### customers
customer_id, name, email, country, city, age, created_at

### products
product_id, name, category, price, stock, supplier

### orders
order_id, customer_id, order_date, status, total_amount

### order_items
item_id, order_id, product_id, quantity, unit_price

### employees
employee_id, name, department, salary, hire_date, manager_id

---

## 💬 Sample Questions to Try

- Show all customers from India
- Top 5 products by total revenue
- Total orders per country
- Average salary by department
- Customers who spent more than 10000
- Products with stock less than 100
- Orders placed in last 90 days
- Show employees and their manager names

---

## 🧠 Key Concepts Used

1. **Prompt Engineering** — Carefully crafted prompts give Gemini the schema
   and rules it needs to generate accurate SQL every time.

2. **Schema-Aware Context** — We send the full table/column list to Gemini
   so it never hallucinates column names.

3. **Temperature Control** — Low temperature (0.1) makes Gemini deterministic,
   reducing random variation in SQL output.

4. **Error Recovery** — When SQL fails, we ask Gemini to diagnose the error
   and suggest a fix in plain English.

5. **Safety Layer** — Only SELECT queries can be executed, preventing any
   accidental data modification.

---

## 📊 Project Outcomes

After building this project you will understand:
- How to integrate Gemini Pro API into a Python app
- Prompt engineering for structured output (SQL)
- Flask REST API design
- SQLite database operations
- Session management
- Full-stack web development

---

## Live Link
