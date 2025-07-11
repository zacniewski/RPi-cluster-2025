echo "[1. Updating and upgrading (apt) ......]" &&
sudo apt update &&
sudo apt upgrade &&
sudo apt dist-upgrade &&
echo "" &&
echo "[2. Cleaning Up ......]" &&
sudo apt autoremove &&
sudo apt autoclean &&
sudo apt clean &&
sudo apt autopurge &&
echo "" &&
echo "[3. Done ......!!!!]" &&
echo ""