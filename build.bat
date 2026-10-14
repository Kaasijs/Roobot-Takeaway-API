@echo on

REM Build from src
docker build --no-cache -t kaasijs/roobotfoodapi:1.0 .
docker build --no-cache -t kaasijs/roobotfoodapi:nightly .
docker build --no-cache -t kaasijs/roobotfoodapi:latest .

REM Push
docker push kaasijs/roobotfoodapi --all-tags