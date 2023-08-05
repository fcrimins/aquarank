set -euo pipefail

ARCH=$(uname -m)
OS=$(uname)
PLATFORM="linux"
if [[ "$ARCH" == "aarch64" ]]; then
	ARCH="aarch64";
elif [[ $ARCH == "ppc64le" ]]; then
	ARCH="ppc64le";
else
	ARCH="64";
fi

mkdir -p "$1"
curl -Ls https://micro.mamba.pm/api/micromamba/$PLATFORM-$ARCH/latest | tar -xj -C "$1" --strip-components=1 bin/micromamba
