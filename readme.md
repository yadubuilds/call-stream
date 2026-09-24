winget install Gyan.FFmpeg

termux-wake-lock

pkg update && pkg upgrade -y

pkg install python git ffmpeg -y

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

pip install ntgcalls==2.2.5