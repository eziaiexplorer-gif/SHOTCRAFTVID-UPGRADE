#!/usr/bin/env sh
set -eu
git remote set-url origin https://github.com/eziaiexplorer-gif/SHOTCRAFTVID-UPGRADE.git 2>/dev/null || git remote add origin https://github.com/eziaiexplorer-gif/SHOTCRAFTVID-UPGRADE.git
git branch -M main
git push -u origin main --tags
