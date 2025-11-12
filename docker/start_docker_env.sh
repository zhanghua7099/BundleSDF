#!/usr/bin/env bash
set -euo pipefail

CONTAINER="bundlesdf"
IMAGE="zhiyuanc/bundlesdf:latest"
DIR="$(cd .. && pwd)"

# Using `./run_bundlesdf.sh --recreate` to recreate the container.
if [[ "${1-}" == "--recreate" ]]; then
  if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER"; then
    docker rm -f "$CONTAINER"
  fi
fi

if command -v xhost >/dev/null 2>&1; then
  xhost +local:root >/dev/null 2>&1 || true
fi

# If not exist container, create it.
if ! docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo ">> Creating container: $CONTAINER"
  exec docker run --gpus all --env NVIDIA_DISABLE_REQUIRE=1 \
    -it --network host --name "$CONTAINER" \
    --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
    -v /home:/home -v /tmp:/tmp -v /mnt:/mnt -v "$DIR":"$DIR" \
    --ipc host \
    -e DISPLAY="$DISPLAY" -e GIT_INDEX_FILE \
    "$IMAGE" bash -lc "cd '$DIR'; exec bash"
fi

# If exist, directly run.
if [[ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER")" != "true" ]]; then
  echo ">> Starting container: $CONTAINER"
  docker start "$CONTAINER" >/dev/null
fi

exec docker exec -it \
  -e DISPLAY="$DISPLAY" \
  -w "$DIR" \
  "$CONTAINER" bash -l
