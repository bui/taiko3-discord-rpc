## taiko3-discord-rpc
Discord rich presence integration for *Taiko no Tatsujin: Atsumete Tomodachi Daisakusen!* (太鼓の達人 あつめて★ともだち大作戦！)

The inspiration for this project came from [jam1garner](https://github.com/jam1garner)'s [integration](https://github.com/jam1garner/smash-disc4d) for Smash Bros.

## Setup
To use this program, you'll need to download its two dependencies manually.
* **[pypresence](https://github.com/qwertyquerty/pypresence)** - drop `pypresence.py` in the same directory as `taiko.py`
* **[pyGecko](https://github.com/wiiudev/pyGecko)** - drop `tcpgecko.py` and `common.py` in the same directory as `taiko.py`.
	* You'll also need to convert `tcpgecko.py` to Python 3 using `2to3`. For example: `2to3 -w tcpgecko.py`

Song titles in `data/song_data.json` are ripped from the game data using `extract_songs.py`, but a pre-built version is provided for your convenience. This build includes all DLC songs.

## Usage
1. Run tcpGecko on your Wii U
2. Run Taiko no Tatsujin on your Wii U (not required if you use `--launch-auto`)
3. Run `taiko.py` supplying your Wii U's IP address
	* For example: `./taiko.py 192.168.0.10`
	* Use `--client-id [ID]` if you want to use your own Discord application
4. Start playing!
