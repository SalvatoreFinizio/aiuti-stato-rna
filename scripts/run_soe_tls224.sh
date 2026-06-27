#!/bin/bash
D="/Users/salvatorefinizio/Library/CloudStorage/Dropbox/PATSTAT/Autumn 2025/unzipped"
t0=$(date +%s)
LC_ALL=C awk -F, '
  NR==FNR{a[$1]=1; next}
  $1=="appln_id"{next}
  ($1 in a){print $1","$2}
' /tmp/soe_applns.txt "$D/tls224_appln_cpc_part01.csv" "$D/tls224_appln_cpc_part02.csv" > /tmp/soe_cpc.csv
echo "DONE_SOE_TLS224 rows=$(wc -l < /tmp/soe_cpc.csv) elapsed=$(( $(date +%s)-t0 ))s"
