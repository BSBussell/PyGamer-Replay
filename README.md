# PyGamer Replay Script Documentation
> A replay management Script by Bee for usage in The Tennessee Gorilla Productions

## Introduction
PyGamer-Replay is a Python script designed for dynamically building and managing replay compilations in OBS Studio.

While existing solutions rely on storing replays in RAM, making them prone to crashes even on machines with 18GB of RAM, PyGamer-Replay takes a more RAM-concious approach by saving replays directly to disk storage. This enables smoother performance, particularly on lower-end machines.

The script leverages OBS’s built-in replay buffer, extending its functionality beyond what the stock Instant Replay script can do by allowing users to:
* Automatically save replays to a folder via hotkey.
* Compile multiple replays into a single video file with a single press.
* Instantly play the stitched compilation on a specified media source in OBS.

This is ideal for tournament streams, highlight compilations, or any scenario where you need a seamless playback of multiple replays highlights without manual video editing.


## Features
### Replay Compilation
A **Replay Compilation** is a collection of replays saved to a specified folder. This script manages this folder, and enables easy hotkeys for:
1. Saving replays to the folder.
2. Stitching each video in the folder to a single video file, and setting a media source 
3. Clearing the folder of all replays.

### Buzzwords
* **Low RAM usage** - As replays are saved directly to disk, the number of replays you can save is only limited by your storage space.
* **Customizable** - The script is highly customizable allowing you to dynamically increase the number of **Compilations** you can have through a *lightweight* configuration file, and bundled with a host of options to customize how replays are saved and built.
* **Hotkey Modularity** - Usage of the script is designed to be interfaced through hotkeys. When paired with a Stream Deck, or other macro devices, this script can be used to quickly save replays and build multiple compilations with the push of a single button.

## Installation
1. **Clone** this Repo.
2. Add `PyGamer-Replay.py` to OBS Studio Scripts.
    > *Note:* Ensure OBS is configured to run Python scripts. This is OS specific and there are a couple guides available online for setting up Python scripting with OBS Studio.

3. Ensure you have installed FFMpeg on your system. You may need to change the path to FFMpeg in the script if it is not in your system's PATH variable.
4. Configure the amount and name of compilations you would like to use in the `config.json` file. By default the script is configured to support 3 compilations, P1_Comp, P2_Comp, and GBL_Comp.
5. From there you can configure hotkeys in OBS in order to build, save, and clear replays for each compilation. You can configure hotkey bindings through the settings.
6. Configure OBS' **Replay Buffer** settings to your desired length. This can be done in the OBS settings under the "Output" tab. The script will utilize this buffer to save replays.

## Usage Guide:
### Configuring Replay Compilation's
Each **Replay Compilation** has a few key settings that must be configured before use.
1. **Folder** - The folder where replays are saved.
2. **Media Source** - The media source where the compilation will be played.
3. **Hotkeys** - The hotkeys used to save replays, build compilations, and clear the folder.

> #### Configuration File
> In order to specify the amount and names of **Replay Compilations**, you will need to edit the `config.json` file. Simply add or remove the name of the compilation you would like to add and refresh the script and the new compilation should appear in the script's settings.


### Hotkey Functions
You can configure hotkeys within OBS Studio to trigger various script functions. I recommend using a Stream Deck or similar macro device for ease of use.

#### Compilation-Specific Hotkeys
These hotkeys are specific to each compilation.
| Hotkey | Function |
|--------|----------|
| Save Replay | Saves the current replay to the folder. |
| Build Compilation | Stitches all replays in the folder to a single video file and plays it on the specified media source. |
| Clear Replays | Deletes all replays in the folder. |


#### Global Hotkeys
These hotkeys are global and perform action across all compilations.
| Hotkey | Function |
|--------|----------|
| Clear All Replays | Deletes all replays in all folders. |
| Build All Compilations | Builds each replay compilation |


### Example Workflow

I use this script in order to build highlight compilations for tournament sets as they are being played. So in a tournament format where players have multiple lives, and play multiple games. During each game I press a button on my stream deck each time a player takes a stock. This button is a macro for a hotkey that saves the replay to a compilation for that specific player.
Once the game is over, I can then press another button on my stream deck that will build a compilation of all the replays saved during that game. This will stitch together all the replays into a single video file and play it on a media source in OBS for instant replay to the viewers.
This is expanded by creating multiple compilations(and thus buttons) for each player in the set. So I can have a compilation for Player 1 and Player 2. This allows me to quickly build and showcase highlights for each player as a set progresses. So, by the end of the set, I can play a compilation of each kill scored by a specific player, and play them specifically.
As a final element, I also have a "Global" replay compilation, with the intention of saving replays from all players across all sets to. This lets me use a compilation "of the tournaments highlights" for usage as backdrops or montages during downtime in the tournament. 
This workflow works because the stream deck macro action then allows me to bind one button to trigger multiple hotkeys, so I can have a single button on my stream deck that saves a replay to Player 1's compilation, and to the Global compilaton by macroing both hotkeys in quick succession.
This allows for a streamlined process of capturing highlights without needing to manually edit videos, all you need to do is press a button when you want to add a replay to a compilation, and then another button to build the compilation and play it back.
This isn't the only way to use this script, but it is an example of how I use it in a tournament setting. The flexibility of the script allows for a wide range of use cases, from simple highlight reels to more complex workflows involving multiple players and sets.
