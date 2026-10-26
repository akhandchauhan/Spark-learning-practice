#!/usr/bin/env bash
# Standalone cluster inside this container: 1 master + 2 workers. The driver is the notebook kernel.
# Same classes that sbin/start-master.sh and start-worker.sh launch, so it only needs the pip pyspark package.
export SPARK_HOME=$(python -c "import pyspark, os; print(os.path.dirname(pyspark.__file__))")
pgrep -f deploy.master.Master > /dev/null && exit 0
mkdir -p /tmp/spark-logs
nohup "$SPARK_HOME/bin/spark-class" org.apache.spark.deploy.master.Master --host localhost --port 7077 --webui-port 8080 > /tmp/spark-logs/master.log 2>&1 &
for i in 1 2; do
  nohup "$SPARK_HOME/bin/spark-class" org.apache.spark.deploy.worker.Worker --cores 1 --memory 1g --webui-port $((8080 + i)) spark://localhost:7077 > /tmp/spark-logs/worker$i.log 2>&1 &
done
