# Rule Engine with AST Implementation

## Table of Contents
1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Components](#components)
5. [API Documentation](#api-documentation)
6. [Rule Structure](#rule-structure)
7. [Test Cases](#test-cases)
8. [Error Handling](#error-handling)
9. [Troubleshooting](#troubleshooting)

## Overview
This project implements a 3-tier rule engine application using Abstract Syntax Trees (AST) to evaluate rules based on various user-defined attributes such as age, department, income, and more. The rule engine allows users to create, combine, and evaluate complex rules via a RESTful API, which can be integrated into various systems.

## Project Structure
```bash
project_root/
├── main.py                 # Flask application and API endpoints
├── requirements.txt        # Project dependencies
├── utils/
│   └── ast_utils.py       # AST implementation and utilities
├── static/
│   ├── css/
│   │   └── styles.css     # Application styling
│   └── js/
│       └── main.js        # Frontend functionality
├── templates/
│   └── index.html         # Main application interface
└── .env                   # Environment variables
```

## Installation

### Step 1: Clone the repository
```bash
git clone <repository-url>
cd rule-engine
```

### Step 2: Set up the virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Set environment variables
Create a `.env` file and set up your environment variables:
```bash
DATABASE_URL=sqlite:///rules.db
```

### Step 4: Run the application
```bash
python main.py
```

The application will start on `http://127.0.0.1:3000` (or the specified port) and can be accessed via the browser or API clients.

## Components

### 1. **AST Node Structure**
The core structure of the rule engine is based on an Abstract Syntax Tree (AST). Here's a simplified node structure:
```python
class Node:
    def __init__(self, type, value=None, left=None, right=None):
        self.type = type        # 'operator' or 'condition'
        self.value = value      # Operator (AND/OR) or condition string
        self.left = left        # Left child node
        self.right = right      # Right child node
```

### 2. **Database Schema**
The rules are stored in an SQLite database with the following schema:
```python
class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), unique=True, nullable=False)
    rule_ast = db.Column(db.PickleType, nullable=False)
```

## API Documentation

### 1. **Create Rule**
- **Endpoint:** `/api/rules/create_rule`
- **Method:** POST
- **Description:** Creates a new rule from a rule string.
- **Request Example:**
  ```json
  {
      "ruleName": "rule1",
      "ruleString": "(age > 30 AND department = 'Sales')"
  }
  ```
- **Response Example:**
  ```json
  {
      "ruleName": "rule1",
      "id": 1,
      "tree": {
          "type": "operator",
          "value": "AND",
          "left": {
              "type": "condition",
              "value": "age > 30"
          },
          "right": {
              "type": "condition",
              "value": "department = 'Sales'"
          }
      }
  }
  ```

### 2. **Combine Rules**
- **Endpoint:** `/api/rules/combine_rules`
- **Method:** POST
- **Description:** Combines multiple rules using a logical operator.
- **Request Example:**
  ```json
  {
      "rules": ["rule1", "rule2"],
      "op": "AND"
  }
  ```
- **Response Example:**
  ```json
  {
      "ruleName": "combined_rule",
      "id": 2,
      "tree": {
          "type": "operator",
          "value": "AND",
          "left": {...},
          "right": {...}
      }
  }
  ```

### 3. **Evaluate Rule**
- **Endpoint:** `/api/rules/evaluate_rule`
- **Method:** POST
- **Description:** Evaluates a rule against user-provided data.
- **Request Example:**
  ```json
  {
      "ast": "rule1",
      "data": {
          "age": 35,
          "department": "Sales"
      }
  }
  ```
- **Response Example:**
  ```json
  {
      "result": true,
      "tree": {...}
  }
  ```

## Rule Structure

### Supported Conditions
- `age > 30`
- `department = 'Sales'`
- `salary >= 50000`

### Supported Logical Operators
- `AND`, `OR`

### Example Rules
1. Simple:
   ```bash
   age > 30
   ```
2. Compound:
   ```bash
   (age > 30 AND department = 'Sales')
   ```

## Test Cases

### Example Test
```python
# Simple rule test case
rule_name = "age_rule"
rule_string = "age > 30"
test_data = {"age": 35}
# Expected output: True
```

## Error Handling

The application handles:
1. **Syntax errors** (e.g., malformed rules).
2. **Data validation errors** (e.g., missing fields).
3. **Database errors** (e.g., duplicate rule names).

## Troubleshooting

### Common Issues:
- **Incorrect rule syntax:** Check for unmatched parentheses or invalid operators.
- **Evaluation issues:** Ensure that the data being passed matches the rule format.
- **Server errors:** Verify that the `.env` file is correctly set up.

For further assistance, please refer to the documentation or create an issue in the repository.

