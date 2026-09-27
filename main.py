from table import Table


def build_database():
    S = Table(["S#", "Sname", "SCity", "Status"], primary_key="S#")
    S.insert(["S1", "Smith", "London", 20])
    S.insert(["S2", "Jones", "Paris", 10])
    S.insert(["S3", "Brown", "London", 30])
    S.insert(["S4", "Clark", "Rome", 20])
    S.insert(["S5", "Adams", "Paris", 10])

    P = Table(["P#", "PName", "Weight", "Color"], primary_key="P#")
    P.insert(["P1", "Nut", 12, "Red"])
    P.insert(["P2", "Bolt", 17, "Green"])
    P.insert(["P3", "Screw", 17, "Blue"])
    P.insert(["P4", "Screw", 14, "Red"])
    P.insert(["P5", "Cam", 12, "Blue"])
    P.insert(["P6", "Cog", 19, "Red"])

    SP = Table(["S#", "P#", "Quantity"])
    SP.insert(["S1", "P1", 300]); SP.insert(["S1", "P2", 200])
    SP.insert(["S1", "P3", 400]); SP.insert(["S1", "P4", 200])
    SP.insert(["S1", "P5", 100]); SP.insert(["S1", "P6", 100])
    SP.insert(["S2", "P1", 300]); SP.insert(["S2", "P2", 400])
    SP.insert(["S3", "P2", 200]); SP.insert(["S3", "P3", 200])
    SP.insert(["S4", "P4", 300]); SP.insert(["S4", "P5", 400])
    SP.insert(["S5", "P1", 200]); SP.insert(["S5", "P2", 100]); SP.insert(["S5", "P5", 500])

    # Խնդիր 8. ինդեքսներ՝ join-երն արագացնելու համար
    SP.create_index("S#")
    SP.create_index("P#")

    return S, P, SP


def main():
    S, P, SP = build_database()

    print("SUPPLIERS"); S.print()
    print("\nPARTS"); P.print()
    print("\nSUPPLIER-PART"); SP.print()

    # -----------------------------------------------------------
    print("\n--- Suppliers who supply parts (այժմ եզակի, distinct()-ով) ---")
    result = S.join(SP, "S#", "S#").select(["Sname"]).distinct()
    result.print()

    # -----------------------------------------------------------
    print("\n--- Suppliers who supply at least one red part ---")
    result = SP.join(P, "P#", "P#")
    result = result.where(lambda row: row["Color"] == "Red")
    result = S.join(result, "S#", "S#")
    result = result.select(["Sname"]).distinct()
    result.print()

    # -----------------------------------------------------------
    # Խնդիր 9ա. Ընդհանուր մատակարարված քանակը ամեն դետալի համար
    # SELECT P#, SUM(Quantity) FROM SP GROUP BY P#
    # -----------------------------------------------------------
    print("\n--- Total quantity supplied, per part ---")
    total_by_part = SP.group_by(
        "P#",
        {"total_quantity": lambda rows: sum(r["Quantity"] for r in rows)},
    ).order_by("P#")
    total_by_part.print()

    # -----------------------------------------------------------
    # Խնդիր 9բ. Դետալներ, որոնք ոչ մի Փարիզի մատակարար չի մատակարարում
    # -----------------------------------------------------------
    print("\n--- Parts not supplied by any Paris-based supplier ---")
    paris_suppliers = S.where(lambda row: row["SCity"] == "Paris")
    parts_from_paris = paris_suppliers.join(SP, "S#", "S#").select(["P#"]).distinct()
    paris_part_ids = set(row["P#"] for row in parts_from_paris.rows)

    result = P.where(lambda row: row["P#"] not in paris_part_ids).select(["PName"])
    result.print()

    # -----------------------------------------------------------
    # Խնդիր 9գ. Մատակարարներ, ովքեր մատակարարում են ԲՈԼՈՐ դետալները
    # (classic relational division)
    # -----------------------------------------------------------
    print("\n--- Suppliers who supply ALL parts ---")
    all_part_ids = set(row["P#"] for row in P.rows)

    supplier_parts = SP.group_by(
        "S#",
        {"parts": lambda rows: set(r["P#"] for r in rows)},
    )
    suppliers_with_everything = supplier_parts.where(
        lambda row: row["parts"] == all_part_ids
    )
    result = S.join(suppliers_with_everything, "S#", "S#").select(["Sname"])
    result.print()

    # -----------------------------------------------------------
    # Խնդիր 5. LEFT JOIN. ցույց տալ բոլոր մատակարարներին, նույնիսկ
    # նրանց, ովքեր ոչինչ չեն մատակարարել
    # -----------------------------------------------------------
    print("\n--- All suppliers with their supplied part count (LEFT JOIN) ---")
    left = S.join(SP, "S#", "S#", left_join=True)
    counts = left.group_by(
        "S#",
        {"num_supplied": lambda rows: sum(1 for r in rows if r["P#"] is not None)},
    ).order_by("S#")
    counts.print()

    # -----------------------------------------------------------
    # Խնդիր 4. HAVING. մատակարարներ, ովքեր մատակարարում են 3-ից ավելի տեսակի դետալ
    # -----------------------------------------------------------
    print("\n--- Suppliers who supply more than 3 kinds of parts (HAVING) ---")
    result = SP.group_by(
        "S#",
        {"num_kinds": len},
        having=lambda row: row["num_kinds"] > 3,
    )
    result = S.join(result, "S#", "S#").select(["Sname", "num_kinds"])
    result.print()

    # -----------------------------------------------------------
    # Խնդիր 7. PRIMARY KEY-ի ստուգում
    # -----------------------------------------------------------
    print("\n--- PRIMARY KEY ստուգում ---")
    try:
        S.insert(["S1", "Someone", "Yerevan", 15])
    except ValueError as e:
        print("Սպասված սխալ.", e)

    # -----------------------------------------------------------
    # Խնդիր 8. find() ինդեքսի միջոցով
    # -----------------------------------------------------------
    print("\n--- find() օգտագործմամբ (ինդեքսի միջոցով) ---")
    SP.find("S#", "S1").print()


if __name__ == "__main__":
    main()
