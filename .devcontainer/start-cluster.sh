#!/usr/bin/env bash
# Standalone cluster inside this container: 1 master + 2 workers. The driver is the notebook kernel.
# Starts only what is missing, so it is safe to re-run. setsid detaches each process from the Codespaces startup shell.
export SPARK_HOME=$(python -c "import pyspark, os; print(os.path.dirname(pyspark.__file__))")
LOGS=/tmp/spark-logs
mkdir -p "$LOGS"
start() { local name=$1; shift; setsid nohup "$SPARK_HOME/bin/spark-class" "$@" > "$LOGS/$name.log" 2>&1 < /dev/null & }

pgrep -f deploy.master.Master > /dev/null ||
  start master org.apache.spark.deploy.master.Master --host localhost --port 7077 --webui-port 8080

for _ in $(seq 60); do (echo > /dev/tcp/localhost/7077) 2>/dev/null && break; sleep 1; done

for i in 1 2; do
  pgrep -f "deploy.worker.Worker.*--webui-port 808$i" > /dev/null ||
    start worker$i org.apache.spark.deploy.worker.Worker --cores 1 --memory 1g --webui-port 808$i spark://localhost:7077
done

sleep 5
echo "Spark workers running: $(pgrep -fc deploy.worker.Worker) (expected 2). Logs: $LOGS"
