#!/bin/bash
D="/Users/salvatorefinizio/Library/CloudStorage/Dropbox/PATSTAT/Autumn 2025/unzipped"
t0=$(date +%s)
LC_ALL=C awk -F, '
  NR==FNR { fam[$1]=1; next }
  $1=="appln_id" { next }
  ($22 in fam) { y=$16+0; if(y>=1900 && y<=2026){ if(!($22 in mn) || y<mn[$22]) mn[$22]=y } }
  END { for(f in mn) print f","mn[f] }
' /tmp/aid_families.txt "$D/tls201_appln_part01.csv" "$D/tls201_appln_part02.csv" "$D/tls201_appln_part03.csv" > /tmp/fam_year.csv
echo "DONE_TLS201 families_with_year=$(wc -l < /tmp/fam_year.csv) elapsed=$(( $(date +%s)-t0 ))s"
