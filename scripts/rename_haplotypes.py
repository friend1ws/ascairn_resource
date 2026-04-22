#!/usr/bin/env python3
"""
Copy a panel with renamed haplotype names.

Renaming rules:
  - <sample>.pat -> <sample>.h1
  - <sample>.mat -> <sample>.h2
  - CHM13.pat / CHM13.mat -> CHM13 (strip suffix for single-haplotype genomes)
  - CHM1.pat / CHM1.mat -> CHM1

Processes under <src_dir>:
  - hap_info/*.txt       (Haplotype column, 1st column)
  - kmer_info/*.txt.gz   (Haplotype column)
  - rare_kmer_list.fa    (copied as-is)

Output is written to <dst_dir> (created if missing).

Usage:
    python3 rename_haplotypes.py <src_dir> <dst_dir>

Example:
    python3 rename_haplotypes.py \\
        ~/project/cen_marker/ascairn_data/data260401 \\
        ../resource/panel/ascairn_paper_2025
"""

import gzip
import os
import shutil
import sys


SINGLE_HAP_GENOMES = {"CHM13", "CHM1"}


def convert(name):
    for prefix in SINGLE_HAP_GENOMES:
        if name == f"{prefix}.pat" or name == f"{prefix}.mat":
            return prefix
    if name.endswith(".pat"):
        return name[:-4] + ".h1"
    if name.endswith(".mat"):
        return name[:-4] + ".h2"
    return name


def process_hap_info(src, dst):
    with open(src) as f:
        lines = f.readlines()
    with open(dst, "w") as f:
        f.write(lines[0])
        for line in lines[1:]:
            parts = line.rstrip("\n").split("\t")
            parts[0] = convert(parts[0])
            f.write("\t".join(parts) + "\n")
    return len(lines) - 1


def process_kmer_info(src, dst):
    with gzip.open(src, "rt") as fin:
        header = fin.readline()
        hap_idx = header.rstrip("\n").split("\t").index("Haplotype")
        with gzip.open(dst, "wt") as fout:
            fout.write(header)
            n = 0
            for line in fin:
                parts = line.rstrip("\n").split("\t")
                parts[hap_idx] = convert(parts[hap_idx])
                fout.write("\t".join(parts) + "\n")
                n += 1
    return n


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    src_dir = sys.argv[1]
    dst_dir = sys.argv[2]

    # hap_info: source may be named hap_info_m3 or hap_info
    src_hap_info = os.path.join(src_dir, "hap_info")
    if not os.path.isdir(src_hap_info):
        src_hap_info = os.path.join(src_dir, "hap_info_m3")
    src_kmer_info = os.path.join(src_dir, "kmer_info")

    dst_hap_info = os.path.join(dst_dir, "hap_info")
    dst_kmer_info = os.path.join(dst_dir, "kmer_info")
    os.makedirs(dst_hap_info, exist_ok=True)
    os.makedirs(dst_kmer_info, exist_ok=True)

    for fname in sorted(os.listdir(src_hap_info)):
        if not fname.endswith(".txt"):
            continue
        n = process_hap_info(os.path.join(src_hap_info, fname),
                             os.path.join(dst_hap_info, fname))
        print(f"hap_info/{fname}: {n} rows")

    for fname in sorted(os.listdir(src_kmer_info)):
        if not fname.endswith(".txt.gz"):
            continue
        n = process_kmer_info(os.path.join(src_kmer_info, fname),
                              os.path.join(dst_kmer_info, fname))
        print(f"kmer_info/{fname}: {n} rows")

    src_fa = os.path.join(src_dir, "rare_kmer_list.fa")
    if os.path.isfile(src_fa):
        shutil.copy(src_fa, os.path.join(dst_dir, "rare_kmer_list.fa"))
        print("rare_kmer_list.fa: copied")


if __name__ == "__main__":
    main()
