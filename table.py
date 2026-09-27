"""
Table դասը՝ ընդլայնված տարբերակ։

Ավելացված է նախորդ տարբերակի նկատմամբ.
  1) join()-ը այլևս չի կրկնում ընդհանուր անուն ունեցող սյունակները
  2) group_by()-ը թույլ է տալիս մի քանի ագրեգացիա միանգամից + HAVING
  3) join()-ը ունի left_join= տարբերակ
  4) order_by()-ը թույլ է տալիս մի քանի սյունակ
  5) primary_key= պարամետր՝ եզակիությունը ապահովելու համար
  6) create_index() / find()՝ արագ որոնման համար
"""


class Table:
    # CREATE TABLE table (columns...) [PRIMARY KEY (primary_key)]
    def __init__(self, columns, primary_key=None):
        self.columns = columns
        self.rows = []
        self.primary_key = primary_key
        self.indexes = {}  # {column_name: {value: [rows]}}

    # ---------------------------------------------------------------
    # INSERT INTO table VALUES (...)
    # ---------------------------------------------------------------
    def insert(self, values):
        if len(values) != len(self.columns):
            raise ValueError(
                "սպասվում էր {} արժեք, ստացվեց {}".format(len(self.columns), len(values))
            )

        row = {}
        for i in range(len(self.columns)):
            column_name = self.columns[i]
            row[column_name] = values[i]

        # Խնդիր 7. PRIMARY KEY-ի եզակիության ստուգում
        if self.primary_key is not None:
            key_value = row[self.primary_key]
            if self._rows_matching(self.primary_key, key_value):
                raise ValueError(
                    "կրկնվող {}={} արժեք (PRIMARY KEY խախտում)".format(
                        self.primary_key, key_value
                    )
                )

        self.rows.append(row)

        # եթե այս սյունակի համար ինդեքս կա, թարմացնում ենք այն նոր տողով
        for column_name, index in self.indexes.items():
            index.setdefault(row[column_name], []).append(row)

    # ---------------------------------------------------------------
    # SELECT * FROM table WHERE condition
    # ---------------------------------------------------------------
    def where(self, condition):
        result = Table(self.columns)
        for row in self.rows:
            if condition(row):
                result.rows.append(row)
        return result

    # ---------------------------------------------------------------
    # SELECT col1, col2 FROM table
    # ---------------------------------------------------------------
    def select(self, columns_name):
        result = Table(columns_name)
        for row in self.rows:
            new_row = {}
            for col in columns_name:
                new_row[col] = row[col]
            result.rows.append(new_row)
        return result

    # ---------------------------------------------------------------
    # UPDATE table SET ... WHERE ...
    # ---------------------------------------------------------------
    def update(self, values, condition):
        for row in self.rows:
            if condition(row):
                for column_name in values:
                    row[column_name] = values[column_name]

        # ինդեքսները այլևս վստահելի չեն. պարզության համար՝ մաքրում ենք
        self.indexes = {}

    # ---------------------------------------------------------------
    # DELETE FROM table WHERE ...
    # ---------------------------------------------------------------
    def delete(self, condition):
        new_rows = []
        for row in self.rows:
            if not condition(row):
                new_rows.append(row)
        self.rows = new_rows
        self.indexes = {}

    # ---------------------------------------------------------------
    # Խնդիր 6. ORDER BY col1, col2, ... [DESC]
    # ---------------------------------------------------------------
    def order_by(self, columns, desc=False):
        if isinstance(columns, str):
            columns = [columns]

        result = Table(self.columns)
        result.rows = sorted(
            self.rows,
            key=lambda row: tuple(row[c] for c in columns),
            reverse=desc,
        )
        return result

    # ---------------------------------------------------------------
    # Խնդիր 3 և 4. GROUP BY col AS {name: aggregate_function, ...} [HAVING]
    # ---------------------------------------------------------------
    def group_by(self, group_column, aggregates, having=None):
        groups = {}
        for row in self.rows:
            key = row[group_column]
            groups.setdefault(key, []).append(row)

        result_columns = [group_column] + list(aggregates.keys())
        result = Table(result_columns)

        for key, rows_in_group in groups.items():
            new_row = {group_column: key}
            for aggregate_name, aggregate_function in aggregates.items():
                new_row[aggregate_name] = aggregate_function(rows_in_group)

            # HAVING-ը ստուգում է արդեն ագրեգացված տողը, ոչ թե հում տողերը
            if having is None or having(new_row):
                result.rows.append(new_row)

        return result

    # ---------------------------------------------------------------
    # Խնդիր 1 և 5. JOIN [LEFT] ON self_column = other_column
    # ---------------------------------------------------------------
    def join(self, other_table, self_column, other_column, left_join=False):
        # չենք կրկնում այն սյունակները, որոնք արդեն կան self-ում
        extra_columns = [c for c in other_table.columns if c not in self.columns]
        columns = self.columns + extra_columns
        result = Table(columns)

        for row1 in self.rows:
            key = row1[self_column]
            matches = other_table._rows_matching(other_column, key)

            if matches:
                for row2 in matches:
                    new_row = dict(row1)
                    for column in extra_columns:
                        new_row[column] = row2[column]
                    result.rows.append(new_row)
            elif left_join:
                new_row = dict(row1)
                for column in extra_columns:
                    new_row[column] = None
                result.rows.append(new_row)

        return result

    # ---------------------------------------------------------------
    # Խնդիր 8. Ինդեքսավորում՝ արագ որոնման համար
    # ---------------------------------------------------------------
    def create_index(self, column_name):
        index = {}
        for row in self.rows:
            index.setdefault(row[column_name], []).append(row)
        self.indexes[column_name] = index

    def find(self, column_name, value):
        """SELECT * FROM table WHERE column_name = value, ինդեքսի միջոցով"""
        result = Table(self.columns)
        result.rows = list(self._rows_matching(column_name, value))
        return result

    def _rows_matching(self, column_name, value):
        if column_name in self.indexes:
            return self.indexes[column_name].get(value, [])
        return [row for row in self.rows if row[column_name] == value]

    # ---------------------------------------------------------------
    def print(self):
        print(" | ".join(self.columns))
        print("-" * (len(self.columns) * 12))
        for row in self.rows:
            values = [str(row[column]) for column in self.columns]
            print(" | ".join(values))

    def distinct(self):
        result = Table(self.columns)
        seen = set()
        for row in self.rows:
            values = tuple(row[column] for column in self.columns)
            if values not in seen:
                seen.add(values)
                result.rows.append(row)
        return result
