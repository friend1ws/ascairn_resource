#!/bin/bash
#
# Convert legacy ascairn_resource (ver_2024-12-06) to the new panel format.
#
# Usage:
#   bash scripts/convert_legacy_to_panel.sh <legacy_dir> <output_dir> [panel_name]
#
# Example:
#   bash scripts/convert_legacy_to_panel.sh resource/ver_2024-12-06 resource ascairn_paper_2025

set -euo pipefail

if [ $# -lt 2 ] || [ $# -gt 3 ]; then
    echo "Usage: $0 <legacy_dir> <output_dir> [panel_name]"
    echo ""
    echo "Arguments:"
    echo "  legacy_dir    Path to legacy resource directory (e.g., resource/ver_2024-12-06)"
    echo "  output_dir    Path to output root (e.g., resource/)"
    echo "  panel_name    Panel name (default: ascairn_paper_2025)"
    exit 1
fi

LEGACY_DIR="$1"
OUTPUT_DIR="$2"
PANEL_NAME="${3:-ascairn_paper_2025}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
COMMON_DIR="${OUTPUT_DIR}/common"
PANEL_DIR="${OUTPUT_DIR}/panel/${PANEL_NAME}"

mkdir -p "${COMMON_DIR}"
mkdir -p "${PANEL_DIR}/kmer_info"
mkdir -p "${PANEL_DIR}/hap_info"

# Copy BED files to common/
echo "Copying BED files to common/..."
for BED_FILE in \
    cen_region_curated_margin_hg38.bed \
    cen_region_curated_margin_chm13.bed \
    chr22_long_arm_hg38.bed \
    chr22_long_arm_chm13.bed \
    chrX_short_arm_hg38.bed \
    chrX_short_arm_chm13.bed
do
    if [ -f "${LEGACY_DIR}/${BED_FILE}" ]; then
        cp "${LEGACY_DIR}/${BED_FILE}" "${COMMON_DIR}/${BED_FILE}"
        echo "  ${BED_FILE}"
    else
        echo "  WARNING: ${BED_FILE} not found"
    fi
done

# Copy rare_kmer_list.fa
echo "Copying rare_kmer_list.fa..."
cp "${LEGACY_DIR}/rare_kmer_list.fa" "${PANEL_DIR}/rare_kmer_list.fa"

# Process each chromosome
for CHR_IND in $(seq 1 22) X; do
    CHR="chr${CHR_IND}"
    echo "Processing ${CHR}..."

    # Convert kmer_info: remove Marker_num, subtract 100000 from Marker_pos, rename Study_group -> Assembly_source
    gzip -dc "${LEGACY_DIR}/kmer_info/${CHR}.kmer_info.txt.gz" \
        | awk -F'\t' 'BEGIN{OFS="\t"} NR==1{for(i=1;i<=NF;i++){if($i=="Marker_num") mn=i; if($i=="Marker_pos") mp=i; if($i=="Study_group") $i="Assembly_source"}; out=""; for(i=1;i<=NF;i++){if(i!=mn){if(out!="") out=out OFS; out=out $i}}; print out} NR>1{$mp=$mp-100000; out=""; for(i=1;i<=NF;i++){if(i!=mn){if(out!="") out=out OFS; out=out $i}}; print out}' \
        | gzip -c > "${PANEL_DIR}/kmer_info/${CHR}.kmer_info.txt.gz"

    # Generate hap_info from hap_cluster.txt + kmer_info Contig_len
    python3 "${SCRIPT_DIR}/generate_hap_info.py" \
        "${LEGACY_DIR}/cluster_m3/${CHR}.hap_cluster.txt" \
        "${LEGACY_DIR}/kmer_info/${CHR}.kmer_info.txt.gz" \
        "${PANEL_DIR}/hap_info/${CHR}.hap_info.txt"
done

echo ""
echo "Done! New panel created at: ${PANEL_DIR}"
