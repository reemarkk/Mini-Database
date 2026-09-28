# Mini In-Memory Database (SQL in Python)

A small, educational relational "database" written in pure Python. It shows how the core SQL operations (`CREATE TABLE`, `INSERT`, `SELECT`, `WHERE`, `UPDATE`, `DELETE`, `ORDER BY`, `GROUP BY ... HAVING`, `JOIN`, `DISTINCT`, `PRIMARY KEY`) can be built from a few simple Python functions.

The project is inspired by the *NotQuiteABase* idea from Chapter 23 ("Databases and SQL") of *Data Science from Scratch* by Joel Grus. The code here is an independent implementation, written in Python 3 and extended with extra features.

To demonstrate it, `main.py` runs eight queries against the classic **Suppliers – Parts – Supplier-Part (S / P / SP)** example database.

---

## Table of contents

- [Features](#features)
- [Project structure](#project-structure)
- [Requirements and how to run](#requirements-and-how-to-run)
- [How it works](#how-it-works)
- [The example database](#the-example-database)
- [API reference](#api-reference)
- [The demo queries](#the-demo-queries)
- [Design notes and limitations](#design-notes-and-limitations)

---

## Features

| SQL feature | Python method |
|---|---|
| `CREATE TABLE ... PRIMARY KEY` | `Table(columns, primary_key=None)` |
| `INSERT INTO` | `insert(row_values)` |
| `SELECT col1, col2` (and computed columns) | `select(keep_columns, additional_columns)` |
| `WHERE` | `where(predicate)` |
| `UPDATE ... SET ... WHERE` | `update(updates, predicate)` |
| `DELETE FROM ... WHERE` | `delete(predicate)` |
| `ORDER BY [DESC]` | `order_by(key_function, reverse=False)` |
| `GROUP BY ... HAVING` | `group_by(group_columns, aggregates, having=None)` |
| `INNER JOIN` / `LEFT JOIN` | `join(other_table, left_join=False)` |
| `SELECT DISTINCT` | `distinct()` |
| Pretty-print a table | `print()` |

Every query method returns a **new** `Table`, so calls can be chained:

```python
S.join(SP).select(["Sname"]).distinct()
```

---

## Project structure

```
.
├── table.py    # the Table class (the "database engine")
├── main.py     # builds the S / P / SP database and runs 8 example queries
└── README.md
```

---

## Requirements and how to run

- Python 3.6 or newer (uses f-strings). No third-party packages.

```bash
python3 main.py
```

---

## How it works

A `Table` is created just by naming its columns:

```python
S = Table(["S#", "Sname", "SCity", "Status"], primary_key="S#")
```

`insert()` takes a list of values in the same order as the columns and stores each row as a **dictionary** (column name to value):

```python
S.insert(["S1", "Smith", "London", 20])
# stored as: {"S#": "S1", "Sname": "Smith", "SCity": "London", "Status": 20}
```

That is done by one line inside `insert()`:

```python
row = dict(zip(self.columns, row_values))
```

Storing rows as dictionaries wastes memory, because every row repeats the column names, and a real database would never do this. It is used here on purpose: it lets every method refer to a value by name (`row["SCity"]`) instead of by position (`row[2]`), which keeps the code short and easy to read.

Conditions and calculations are passed in as ordinary Python functions:

```python
S.where(lambda row: row["SCity"] == "Paris")
```

---

## The example database

**S (Suppliers)** – primary key `S#`

| S# | Sname | SCity | Status |
|----|-------|--------|--------|
| S1 | Smith | London | 20 |
| S2 | Jones | Paris  | 10 |
| S3 | Brown | London | 30 |
| S4 | Clark | Rome   | 20 |
| S5 | Adams | Paris  | 10 |

`Status` is simply a numeric rating attribute of a supplier (a higher value is typically read as a more highly rated supplier). It exists to give the queries an extra numeric column to work with.

**P (Parts)** – primary key `P#`

| P# | PName | Weight | Color |
|----|-------|--------|-------|
| P1 | Nut   | 12 | Red   |
| P2 | Bolt  | 17 | Green |
| P3 | Screw | 17 | Blue  |
| P4 | Screw | 14 | Red   |
| P5 | Cam   | 12 | Blue  |
| P6 | Cog   | 19 | Red   |

**SP (Supplier–Part)** – which supplier supplies which part, and how many (15 rows). Its columns are `S#`, `P#`, `Quantity`.

---

## API reference

### `Table(columns, primary_key=None)`
Creates an empty table. `columns` is a list of column names. If `primary_key` is given, `insert()` rejects duplicate values in that column.

### `insert(row_values)`
Adds one row. Raises `TypeError` if the number of values does not match the number of columns, and `ValueError` if the primary key already exists.

### `select(keep_columns=None, additional_columns=None)`
Returns a new table with only `keep_columns` (all columns if `None`). `additional_columns` is a dict `{new_column_name: function(row)}` for computed columns.

```python
S.select(["Sname"], {"name_length": lambda row: len(row["Sname"])})
```

### `where(predicate)`
Returns a new table with only the rows for which `predicate(row)` is true.

### `update(updates, predicate)`
For every row matching `predicate`, sets the columns in the `updates` dict to the new values. Modifies the table in place.

```python
S.update({"Status": 25}, lambda row: row["S#"] == "S1")
```

### `delete(predicate=lambda row: True)`
Removes the rows matching `predicate`. With no argument, removes **all** rows. Modifies the table in place.

### `order_by(key_function, reverse=False)`
Returns a sorted copy. `key_function` works like the `key` argument of Python's `sorted()`.

### `group_by(group_columns, aggregates, having=None)`
Groups rows by the values of `group_columns`.

- `aggregates` is a dict `{result_column: function(rows)}`; each function receives the list of rows in one group and returns a value (a number, a set, anything).
- `having` is an optional function that receives a dict of the **already computed aggregate values** for a group and decides whether to keep it, for example `lambda row: row["num_kinds"] > 3`.

### `join(other_table, left_join=False)`
Joins two tables on **all columns with the same name** (found automatically). With `left_join=True`, rows of the left table with no match are kept, and the right-hand columns are filled with `None` (SQL's `NULL`). Raises `ValueError` if the tables have no common column.

### `distinct()`
Returns a new table with duplicate rows removed (first occurrence kept).

### `print()`
Prints the table as aligned text with a header line.

---

## The demo queries

Example: Which suppliers supply at least one red part?

```sql
SELECT DISTINCT Sname
FROM S JOIN SP ON S."S#" = SP."S#"
       JOIN P  ON SP."P#" = P."P#"
WHERE Color = 'Red';
```

```python
result = SP.join(P)
result = result.where(lambda row: row["Color"] == "Red")
result = S.join(result)
result = result.select(["Sname"]).distinct()
```

Note that in SQL the database decides the order of the operations; here you choose it yourself (join, filter, then join again), which is the idea behind query optimization.

## Design notes and limitations

- **Rows are dicts.** Chosen for readability, not efficiency (see [How it works](#how-it-works)).
- **No types.** Columns have names only; any value can go in any column.
- **`join` is a nested loop.** Every left row is compared with every right row, which is simple but slow on large tables. There are no indexes.
- **`join` uses common column names.** Tables must share a column name to be joined. If they share more than one, all of them must match. Columns that have the same name in both tables appear only once in the result.
- **Primary key check is O(n).** Each `insert()` scans the existing rows. A real database uses an index.
- **`PRIMARY KEY` covers a single column** and is only checked on `insert()`, not on `update()`.
- **`group_by` groups by exact value** and supports one `having` function that sees the aggregate values, not the raw rows.
- **In-memory only.** Nothing is saved to disk.
- **Not thread-safe** and not meant for production use.

---
