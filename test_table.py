"""
Խնդիր 10. Unit test-եր Table դասի համար։
Գործարկել՝  python3 -m unittest test_table.py -v
"""
import unittest
from table import Table


def make_users():
    users = Table(["user_id", "name", "num_friends"], primary_key="user_id")
    users.insert([0, "Hero", 0])
    users.insert([1, "Dunn", 2])
    users.insert([2, "Sue", 3])
    return users


class TestBasics(unittest.TestCase):
    def test_insert_and_rows(self):
        users = make_users()
        self.assertEqual(len(users.rows), 3)
        self.assertEqual(users.rows[0], {"user_id": 0, "name": "Hero", "num_friends": 0})

    def test_insert_wrong_length_raises(self):
        users = make_users()
        with self.assertRaises(ValueError):
            users.insert([9, "TooFew"])

    def test_primary_key_violation(self):
        users = make_users()
        with self.assertRaises(ValueError):
            users.insert([0, "Duplicate", 5])

    def test_where(self):
        users = make_users()
        result = users.where(lambda row: row["num_friends"] >= 2)
        self.assertEqual(len(result.rows), 2)

    def test_select(self):
        users = make_users()
        result = users.select(["name"])
        self.assertEqual(result.columns, ["name"])
        self.assertEqual(result.rows[0], {"name": "Hero"})

    def test_update(self):
        users = make_users()
        users.update({"num_friends": 10}, lambda row: row["user_id"] == 0)
        self.assertEqual(users.rows[0]["num_friends"], 10)

    def test_delete(self):
        users = make_users()
        users.delete(lambda row: row["user_id"] == 1)
        self.assertEqual(len(users.rows), 2)
        ids = [row["user_id"] for row in users.rows]
        self.assertNotIn(1, ids)

    def test_order_by_single_column(self):
        users = make_users()
        result = users.order_by("num_friends")
        friends = [row["num_friends"] for row in result.rows]
        self.assertEqual(friends, [0, 2, 3])

    def test_order_by_desc(self):
        users = make_users()
        result = users.order_by("num_friends", desc=True)
        friends = [row["num_friends"] for row in result.rows]
        self.assertEqual(friends, [3, 2, 0])

    def test_order_by_multiple_columns(self):
        t = Table(["a", "b"])
        t.insert([1, "z"]); t.insert([1, "a"]); t.insert([0, "x"])
        result = t.order_by(["a", "b"])
        self.assertEqual([(r["a"], r["b"]) for r in result.rows], [(0, "x"), (1, "a"), (1, "z")])

    def test_distinct(self):
        t = Table(["x"])
        t.insert([1]); t.insert([1]); t.insert([2])
        result = t.distinct()
        self.assertEqual(len(result.rows), 2)


class TestGroupBy(unittest.TestCase):
    def test_group_by_single_aggregate(self):
        users = make_users()
        result = users.group_by("num_friends", {"count": len})
        counts = {row["num_friends"]: row["count"] for row in result.rows}
        self.assertEqual(counts, {0: 1, 2: 1, 3: 1})

    def test_group_by_multiple_aggregates(self):
        t = Table(["group", "value"])
        for g, v in [("a", 1), ("a", 3), ("b", 5)]:
            t.insert([g, v])
        result = t.group_by(
            "group",
            {"total": lambda rows: sum(r["value"] for r in rows), "count": len},
        )
        by_group = {row["group"]: row for row in result.rows}
        self.assertEqual(by_group["a"]["total"], 4)
        self.assertEqual(by_group["a"]["count"], 2)
        self.assertEqual(by_group["b"]["total"], 5)

    def test_having(self):
        t = Table(["group", "value"])
        for g, v in [("a", 1), ("a", 3), ("b", 5)]:
            t.insert([g, v])
        result = t.group_by("group", {"count": len}, having=lambda row: row["count"] > 1)
        groups = [row["group"] for row in result.rows]
        self.assertEqual(groups, ["a"])


class TestJoin(unittest.TestCase):
    def setUp(self):
        self.users = Table(["user_id", "name"], primary_key="user_id")
        self.users.insert([0, "Hero"])
        self.users.insert([1, "Dunn"])

        self.interests = Table(["user_id", "interest"])
        self.interests.insert([0, "SQL"])
        self.interests.insert([0, "Python"])

    def test_inner_join_no_duplicate_columns(self):
        result = self.users.join(self.interests, "user_id", "user_id")
        self.assertEqual(result.columns.count("user_id"), 1)
        self.assertEqual(len(result.rows), 2)

    def test_inner_join_drops_unmatched(self):
        result = self.users.join(self.interests, "user_id", "user_id")
        names = set(row["name"] for row in result.rows)
        self.assertEqual(names, {"Hero"})  # Dunn-ը հետաքրքրություն չունի

    def test_left_join_keeps_unmatched(self):
        result = self.users.join(self.interests, "user_id", "user_id", left_join=True)
        dunn_rows = [row for row in result.rows if row["name"] == "Dunn"]
        self.assertEqual(len(dunn_rows), 1)
        self.assertIsNone(dunn_rows[0]["interest"])


class TestIndex(unittest.TestCase):
    def test_find_uses_index_and_matches_scan(self):
        t = Table(["k", "v"])
        t.insert(["a", 1]); t.insert(["b", 2]); t.insert(["a", 3])
        t.create_index("k")
        result = t.find("k", "a")
        self.assertEqual(sorted(row["v"] for row in result.rows), [1, 3])

    def test_index_updated_after_insert(self):
        t = Table(["k", "v"])
        t.create_index("k")
        t.insert(["a", 1])
        self.assertEqual(len(t.find("k", "a").rows), 1)


if __name__ == "__main__":
    unittest.main()
