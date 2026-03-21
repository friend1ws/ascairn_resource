#!/usr/bin/env python3
"""
Generate hap_info.txt from hap_cluster.txt and kmer_info.txt.gz.

Usage:
    python3 generate_hap_info.py <hap_cluster_file> <kmer_info_file> <output_file>

hap_info.txt format:
    Haplotype  Cluster  Contig_len
"""

import gzip
import sys
from collections import OrderedDict


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 generate_hap_info.py <hap_cluster_file> <kmer_info_file> <output_file>")
        sys.exit(1)

    hap_cluster_file = sys.argv[1]
    kmer_info_file = sys.argv[2]
    output_file = sys.argv[3]

    # Read hap_cluster.txt: Haplotype -> Cluster
    hap_cluster = OrderedDict()
    with open(hap_cluster_file, "r") as f:
        f.readline()  # skip header
        for line in f:
            fields = line.rstrip("\n").split("\t")
            hap_cluster[fields[0]] = fields[1]

    # Extract unique Haplotype -> Contig_len from kmer_info
    hap_contig_len = {}
    with gzip.open(kmer_info_file, "rt") as f:
        header = f.readline().rstrip("\n").split("\t")
        hap_idx = header.index("Haplotype")
        contig_len_idx = header.index("Contig_len")
        for line in f:
            fields = line.rstrip("\n").split("\t")
            hap = fields[hap_idx]
            if hap not in hap_contig_len:
                hap_contig_len[hap] = fields[contig_len_idx]

    # Write hap_info.txt
    with open(output_file, "w") as f:
        f.write("Haplotype\tCluster\tContig_len\n")
        for hap, cluster in hap_cluster.items():
            contig_len = hap_contig_len.get(hap, "NA")
            f.write(f"{hap}\t{cluster}\t{contig_len}\n")


if __name__ == "__main__":
    main()
