#!/bin/bash
D="/Users/salvatorefinizio/Library/CloudStorage/Dropbox/PATSTAT/Autumn 2025/unzipped"
t0=$(date +%s)
LC_ALL=C awk -F, '
  NR==FNR{f[$1]=1; next}
  $1=="appln_id"{next}
  ($22 in f){ print $22","($16+0)","$1 }
' /tmp/soe_families.txt "$D/tls201_appln_part01.csv" "$D/tls201_appln_part02.csv" "$D/tls201_appln_part03.csv" > /tmp/soe_appln.csv
echo "DONE_SOE_TLS201 rows=$(wc -l < /tmp/soe_appln.csv) elapsed=$(( $(date +%s)-t0 ))s"
