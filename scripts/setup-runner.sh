#!/usr/bin/env bash
# setup-runner.sh — Install GitHub Actions self-hosted runner on HO-GPU-01 / HO-RUNNER-01
# Run as: raylee@192.168.8.200
# Usage: bash setup-runner.sh <GITHUB_RUNNER_TOKEN>
# Get token from: https://github.com/raylee-hawkins/HawkinsOperations/settings/actions/runners/new
set -euo pipefail

TOKEN="${1:-}"
if [[ -z "$TOKEN" ]]; then
  echo "Usage: $0 <GITHUB_RUNNER_TOKEN>"
  echo "Get token at: https://github.com/raylee-hawkins/HawkinsOperations/settings/actions/runners/new"
  exit 1
fi

echo "=== Step 1: System packages ==="
sudo apt-get update -qq
sudo apt-get install -y curl git

echo "=== Step 2: PowerShell 7 ==="
if command -v pwsh &>/dev/null; then
  echo "pwsh already installed: $(pwsh --version)"
else
  # Ubuntu 24.04 LTS
  wget -q "https://packages.microsoft.com/config/ubuntu/24.04/packages-microsoft-prod.deb" -O /tmp/ms-prod.deb
  sudo dpkg -i /tmp/ms-prod.deb
  sudo apt-get update -qq
  sudo apt-get install -y powershell
  echo "pwsh installed: $(pwsh --version)"
fi

echo "=== Step 3: Node.js 20 LTS ==="
CURRENT_NODE=$(node --version 2>/dev/null || echo "none")
if [[ "$CURRENT_NODE" == v20* ]]; then
  echo "Node.js 20 already installed: $CURRENT_NODE"
else
  echo "Upgrading from $CURRENT_NODE to Node.js 20 LTS"
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
  echo "node installed: $(node --version)"
fi

echo "=== Step 4: GitHub Actions runner ==="
mkdir -p ~/actions-runner && cd ~/actions-runner

# Fetch latest runner version from GitHub
RUNNER_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest | grep '"tag_name"' | sed 's/.*"v\([^"]*\)".*/\1/')
RUNNER_FILENAME="actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_FILENAME}"

echo "Downloading runner v${RUNNER_VERSION}..."
curl -sLo "${RUNNER_FILENAME}" "${RUNNER_URL}"
tar xzf "${RUNNER_FILENAME}"

echo "=== Step 5: Configure runner ==="
./config.sh \
  --url "https://github.com/raylee-hawkins/HawkinsOperations" \
  --token "${TOKEN}" \
  --name "HO-RUNNER-01" \
  --labels "self-hosted,linux,x64,hawkinsops" \
  --unattended

echo "=== Step 6: Install and start service ==="
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status

echo ""
echo "=== Done! ==="
echo "Runner status: https://github.com/raylee-hawkins/HawkinsOperations/settings/actions/runners"
pwsh --version
node --version
python3 --version
git --version
