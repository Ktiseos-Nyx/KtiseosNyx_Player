# KtiseosNyx_Player

**WARNING: AUDIO PLAYER IN EXTREME DEVELOPMENT. MAY SPONTANEOUSLY COMBUST YOUR EARDRUMS. PROCEED WITH CAUTION (AND EARPLUGS).**

A *supposedly* simple audio player built with PyQt6, featuring playlist support (if you can call it that).  Currently, it's more of an "audio roulette" – you might get music, you might get silence, you might get a sound so loud it registers on the Richter scale.  We're working on it (maybe).

Basically, this project is what happens when someone says, "Can it be done?" instead of "Should it be done?". The answer, apparently, is "sort of, but at what cost?".

<img width="446" alt="Screenshot 2025-03-19 at 23 20 45" src="https://github.com/user-attachments/assets/33e98379-5239-4fd7-a29d-ed9699315b0b" />

## Features (Planned, Implemented, or Imagined):

*   **Plays Audio (Sometimes):**  When it feels like it, the player *might* play audio files. Success rate varies depending on the alignment of the planets and the whims of the Python interpreter.
*   **Playlist Support (Sort Of):**  You can drag and drop files, folders, and even those ancient .m3u things.  Whether they play in the order you expect is a mystery for the ages.
*   **Volume Control (Potentially Lethal):**  There's a slider. It *claims* to control the volume.  We recommend starting with it at 0 and inching it up *very* slowly, while wearing hearing protection and possibly a bomb suit.
*   **Mute Button (A Glimmer of Hope):**  There's a mute button.  It's your best friend.  Use it liberally.
*   **Next/Previous Buttons (Theoretical):**  They exist.  They might even work.  We're not making any promises.
*   **Repeat Modes (Experimental):**  Repeat one, repeat all, repeat off.  Choose your own adventure in audio looping.
*   **Shuffle (Philosophical):**  We contemplate the meaning of "shuffle" in a world where file loading order is already a chaotic mess.
*   **Drag and Drop (For the Brave):**  Feel free to drag and drop files.  We can't guarantee what will happen, but it'll probably be interesting.
*   **Menu Bar (Mostly Harmless):**  It has menus!  File, Edit, View, Window, Help.  They mostly contain things that might work someday.
*   **About Dialog (Existential):**  Tells you who to blame for this sonic abomination.
*   **Asynchronous Loading (Theoretical):** Supposedly loads files in the background. In practice, it might just be contemplating the meaning of life while your UI freezes.
* **Cross-Platform**: Works on Windows, Mac and Linux!
*   **Open Source (Unfortunately):**  The code is available for your perusal (and potential amusement/horror).

## Dependencies (A Motley Crew):

You'll need a bunch of stuff.  We're not entirely sure *why* we need all of it, but it seems important:

*   **Python 3.10 (or later, maybe):**  We think.  Honestly, we've lost track.
*   **PyQt6:**  For the GUI (because who needs a command-line audio player in this century?).
*   **pydub:**  For loading and manipulating audio (when it works).
*    **sounddevice:** Or pyaudio!
*   **aiofiles:** For asynchronous file I/O (because we like to live dangerously).
*   **numpy:** For... reasons.  Numbers, probably.
*   **qtawesome:** For fancy icons (because even a potentially ear-splitting application deserves a little style).
*   **FFmpeg:**  The Swiss Army Knife of audio/video processing.  Make sure it's installed and in your PATH.  (Seriously, this one is *actually* important.)
*   **Various other libraries**: See the installation instructions, though they're not guaranteed.

## Installation (Good Luck):

1.  **Clone the Repository:**
    ```bash
    git clone [your repository URL here]
    ```

2.  **Install Dependencies:**
    ```bash
    pip install PyQt6 pydub sounddevice soundfile numpy qtawesome aiofiles
    ```
    Or, if you're brave, try:
     ```bash
    pip install -r requirements.txt
    ```
    (You'll need to create a `requirements.txt` file with all the dependencies listed. Which you should do. Really.)

3. **Install FFmpeg:**

    *   **Windows:** Download a build from somewhere reputable (gyan.dev is a good start). Add the `bin` folder to your system's PATH.  Good luck.
    *   **macOS:** `brew install ffmpeg` (if you have Homebrew, which you should).
    *   **Linux:** Use your distribution's package manager (e.g., `apt install ffmpeg`, `yum install ffmpeg`, etc.).

4.  **Pray:**  Seriously, at this point, a little prayer might help.

5.  **Run the Script:**
    ```bash
    python your_script_name.py
    ```

## Usage (At Your Own Risk):

1.  Drag and drop files, folders, or .m3u playlists onto the window. Or use the "Load" button, or the menu options. If they work.
2.  Click the "Play" button (if you dare).
3.  Adjust the volume slider *very, very carefully*. We recommend starting at 0 and increasing it by *extremely* small increments.
4.  Use the mute button frequently.  It's your lifeline.
5.  The other buttons might do something.  Experiment at your own risk.

## Troubleshooting (You're Gonna Need This):

*   **"Unrecognized audio format" error:**  Probably means FFmpeg isn't installed correctly, or it's not in your PATH, or `pydub` is having a bad day.  Or maybe the file is just cursed.
*   **No sound:**  Check your system's audio output settings.  Make sure the correct output device is selected.  Make sure the volume isn't muted at the OS level.  Make sure you haven't accidentally muted the player itself.  Pray.
*   **Distorted/Garbled sound:**  This usually means there's a mismatch in the audio data format.  We're *supposed* to be handling this, but, well, see the warning at the top.
*   **Application freezes:**  The asynchronous loading might not be as asynchronous as we think.  Or maybe it's just taking a nap.
*   **It just crashes:**  ¯\\\_(ツ)\_/¯  Welcome to the world of audio programming.

## Contributing (Are You Sure?):

If you're brave (or foolish) enough to contribute to this project, feel free to submit pull requests.  But be warned: the code is a work in progress (to put it mildly).  We make no guarantees about its stability, sanity, or adherence to any known coding standards.

## License:**

This project is licensed under the [MIT License](LICENSE) - see the `LICENSE` file for details. (Basically, you can do whatever you want with it, but don't blame us if it breaks your computer, your ears, or your sanity.)

## Disclaimer:

This is a *highly* experimental project.  It is *not* intended for production use.  It is *likely* to contain bugs, glitches, and potentially ear-damaging volume issues.  Use it at your own risk.  We are not responsible for any damage to your hardware, software, hearing, or mental well-being.  You have been warned. Seriously.
