@echo off
git remote set-url origin https://github.com/eziaiexplorer-gif/SHOTCRAFTVID-UPGRADE.git 2>nul || git remote add origin https://github.com/eziaiexplorer-gif/SHOTCRAFTVID-UPGRADE.git
git branch -M main
git push -u origin main --tags
