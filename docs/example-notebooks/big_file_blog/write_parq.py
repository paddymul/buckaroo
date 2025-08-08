import polars as pl
JULY_FILE = "~/NPPES_Data_Dissemination_July_2025/npidata_pfile_20050523-20250713.csv"
pl.read_csv(JULY_FILE).write_parquet("~/JULY_FULL2.parq")
