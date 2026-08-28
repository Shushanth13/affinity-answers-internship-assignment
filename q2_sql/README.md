# Q2 - Rfam Public MySQL Database

The SQL queries for this question are available in `queries.sql`.

## Database Connection

The queries can be executed using the public Rfam MySQL database.

```bash
mysql --user rfamro --host mysql-rfam-public.ebi.ac.uk --port 4497 --database Rfam
```

## Tables Used

The queries use the following tables:

- **taxonomy** – Contains species and taxonomy information.
- **rfamseq** – Stores sequence details, including sequence length.
- **family** – Contains Rfam family information.
- **full_region** – Links families with sequences.

## Query Summary

### (a) Count Acacia species

Counts the number of species that belong to the **Acacia** genus using the `taxonomy` table.

### (b) Wheat species with the longest sequence

Joins the `taxonomy` and `rfamseq` tables, filters wheat species (`Triticum`), and returns the species with the longest sequence.

### (c) Paginated family list

Joins the `family`, `full_region`, and `rfamseq` tables to find the maximum sequence length for each family. Only families with a maximum sequence length greater than **1,000,000** are included. The results are sorted in descending order and page 9 is returned using `LIMIT` and `OFFSET`.

## Note

I was not able to execute these queries from my current environment because the public Rfam database could not be reached. The queries were written based on the Rfam database documentation and schema. They should run on a normal system with access to the public database.