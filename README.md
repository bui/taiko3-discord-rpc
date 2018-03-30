## taiko3-discord-rpc
Discord rich presence integration for *Taiko no Tatsujin* titles on Wii U.

![](https://s7.postimg.org/vltjohifv/taiko_screen.png)

### Supported titles
* *[Taiko no Tatsujin: Wii U Version!](http://wiiu.taiko-ch.net/)* (太鼓の達人 Wii Uば～じょん！)
* *[Taiko no Tatsujin: Tokumori!](http://wiiu2.taiko-ch.net/)* (太鼓の達人 特盛り！)
* *[Taiko no Tatsujin: Atsumete Tomodachi Daisakusen!](http://wiiu3.taiko-ch.net/)* (太鼓の達人 あつめて★ともだち大作戦！)

## Binaries
You can find pre-build binaries on the [Releases](https://github.com/bui/taiko3-discord-rpc/releases) page. They include a configuration file that you can edit, and batch files to auto-launch each title.

## Setup
To use this program, you'll need to download its two dependencies manually.
* **[pypresence](https://github.com/qwertyquerty/pypresence)** - drop `pypresence.py` in the same directory as `taiko.py`
* **[pyGecko](https://github.com/wiiudev/pyGecko)** - drop `tcpgecko.py` and `common.py` in the same directory as `taiko.py`
	* You'll also need to convert `tcpgecko.py` to Python 3 using `2to3`. For example: `2to3 -w tcpgecko.py`

Song data in `data/` is ripped from the game using `extract_songs.py`, but pre-built versions are provided for your convenience. These versions include all DLC songs.

## Usage
1. Run [tcpGecko](https://github.com/BullyWiiPlaza/tcpgecko) on your Wii U
2. Run a *Taiko no Tatsujin* title on your Wii U (not required if you use `--launch-auto`)
3. Run `taiko.py` supplying your Wii U's IP address
	* For example: `./taiko.py 192.168.0.10`
	* Use `--client-id [ID]` if you want to use your own Discord application
4. Start playing!

## Warnings
* Avoid accessing any Miiverse features in the game, as this tends to crash tcpGecko. If you see the screen below during game startup, select the right option (いいえ).<br>
![](https://s7.postimg.org/c9fz4h8ff/Honeyview_cc.png)