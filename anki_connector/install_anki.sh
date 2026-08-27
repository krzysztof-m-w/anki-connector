#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="/usr/local/share/anki"
BIN_PATH="/usr/local/bin/anki"
TMP_DIR="$(mktemp -d)"

cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

API_HEADERS=(
    -H "Accept: application/vnd.github+json"
    -H "X-GitHub-Api-Version: 2022-11-28"
)

echo "Checking for the newest Anki release..."

# Download release metadata completely before parsing it.
curl -fsSL \
    "${API_HEADERS[@]}" \
    "https://api.github.com/repos/ankitects/anki/releases/latest" \
    -o "$TMP_DIR/release.json"

if command -v jq >/dev/null 2>&1; then
    VERSION="$(jq -r '.tag_name' "$TMP_DIR/release.json")"
else
    VERSION="$(
        sed -nE 's/^[[:space:]]*"tag_name":[[:space:]]*"([^"]+)".*/\1/p' \
            "$TMP_DIR/release.json" |
        head -n1
    )"
fi

if [[ -z "$VERSION" || "$VERSION" == "null" ]]; then
    echo "ERROR: Could not determine the latest Anki version."
    exit 1
fi

echo "Latest stable Anki: $VERSION"

echo "Finding Linux x86-64 package..."

if command -v jq >/dev/null 2>&1; then
    ASSET_URL="$(
        jq -r '
            .assets[]
            | select(
                (.name | test("linux"; "i"))
                and
                (.name | test("x86_64|amd64"; "i"))
                and
                (.name | test("\\.(tar\\.zst|tar\\.gz)$"))
            )
            | .browser_download_url
        ' "$TMP_DIR/release.json" |
        head -n1
    )"
else
    ASSET_URL="$(
        grep '"browser_download_url":' "$TMP_DIR/release.json" |
        grep -Ei 'linux.*(x86_64|amd64).*\.(tar\.zst|tar\.gz)' |
        sed -E 's/.*"browser_download_url":[[:space:]]*"([^"]+)".*/\1/' |
        head -n1
    )"
fi

if [[ -z "$ASSET_URL" ]]; then
    echo "ERROR: Could not find a Linux x86-64 Anki package."
    echo
    echo "Available assets:"
    if command -v jq >/dev/null 2>&1; then
        jq -r '.assets[].name' "$TMP_DIR/release.json"
    else
        grep '"name":' "$TMP_DIR/release.json"
    fi
    exit 1
fi

echo "Downloading:"
echo "  $ASSET_URL"

ARCHIVE="$TMP_DIR/anki.tar.zst"

curl -fL --progress-bar \
    "$ASSET_URL" \
    -o "$ARCHIVE"

echo "Extracting..."

mkdir -p "$TMP_DIR/extracted"

tar --zstd -xf "$ARCHIVE" -C "$TMP_DIR/extracted"

# Locate the actual Anki executable.
ANKI_BIN="$(
    find "$TMP_DIR/extracted" \
        -type f \
        -name "anki" \
        -perm -u+x \
        -print -quit
)"

if [[ -z "$ANKI_BIN" ]]; then
    echo "ERROR: Could not find the Anki executable after extraction."
    exit 1
fi

ANKI_DIR="$(dirname "$ANKI_BIN")"

echo "Installing Anki to:"
echo "  $INSTALL_DIR"

# Install only after the download and extraction succeeded.
sudo rm -rf "$INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"
sudo cp -a "$ANKI_DIR"/. "$INSTALL_DIR"/

# System-wide command.
sudo ln -sfn "$INSTALL_DIR/anki" "$BIN_PATH"

echo
echo "======================================"
echo " Anki $VERSION installed successfully"
echo "======================================"
echo
echo "Run:"
echo "  anki"