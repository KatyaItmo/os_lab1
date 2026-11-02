#!/usr/bin/env bash
set -euo pipefail

CORE=2
N=10
ITER=20
OUT=results_graph_traverse.csv
GRAPH=graph-rand.bin

echo "timestamp,graph,op,run_id,wall_time_s,user_time_s,sys_time_s,vol_ctx,invol_ctx,minflt,majflt" > "$OUT"

ts=$(date +%s)
/usr/bin/time \
 -f "$ts,$GRAPH,read,warmup_1,%e,%U,%S,%w,%c,%R,%F" \
 -a -o "$OUT" \
 taskset -c "$CORE" ./out/graph_traverse "$ITER" "$GRAPH" \
 > /dev/null

/usr/bin/time \
 -f "$ts,$GRAPH,read,warmup_2,%e,%U,%S,%w,%c,%R,%F" \
 -a -o "$OUT" \
 taskset -c "$CORE" ./out/graph_traverse "$ITER" "$GRAPH" \
 > /dev/null

/usr/bin/time \
 -f "$ts,$GRAPH,write,warmup_1,%e,%U,%S,%w,%c,%R,%F" \
 -a -o "$OUT" \
 taskset -c "$CORE" ./out/graph_traverse --write "$ITER" "$GRAPH" \
 > /dev/null

/usr/bin/time \
 -f "$ts,$GRAPH,write,warmup_2,%e,%U,%S,%w,%c,%R,%F" \
 -a -o "$OUT" \
 taskset -c "$CORE" ./out/graph_traverse --write "$ITER" "$GRAPH" \
 > /dev/null

for i in $(seq 1 "$N"); do
  ts=$(date +%s)

  /usr/bin/time \
   -f "$ts,$GRAPH,read,$i,%e,%U,%S,%w,%c,%R,%F" \
   -a -o "$OUT" \
   taskset -c "$CORE" ./out/graph_traverse "$ITER" "$GRAPH" \
   > /dev/null

  /usr/bin/time \
   -f "$ts,$GRAPH,write,$i,%e,%U,%S,%w,%c,%R,%F" \
   -a -o "$OUT" \
   taskset -c "$CORE" ./out/graph_traverse --write "$ITER" "$GRAPH" \
   > /dev/null
done
