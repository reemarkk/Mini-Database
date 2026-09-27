from table import Table

def build_database():
    S = Table(
        ["S#", "Sname", "SCity", "Status"],
        primary_key="S#"
    )

    S.insert(["S1", "Smith", "London", 20])
    S.insert(["S2", "Jones", "Paris", 10])
    S.insert(["S3", "Brown", "London", 30])
    S.insert(["S4", "Clark", "Rome", 20])
    S.insert(["S5", "Adams", "Paris", 10])

    P = Table(
        ["P#", "PName", "Weight", "Color"],
        primary_key="P#"
    )

    P.insert(["P1", "Nut", 12, "Red"])
    P.insert(["P2", "Bolt", 17, "Green"])
    P.insert(["P3", "Screw", 17, "Blue"])
    P.insert(["P4", "Screw", 14, "Red"])
    P.insert(["P5", "Cam", 12, "Blue"])
    P.insert(["P6", "Cog", 19, "Red"])

    SP = Table(["S#", "P#", "Quantity"])

    SP.insert(["S1", "P1", 300])
    SP.insert(["S1", "P2", 200])
    SP.insert(["S1", "P3", 400])
    SP.insert(["S1", "P4", 200])
    SP.insert(["S1", "P5", 100])
    SP.insert(["S1", "P6", 100])

    SP.insert(["S2", "P1", 300])
    SP.insert(["S2", "P2", 400])

    SP.insert(["S3", "P2", 200])
    SP.insert(["S3", "P3", 200])

    SP.insert(["S4", "P4", 300])
    SP.insert(["S4", "P5", 400])

    SP.insert(["S5", "P1", 200])
    SP.insert(["S5", "P2", 100])
    SP.insert(["S5", "P5", 500])

    return S, P, SP


def main():

    S, P, SP = build_database()

    # -----------------------------------------------------------
    # PRINT DATABASE
    # -----------------------------------------------------------

    print("SUPPLIERS")
    S.print()

    print("\nPARTS")
    P.print()

    print("\nSUPPLIER-PART")
    SP.print()

    # -----------------------------------------------------------
    # 1. Suppliers who supply parts
    # -----------------------------------------------------------

    print("\n--- Suppliers who supply parts ---")

    result = S.join(SP)
    result = result.select(["Sname"])
    result = result.distinct()

    result.print()

    # -----------------------------------------------------------
    # 2. Suppliers who supply at least one red part
    # -----------------------------------------------------------

    print("\n--- Suppliers who supply at least one red part ---")

    result = SP.join(P)

    result = result.where(
        lambda row: row["Color"] == "Red"
    )

    result = S.join(result)

    result = result.select(["Sname"])
    result = result.distinct()

    result.print()

    # -----------------------------------------------------------
    # 3. Total quantity supplied for each part
    # -----------------------------------------------------------

    print("\n--- Total quantity supplied, per part ---")

    total_by_part = SP.group_by(
        ["P#"],
        {
            "total_quantity":
                lambda rows: sum(
                    row["Quantity"]
                    for row in rows
                )
        }
    )

    total_by_part = total_by_part.order_by(
        lambda row: row["P#"]
    )

    total_by_part.print()

    # -----------------------------------------------------------
    # 4. Parts not supplied by any Paris supplier
    # -----------------------------------------------------------

    print(
        "\n--- Parts not supplied by any Paris-based supplier ---"
    )

    paris_suppliers = S.where(
        lambda row: row["SCity"] == "Paris"
    )

    parts_from_paris = paris_suppliers.join(SP)

    parts_from_paris = parts_from_paris.select(["P#"])
    parts_from_paris = parts_from_paris.distinct()

    paris_part_ids = set(
        row["P#"]
        for row in parts_from_paris.rows
    )

    result = P.where(
        lambda row: row["P#"] not in paris_part_ids
    )

    result = result.select(["PName"])

    result.print()

    # -----------------------------------------------------------
    # 5. Suppliers who supply ALL parts
    # -----------------------------------------------------------

    print("\n--- Suppliers who supply ALL parts ---")

    all_part_ids = set(
        row["P#"]
        for row in P.rows
    )

    supplier_parts = SP.group_by(
        ["S#"],
        {
            "parts":
                lambda rows: set(
                    row["P#"]
                    for row in rows
                )
        }
    )

    suppliers_with_everything = supplier_parts.where(
        lambda row: row["parts"] == all_part_ids
    )

    result = S.join(
        suppliers_with_everything
    )

    result = result.select(["Sname"])

    result.print()

    # -----------------------------------------------------------
    # 6. LEFT JOIN
    # -----------------------------------------------------------

    print(
        "\n--- All suppliers with their supplied part count ---"
    )

    left = S.join(
        SP,
        left_join=True
    )

    counts = left.group_by(
        ["S#"],
        {
            "num_supplied":
                lambda rows: sum(
                    1
                    for row in rows
                    if row["P#"] is not None
                )
        }
    )

    counts = counts.order_by(
        lambda row: row["S#"]
    )

    counts.print()

    # -----------------------------------------------------------
    # 7. HAVING
    # Suppliers who supply more than 3 kinds of parts
    # -----------------------------------------------------------

    print(
        "\n--- Suppliers who supply more than 3 kinds of parts ---"
    )

    result = SP.group_by(
        ["S#"],
        {
            "num_kinds": lambda rows: len(rows)
        },
        having=lambda row: row["num_kinds"] > 3
    )

    result = S.join(result)

    result = result.select(
        ["Sname", "num_kinds"]
    )

    result.print()

    # -----------------------------------------------------------
    # 8. PRIMARY KEY
    # -----------------------------------------------------------

    print("\n--- PRIMARY KEY check ---")

    try:
        S.insert(
            ["S1", "Someone", "Yerevan", 15]
        )

    except ValueError as e:
        print (e)


if __name__ == "__main__":
    main()