-- Connect: mysql --user rfamro --host mysql-rfam-public.ebi.ac.uk --port 4497 --database Rfam

-- (a) How many types of Acacia plants in taxonomy table
SELECT COUNT(DISTINCT species) AS acacia_species_count
FROM taxonomy
WHERE tax_string LIKE '%;Acacia;%';

SELECT DISTINCT species
FROM taxonomy
WHERE tax_string LIKE '%;Acacia;%'
ORDER BY species;

-- (b) Wheat with longest DNA sequence
SELECT tx.species, rs.rfamseq_acc, rs.length
FROM rfamseq rs
JOIN taxonomy tx ON rs.ncbi_id = tx.ncbi_id
WHERE tx.tax_string LIKE '%;Triticum;%'
ORDER BY rs.length DESC
LIMIT 1;

SELECT tx.species, MAX(rs.length) AS max_length
FROM rfamseq rs
JOIN taxonomy tx ON rs.ncbi_id = tx.ncbi_id
WHERE tx.tax_string LIKE '%;Triticum;%'
GROUP BY tx.species
ORDER BY max_length DESC
LIMIT 1;

-- (c) Paginated family list, families with max DNA length > 1,000,000, page 9 (15/page)
SELECT
    f.rfam_acc,
    f.rfam_id AS family_name,
    MAX(rs.length) AS max_dna_length
FROM family f
JOIN full_region fr ON fr.rfam_acc = f.rfam_acc
JOIN rfamseq rs ON rs.rfamseq_acc = fr.rfamseq_acc
GROUP BY f.rfam_acc, f.rfam_id
HAVING MAX(rs.length) > 1000000
ORDER BY max_dna_length DESC
LIMIT 15 OFFSET 120;