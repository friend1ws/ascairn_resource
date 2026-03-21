# ascairn_resource

Resource files for [ascairn](https://github.com/friend1ws/ascairn), software for estimating centromere variation from short-read sequencing data.

## Directory Structure

```
resource/
├── common/                              # Shared across all panels
│   ├── cen_region_curated_margin_hg38.bed
│   ├── cen_region_curated_margin_chm13.bed
│   ├── chr22_long_arm_hg38.bed
│   ├── chr22_long_arm_chm13.bed
│   ├── chrX_short_arm_hg38.bed
│   └── chrX_short_arm_chm13.bed
├── panel/
│   └── ascairn_paper_2025/              # Default panel (HPRC Year 1, HGSVC Phase 3, CHM13, CHM1, HG002)
│       ├── rare_kmer_list.fa
│       ├── kmer_info/
│       │   ├── chr1.kmer_info.txt.gz
│       │   ├── ...
│       │   └── chrX.kmer_info.txt.gz
│       └── hap_info/
│           ├── chr1.hap_info.txt
│           ├── ...
│           └── chrX.hap_info.txt
└── legacy/
    └── ver_2024-12-06/                  # Previous format (kept for backward compatibility)
```

## File Descriptions

### common/

BED files defining genomic regions used by ascairn. These are shared across all panels.

| File | Description |
|------|-------------|
| `cen_region_curated_margin_{hg38,chm13}.bed` | Centromere alpha-satellite regions with 100 kbp margins on each side. Used by `kmer_count` to extract reads for k-mer counting. |
| `chr22_long_arm_{hg38,chm13}.bed` | A non-centromeric region on the chr22 long arm. Used by `check_depth` as a baseline for estimating sequencing coverage. |
| `chrX_short_arm_{hg38,chm13}.bed` | A non-centromeric region on the chrX short arm. Used by `check_depth` to determine biological sex by comparing chrX coverage to the baseline. |

### panel/

Each subdirectory under `panel/` is a self-contained reference panel. A panel contains three components:

#### `rare_kmer_list.fa`

FASTA file listing rare k-mer sequences used as markers for centromere classification. Used by the `kmer_count` step.

#### `kmer_info/{chr}.kmer_info.txt.gz`

Gzipped TSV file describing where each rare k-mer (marker) occurs in the reference haplotypes. One file per chromosome.

**Required columns:**

| Column | Description |
|--------|-------------|
| `Marker` | K-mer sequence |
| `Haplotype` | Haplotype identifier (e.g., `HG00438.pat`) |

Each row represents one occurrence of a marker in a haplotype. If a marker appears multiple times in a haplotype (copy number > 1), there will be multiple rows for that `Marker` × `Haplotype` pair.

**Optional columns:**

| Column | Description |
|--------|-------------|
| `Assembly_source` | Assembly project or source from which the haplotype was derived |
| `Contig_len` | Length of the centromeric contig for this haplotype (excluding margins) |
| `Marker_pos` | Position of the marker relative to the start of the centromeric contig. The original contig sequence includes 100,000 bp margins on both ends; `Marker_pos` is adjusted so that position 0 corresponds to the start of the centromeric region itself. Values can be negative (marker in the upstream margin) or exceed `Contig_len` (marker in the downstream margin). |
| `Marker_strand` | Strand orientation of the marker (`+` or `-`) |

Additional columns may be present and will be ignored by ascairn.

**Example:**
```
Marker	Haplotype	Assembly_source	Contig_len	Marker_pos	Marker_strand
CCCAGGTGGTTAATGATGCATTTTTCA	HG00438.mat	f1_assembly_v2_genbank	3165450	-98714	+
CCCAGGTGGTTAATGATGCATTTTTCA	HG00438.pat	f1_assembly_v2_genbank	2444327	-98700	+
```

#### `hap_info/{chr}.hap_info.txt`

TSV file mapping each haplotype to a cluster and providing optional annotations. One file per chromosome.

**Required columns:**

| Column | Description |
|--------|-------------|
| `Haplotype` | Haplotype identifier (must match values in `kmer_info`) |
| `Cluster` | Cluster ID assigned to this haplotype |

**Optional columns:**

Any additional columns beyond `Haplotype` and `Cluster` are treated as annotations and propagated to the ascairn output. See the [ascairn README](https://github.com/friend1ws/ascairn#output-format) for details.

| Column | Description |
|--------|-------------|
| `Contig_len` | Length of the centromeric contig |

**Example:**
```
Haplotype	Cluster	Contig_len
HG00438.pat	1	2444327
HG02300.mat	1	4323166
NA20355.mat	1	1686442
```

## License

See [LICENSE](LICENSE).
