import polars as pl
import time
def to_parquet(orig_csv_fname, output_parquet_fname):
    pl.scan_csv(orig_csv_fname).sink_parquet(output_parquet_fname)

#df = pl.read_parquet("~/JULY_FULL_enum.parq")

to_parquet("~/NPPES_Data_Dissemination_July_2025/npidata_pfile_20050523-20250713.csv", "~/JULY_FULL2.parq")
time.sleep(30)

'''
#contents of write_parq.py
import polars as pl
JULY_FILE = "~/NPPES_Data_Dissemination_July_2025/npidata_pfile_20050523-20250713.csv"
pl.read_csv(JULY_FILE).write_parquet("~/JULY_FULL2.parq")


'''
