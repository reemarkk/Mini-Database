from collections import defaultdict


class Table:
    def __init__(self, columns, primary_key=None):
        self.columns = columns
        self.rows = []
        self.primary_key = primary_key

    def __repr__(self):
        result = [str(self.columns)]

        for row in self.rows:
            result.append(str(row))

        return "\n".join(result)

    def insert(self, row_values):
        if len(row_values) != len(self.columns):
            raise TypeError("Սխալ քանակությամբ արժեքներ")

        row = dict(zip(self.columns, row_values))

        # PRIMARY KEY check
        if self.primary_key is not None:
            key = row[self.primary_key]

            for existing_row in self.rows:
                if existing_row[self.primary_key] == key:
                    raise ValueError(
                        f"Duplicate primary key: {key}"
                    )

        self.rows.append(row)

    def select(self, keep_columns=None, additional_columns=None):
        if keep_columns is None:
            keep_columns = self.columns

        if additional_columns is None:
            additional_columns = {}

        result = Table(
            keep_columns + list(additional_columns.keys())
        )

        for row in self.rows:
            new_row = [
                row[column]
                for column in keep_columns
            ]

            for calculation in additional_columns.values():
                new_row.append(calculation(row))

            result.insert(new_row)

        return result

    def where(self, predicate):
        result = Table(self.columns)

        result.rows = [
            row
            for row in self.rows
            if predicate(row)
        ]

        return result

    def limit(self, n):
        result = Table(self.columns)
        result.rows = self.rows[:n]
        return result

    def update(self, updates, predicate):
        for row in self.rows:
            if predicate(row):
                for column, value in updates.items():
                    row[column] = value

    def delete(self, predicate=lambda row: True):
        self.rows = [
            row
            for row in self.rows
            if not predicate(row)
        ]

    def order_by(self, key_function, reverse=False):
        result = self.select()

        result.rows.sort(
            key=key_function,
            reverse=reverse
        )

        return result

    def group_by(self, group_columns, aggregates, having=None):
        groups = defaultdict(list)

        # Ստեղծում ենք խմբերը
        for row in self.rows:
            key = tuple(
                row[column]
                for column in group_columns
            )

            groups[key].append(row)

        result = Table(
            group_columns + list(aggregates.keys())
        )

        # Հաշվում ենք aggregate-ները
        for key, rows in groups.items():

            aggregate_values = {}

            for name, function in aggregates.items():
                aggregate_values[name] = function(rows)

            # HAVING
            if having is not None:
                if not having(aggregate_values):
                    continue

            new_row = list(key)

            for name in aggregates:
                new_row.append(
                    aggregate_values[name]
                )

            result.insert(new_row)

        return result

    def join(self, other_table, left_join=False):

        common_columns = [
            column
            for column in self.columns
            if column in other_table.columns
        ]

        if not common_columns:
            raise ValueError(
                "JOIN-ի համար ընդհանուր սյունակ չկա"
            )

        other_columns = [
            column
            for column in other_table.columns
            if column not in common_columns
        ]

        result = Table(
            self.columns + other_columns
        )

        for left_row in self.rows:

            matches = []

            for right_row in other_table.rows:

                if all(
                    left_row[column] == right_row[column]
                    for column in common_columns
                ):
                    matches.append(right_row)

            # INNER JOIN
            for right_row in matches:

                new_row = [
                    left_row[column]
                    for column in self.columns
                ]

                new_row += [
                    right_row[column]
                    for column in other_columns
                ]

                result.insert(new_row)

            # LEFT JOIN
            if left_join and not matches:
 
              new_row = [
                    left_row[column]
                    for column in self.columns
                ]

                new_row += [
                    None
                    for column in other_columns
                ]

                result.insert(new_row)

        return result

    def distinct(self):
        result = Table(self.columns)
        seen = set()

        for row in self.rows:
            values = tuple(
                row[column]
                for column in self.columns
            )

            if values not in seen:
                seen.add(values)
                result.rows.append(row)

        return result

    def print(self):
        print(" | ".join(self.columns))
        print("-" * (len(self.columns) * 12))

        for row in self.rows:
            values = []

            for column in self.columns:
                values.append(str(row[column]))

            print(" | ".join(values))