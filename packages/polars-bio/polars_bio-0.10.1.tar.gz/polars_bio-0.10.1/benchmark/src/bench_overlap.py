import itertools
import json
import os
import timeit

import bioframe as bf
import numpy as np
import pandas as pd
import pybedtools
import pyranges as pr
import pyranges1 as pr1
from genomicranges import GenomicRanges
from pygenomics.interval import GenomicBase
from rich import print
from rich.box import MARKDOWN
from rich.table import Table

import polars_bio as pb

BENCH_DATA_ROOT = os.getenv("BENCH_DATA_ROOT")

if BENCH_DATA_ROOT is None:
    raise ValueError("BENCH_DATA_ROOT is not set")


pb.ctx.set_option("datafusion.optimizer.repartition_joins", "false")

columns = ("contig", "pos_start", "pos_end")


num_repeats = 3
num_executions = 3


test_cases = [
    {
        "df_path_1": f"{BENCH_DATA_ROOT}/fBrain-DS14718/*.parquet",
        "df_path_2": f"{BENCH_DATA_ROOT}/exons/*.parquet",
        "name": "1-2",
    },
    {
        "df_path_1": f"{BENCH_DATA_ROOT}/exons/*.parquet",
        "df_path_2": f"{BENCH_DATA_ROOT}/ex-anno/*.parquet",
        "name": "2-7",
    },
    {
        "df_path_1": f"{BENCH_DATA_ROOT}/fBrain-DS14718/*.parquet",
        "df_path_2": f"{BENCH_DATA_ROOT}/chainRn4/*.parquet",
        "name": "1-0",
    },
    {
        "df_path_1": f"{BENCH_DATA_ROOT}/ex-anno/*.parquet",
        "df_path_2": f"{BENCH_DATA_ROOT}/chainRn4/*.parquet",
        "name": "7-0",
    },
    {
        "df_path_1": f"{BENCH_DATA_ROOT}/ex-anno/*.parquet",
        "df_path_2": f"{BENCH_DATA_ROOT}/chainOrnAna1/*.parquet",
        "name": "7-3",
    },
    {
        "df_path_1": f"{BENCH_DATA_ROOT}/chainRn4/*.parquet",
        "df_path_2": f"{BENCH_DATA_ROOT}/ex-rna/*.parquet",
        "name": "0-8",
    },
    {
        "df_path_1": f"{BENCH_DATA_ROOT}/chainVicPac2/*.parquet",
        "df_path_2": f"{BENCH_DATA_ROOT}/ex-rna/*.parquet",
        "name": "4-8",
    },
    {
        "df_path_1": f"{BENCH_DATA_ROOT}/ex-anno/*.parquet",
        "df_path_2": f"{BENCH_DATA_ROOT}/ex-rna/*.parquet",
        "name": "7-8",
    },
    {
        "df_path_1": f"{BENCH_DATA_ROOT}/chainOrnAna1/*.parquet",
        "df_path_2": f"{BENCH_DATA_ROOT}/chainRn4/*.parquet",
        "name": "3-0",
    },
    {
        "df_path_1": f"{BENCH_DATA_ROOT}/chainRn4/*.parquet",
        "df_path_2": f"{BENCH_DATA_ROOT}/chainVicPac2/*.parquet",
        "name": "0-4",
    },
    {
        "df_path_1": f"{BENCH_DATA_ROOT}/chainRn4/*.parquet",
        "df_path_2": f"{BENCH_DATA_ROOT}/chainXenTro3Link/*.parquet",
        "name": "0-5",
    },
]


# pyranges0
def df2pr0(df):
    return pr.PyRanges(
        chromosomes=df.contig,
        starts=df.pos_start,
        ends=df.pos_end,
    )


### pyranges1
def df2pr1(df):
    return pr1.PyRanges(
        {
            "Chromosome": df.contig,
            "Start": df.pos_start,
            "End": df.pos_end,
        }
    )


def bioframe(df_1, df_2):
    len(bf.overlap(df_1, df_2, cols1=columns, cols2=columns, how="inner"))


def polars_bio(df_path_1, df_path_2):
    pb.overlap(df_path_1, df_path_2, col1=columns, col2=columns).collect().count()


def pyranges0(df_1_pr0, df_2_pr0):
    len(df_1_pr0.join(df_2_pr0))


def pyranges1(df_1_pr1, df_2_pr1):
    len(df_1_pr1.join_ranges(df_2_pr1))


def pybedtools0(df_1_bed, df_2_bed):
    len(df_1_bed.intersect(df_2_bed, wa=True, wb=True))


def pygenomics(df_1_pg, df_2_array):
    len(
        list(
            itertools.chain.from_iterable(
                [df_1_pg.find_all((r[0], r[1], r[2])) for r in df_2_array]
            )
        )
    )


def genomicranges(df_1, df_2):
    len(df_1.find_overlaps(df_2, ignore_strand=True, query_type="any"))


functions = [
    bioframe,
    polars_bio,
    pyranges0,
    pyranges1,
    pybedtools0,
    pygenomics,
    genomicranges,
]


# mkdir
# mkdir results directory if it does not exist

os.makedirs("results", exist_ok=True)

for t in test_cases:
    results = []
    df_1 = pd.read_parquet(t["df_path_1"].replace("*.parquet", ""), engine="pyarrow")
    df_2 = pd.read_parquet(t["df_path_2"].replace("*.parquet", ""), engine="pyarrow")
    df_1_pr0 = df2pr0(df_1)
    df_2_pr0 = df2pr0(df_2)
    df_1_pr1 = df2pr1(df_1)
    df_2_pr1 = df2pr1(df_2)
    df_0_bed = pybedtools.BedTool.from_dataframe(df_1)
    df_1_bed = pybedtools.BedTool.from_dataframe(df_2)
    df_1_pg = GenomicBase(
        [(r.contig, r.pos_start, r.pos_end) for r in df_1.itertuples()]
    )
    df_2_array = df_2.values.tolist()

    df_0_gr = GenomicRanges.from_pandas(
        df_1.rename(
            columns={"contig": "seqnames", "pos_start": "starts", "pos_end": "ends"}
        )
    )
    df_1_gr = GenomicRanges.from_pandas(
        df_2.rename(
            columns={"contig": "seqnames", "pos_start": "starts", "pos_end": "ends"}
        )
    )

    for func in functions:
        times = None
        print(f"Running {func.__name__}...")
        if func == bioframe:
            times = timeit.repeat(
                lambda: func(df_1, df_2), repeat=num_repeats, number=num_executions
            )
        elif func == polars_bio:
            times = timeit.repeat(
                lambda: func(t["df_path_1"], t["df_path_2"]),
                repeat=num_repeats,
                number=num_executions,
            )
        elif func == pyranges0:
            times = timeit.repeat(
                lambda: func(df_1_pr0, df_2_pr0),
                repeat=num_repeats,
                number=num_executions,
            )
        elif func == pyranges1:
            times = timeit.repeat(
                lambda: func(df_1_pr1, df_2_pr1),
                repeat=num_repeats,
                number=num_executions,
            )
        elif func == pybedtools0:
            times = timeit.repeat(
                lambda: func(df_0_bed, df_1_bed),
                repeat=num_repeats,
                number=num_executions,
            )
        elif func == pygenomics:
            times = timeit.repeat(
                lambda: func(df_1_pg, df_2_array),
                repeat=num_repeats,
                number=num_executions,
            )
        elif func == genomicranges:
            times = timeit.repeat(
                lambda: func(df_0_gr, df_1_gr),
                repeat=num_repeats,
                number=num_executions,
            )

        per_run_times = [
            time / num_executions for time in times
        ]  # Convert to per-run times
        results.append(
            {
                "name": func.__name__,
                "min": min(per_run_times),
                "max": max(per_run_times),
                "mean": np.mean(per_run_times),
            }
        )

    fastest_mean = min(result["mean"] for result in results)
    for result in results:
        result["speedup"] = fastest_mean / result["mean"]

    # Create Rich table
    table = Table(title="Benchmark Results", box=MARKDOWN)
    table.add_column("Library", justify="left", style="cyan", no_wrap=True)
    table.add_column("Min (s)", justify="right", style="green")
    table.add_column("Max (s)", justify="right", style="green")
    table.add_column("Mean (s)", justify="right", style="green")
    table.add_column("Speedup", justify="right", style="magenta")

    # Add rows to the table
    for result in results:
        table.add_row(
            result["name"],
            f"{result['min']:.6f}",
            f"{result['max']:.6f}",
            f"{result['mean']:.6f}",
            f"{result['speedup']:.2f}x",
        )

    # Display the table
    benchmark_results = {
        # "inputs": {
        #     "df_1_num": len(df_1),
        #     "df_2_num": len(df_2),
        # },
        # "output_num": pb.overlap(df_1, df_2, col1=columns, col2=columns)
        # .collect()
        # .count(),
        "results": results,
    }
    print(t["name"])
    print(json.dumps(benchmark_results, indent=4))
    json.dump(benchmark_results, open(f"results/{t['name']}.json", "w"))
    print(table)
