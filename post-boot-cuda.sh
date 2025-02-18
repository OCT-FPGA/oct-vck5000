#!/usr/bin/env bash

sudo apt update
sudo apt install -y nvidia-driver-535
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt --fix-broken install -y
sudo apt update && sudo apt upgrade -y
sudo apt install -y cuda-12-2
