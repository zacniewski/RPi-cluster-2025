# Troubleshooting

Common issues and solutions for the MLOps system on the Raspberry Pi cluster.

## Table of Contents
- [Connection Issues](#connection-issues)
- [Docker Issues](#docker-issues)
- [Data Ingestion Issues](#data-ingestion-issues)
- [Training Issues](#training-issues)
- [Serving Issues](#serving-issues)
- [MLflow Issues](#mlflow-issues)
- [Pipeline Issues](#pipeline-issues)
- [Performance Tips](#performance-tips)

---

## Connection Issues

### Cannot SSH to a node

**Symptom:** `ssh: connect to host knight-cluster port 22: Connection refused`

**Solutions:**
1. Check the node is powered on and connected to the switch
2. Verify the hostname resolves: `ping knight-cluster`
3. If using hostnames, check `/etc/hosts` on your machine
4. Verify SSH is running on the node: `ssh artur@<IP-address>` using the IP directly
5. Re-check passwordless SSH setup: [07_git_and_passwordless_SSH_configuration.md](../../docs/07_git_and_passwordless_SSH_configuration.md)

### Cannot reach a service (connection refused on port)

**Symptom:** `curl: (7) Failed to connect to rook-cluster port 8080`

**Solutions:**
1. Check the Docker container is running: `ssh artur@rook-cluster docker ps`
2. Check container logs: `ssh artur@rook-cluster "cd /home/artur/SERVING/app && docker compose logs"`
3. Verify the port mapping in `docker-compose.yml`
4. Check if the container crashed: `ssh artur@rook-cluster docker ps -a`

---

## Docker Issues

### Container fails to build

**Symptom:** `pip install` fails during Docker build

**Solutions:**
1. Check internet connectivity on the node: `ssh artur@<node> curl -s https://pypi.org`
2. For ARM64 compatibility issues, check if the package supports `aarch64`
3. Try building with `--no-cache`: `docker compose build --no-cache`
4. Check available disk space: `ssh artur@<node> df -h`

### Container keeps restarting

**Symptom:** `docker ps` shows container restarting

**Solutions:**
1. Check logs: `docker compose logs --tail 50`
2. Common causes:
   - Missing config file (volume not mounted correctly)
   - Port already in use by another service
   - Python import error (missing dependency)
3. Run the container interactively to debug: `docker compose run --rm <service> bash`

### Out of disk space

**Symptom:** `No space left on device`

**Solutions:**
1. Clean unused Docker images: `docker system prune -f`
2. Remove old model artifacts or datasets
3. Check NVMe usage: `df -h /`

---

## Data Ingestion Issues

### Validation fails

**Symptom:** Ingestion returns `status: failed`

**Solutions:**
1. Check the validation report in the response or in `/home/artur/DATA/logs/ingestion_log.jsonl`
2. Common causes:
   - Missing columns — update `validation_rules.yaml` to match your data
   - Wrong dtypes — the validator tries auto-casting, but some types cannot be converted
   - Values out of range — adjust `range_checks` in the rules
   - Too many missing values — clean your data or increase `max_missing_pct`

### Push to knight-cluster fails

**Symptom:** `rsync` error during push

**Solutions:**
1. Verify SSH from pawn to knight works: `docker compose exec pawn-ingestion ssh artur@knight-cluster echo ok`
2. Check that the SSH key is mounted: the `~/.ssh` volume must be in `docker-compose.yml`
3. Ensure the destination directory exists on knight: `ssh artur@knight-cluster ls /home/artur/TRAINING/data/`

---

## Training Issues

### No dataset found

**Symptom:** `FileNotFoundError: /data/latest.csv`

**Solutions:**
1. Run ingestion first with `--push`: the dataset must be pushed from pawn to knight
2. Check the file exists: `ssh artur@knight-cluster ls /home/artur/TRAINING/data/`
3. Verify the `dataset_path` in `training_config.yaml` matches the actual file location

### MLflow logging fails

**Symptom:** Warning about MLflow connection

**Solutions:**
1. This is non-fatal — training continues without tracking
2. Check MLflow is running: `curl http://queen-cluster:5000/`
3. Verify `MLFLOW_TRACKING_URI` in the knight's `docker-compose.yml`
4. Check network connectivity from knight to queen: `ssh artur@knight-cluster curl -s http://queen-cluster:5000/`

### Out of memory during training

**Symptom:** Container killed (OOMKilled)

**Solutions:**
1. Use a simpler model (e.g., `logistic_regression` instead of `random_forest`)
2. Reduce `n_estimators` or `max_depth` in hyperparameters
3. Use a smaller dataset
4. Check available memory: `ssh artur@knight-cluster free -h`

---

## Serving Issues

### No model loaded (503 error)

**Symptom:** `POST /predict` returns 503 "No model loaded"

**Solutions:**
1. Check if a model file exists: `ssh artur@rook-cluster ls /home/artur/SERVING/models/`
2. If empty, run training with `--push` first
3. Force reload: `curl -X POST http://rook-cluster:8080/reload`
4. Check container logs for model loading errors

### Wrong predictions

**Solutions:**
1. Verify the model was trained on the correct dataset
2. Check that the feature order in `schemas.py` matches the training data column order
3. Retrain with a different model type or hyperparameters
4. Check MLflow for the model's metrics — low accuracy indicates a data or model issue

---

## MLflow Issues

### MLflow UI not loading

**Symptom:** Browser shows connection error at `http://queen-cluster:5000`

**Solutions:**
1. Check the container: `ssh artur@queen-cluster docker ps | grep mlflow`
2. Check logs: `ssh artur@queen-cluster "cd /home/artur/ORCHESTRATION/app && docker compose logs mlflow"`
3. Verify port 5000 is not used by another service
4. Restart: `ssh artur@queen-cluster "cd /home/artur/ORCHESTRATION/app && docker compose restart mlflow"`

### MLflow database corrupted

**Solutions:**
1. Stop MLflow: `docker compose stop mlflow`
2. Back up the database: `cp /home/artur/ORCHESTRATION/mlflow/mlflow.db /home/artur/ORCHESTRATION/mlflow/mlflow.db.bak`
3. Delete and restart (loses history): `rm /home/artur/ORCHESTRATION/mlflow/mlflow.db && docker compose up -d mlflow`

---

## Pipeline Issues

### Pipeline step times out

**Symptom:** Step fails with timeout error

**Solutions:**
1. Increase the timeout in `pipeline_config.yaml` for the affected step
2. Check if the target node's service is running
3. Training can be slow on RPi — consider reducing dataset size or model complexity

### Scheduler not running

**Solutions:**
1. Check status: `curl http://queen-cluster:8083/scheduler/status`
2. Start it: `curl -X POST http://queen-cluster:8083/scheduler/start`
3. Check orchestrator logs: `docker compose logs orchestrator`

---

## Performance Tips

- **Use NVMe storage** for all data directories — SD cards are too slow for model training
- **Keep models small** — Random Forest with 100 estimators trains in seconds on RPi 5
- **Use joblib format** — faster to save/load than pickle for scikit-learn models
- **Monitor memory** — RPi 5 has 4-8 GB RAM; large datasets may need chunked processing
- **Clean old artifacts** — periodically remove old model files and datasets to free disk space
- **Use batch predictions** — the `/predict/batch` endpoint is more efficient than calling `/predict` in a loop
