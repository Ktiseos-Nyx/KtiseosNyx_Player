import asyncio
import aiofiles
from pydub import AudioSegment
import sounddevice as sd
import soundfile as sf
import os
import sys
import random
import io   # For file handling
import logging
import numpy as np
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QLabel,
                             QHBoxLayout, QVBoxLayout, QSlider, QFileDialog,
                             QMessageBox, QMenuBar, QMenu)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QAction, QKeySequence
import qtawesome

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("player.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class KtiseosNyxPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KtiseosNyx Player")
        self.setMinimumSize(250, 100)

        self.playlist = []
        self.current_track_index = 0
        self.current_sound = None
        self.shuffled = False
        self.repeat_mode = "off"
        self.volume = 1.0
        self.previous_volume = 1.0  # Store previous volume for mute/unmute
        self.audio_cache = {}
        self.current_data = None
        self.current_sr = None
        self.current_frame = 0 #Keep track of current playback frame

        self.init_ui()
        self.create_menu_bar()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # --- Volume Controls (Slider and Mute Button) ---
        volume_layout = QHBoxLayout()
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(int(self.volume * 100))
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)

        self.mute_button = QPushButton()
        self.mute_button.setIcon(qtawesome.icon('mdi.volume-high'))  # Initial icon
        self.mute_button.setIconSize(QSize(24, 24))
        self.mute_button.clicked.connect(self.toggle_mute)
        self.mute_button.setToolTip("Mute/Unmute") # Add a tooltip
        volume_layout.addWidget(self.mute_button)

        main_layout.addLayout(volume_layout) # Add volume layout

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        self.prev_button = QPushButton()
        self.prev_button.setIcon(qtawesome.icon('mdi.skip-previous'))
        self.prev_button.setIconSize(QSize(24, 24))
        self.prev_button.clicked.connect(self.previous_track)
        button_layout.addWidget(self.prev_button)

        self.play_pause_button = QPushButton()
        self.play_pause_button.setIcon(qtawesome.icon('mdi.play'))
        self.play_pause_button.setIconSize(QSize(24, 24))
        self.play_pause_button.clicked.connect(self.play_pause)
        self.play_pause_button.setText("Play")
        button_layout.addWidget(self.play_pause_button)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(qtawesome.icon('mdi.stop'))
        self.stop_button.setIconSize(QSize(24, 24))
        self.stop_button.clicked.connect(self.stop)
        button_layout.addWidget(self.stop_button)

        self.next_button = QPushButton()
        self.next_button.setIcon(qtawesome.icon('mdi.skip-next'))
        self.next_button.setIconSize(QSize(24, 24))
        self.next_button.clicked.connect(self.next_track)
        button_layout.addWidget(self.next_button)

        self.load_button = QPushButton("Load")
        self.load_button.setIcon(qtawesome.icon('mdi.folder-open'))
        self.load_button.setIconSize(QSize(24,24))
        self.load_button.clicked.connect(self.load_files)
        button_layout.addWidget(self.load_button)
        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)

        self.status_label = QLabel("No file loaded")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        main_layout.addWidget(self.status_label)

        self.setAcceptDrops(True)

    def create_menu_bar(self):
        menu_bar = QMenuBar(self)

        # --- File Menu ---
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        # Open File(s)
        open_action = QAction(qtawesome.icon('mdi.file-music-outline'), "&Open Files...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.load_files)
        file_menu.addAction(open_action)

        # Open Folder
        open_folder_action = QAction(qtawesome.icon('mdi.folder-open'), "Open &Folder...", self)
        open_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_folder_action.triggered.connect(self.open_folder_dialog)
        file_menu.addAction(open_folder_action)

        # Load Playlist (M3U)
        load_playlist_action = QAction(qtawesome.icon('mdi.playlist-music-outline'), "&Load Playlist...", self)
        load_playlist_action.setShortcut(QKeySequence("Ctrl+L"))
        load_playlist_action.triggered.connect(self.load_m3u_dialog)
        file_menu.addAction(load_playlist_action)

        # Save Playlist (M3U)
        save_playlist_action = QAction(qtawesome.icon('mdi.content-save'), "&Save Playlist...", self)
        save_playlist_action.setShortcut(QKeySequence.StandardKey.Save)
        save_playlist_action.triggered.connect(self.save_playlist_dialog)
        file_menu.addAction(save_playlist_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction(qtawesome.icon('mdi.exit-to-app'), "E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(QApplication.instance().quit)
        file_menu.addAction(exit_action)

        # --- Edit Menu ---
        edit_menu = QMenu("&Edit", self)
        menu_bar.addMenu(edit_menu)

        # Clear Playlist
        clear_playlist_action = QAction(qtawesome.icon('mdi.playlist-remove'), "Clear Playlist", self)
        clear_playlist_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        clear_playlist_action.triggered.connect(self.clear_playlist)
        edit_menu.addAction(clear_playlist_action)

        # --- View Menu ---
        view_menu = QMenu("&View", self)
        menu_bar.addMenu(view_menu)
        #Repeat mode submenu
        repeat_menu = QMenu("&Repeat",self)
        repeat_off = QAction("Off",self)
        repeat_off.triggered.connect(lambda: self.set_repeat_mode("off"))
        repeat_menu.addAction(repeat_off)

        repeat_one = QAction("Repeat One", self)
        repeat_one.triggered.connect(lambda: self.set_repeat_mode("one"))
        repeat_menu.addAction(repeat_one)

        repeat_all = QAction("Repeat All", self)
        repeat_all.triggered.connect(lambda: self.set_repeat_mode("all"))
        repeat_menu.addAction(repeat_all)

        view_menu.addMenu(repeat_menu)

        # Shuffle
        shuffle_action = QAction(qtawesome.icon('mdi.shuffle-variant'), "&Shuffle", self, checkable=True)
        shuffle_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        shuffle_action.triggered.connect(self.toggle_shuffle)
        view_menu.addAction(shuffle_action)


        # --- Window Menu ---
        window_menu = QMenu("&Window", self)
        menu_bar.addMenu(window_menu)

        # --- Help Menu ---
        help_menu = QMenu("&Help", self)
        menu_bar.addMenu(help_menu)

        # About
        about_action = QAction(qtawesome.icon('mdi.information-outline'), "&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        self.layout().setMenuBar(menu_bar)


    def set_repeat_mode(self, mode):
        self.repeat_mode = mode
        logging.info(f"Repeat mode set to: {mode}")

    def toggle_shuffle(self, checked):
        self.shuffled = checked
        if self.shuffled:
            if self.playlist:
                random.shuffle(self.playlist)
                self.current_track_index = 0
                if self.current_sound:
                    self.stop()
                self.play_current_track()
                logging.info("Playlist shuffled.")
        else:
            logging.info("Shuffle is not integrated with playlist/folder loading.")
            QMessageBox.information(self,"Shuffle off", "Shuffle is not compatible with playlist loading. Load a single folder to reshuffle.")


    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "About KtiseosNyx Player",
            "A simple audio player built with PyQt6, pydub, and sounddevice.\n"
            "By [Your Name/Your Organization]"
        )

    def clear_playlist(self):
        if self.current_sound:
            self.stop()
        self.playlist = []
        self.current_track_index = 0
        self.audio_cache = {}
        self.update_status_label()
        logging.info("Playlist cleared")

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Audio Folder")
        if folder_path:
            asyncio.run(self.add_folder_to_playlist_async(folder_path))

    def load_m3u_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select M3U Playlist", "", "M3U Files (*.m3u)")
        if file_path:
             asyncio.run(self.add_files_async([file_path]))

    def save_playlist_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Playlist", "", "M3U Files (*.m3u)")
        if file_path:
            if not file_path.lower().endswith(".m3u"):
                file_path += ".m3u"
            self.save_playlist_to_file(file_path)

    def save_playlist_to_file(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for track in self.playlist:
                    f.write(track + '\n')
            logging.info(f"Playlist saved to {file_path}")
        except Exception as e:
            logging.exception(f"Error saving playlist to {file_path}: {e}")
            QMessageBox.critical(self, "Error", f"Error saving playlist: {e}")


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
        asyncio.run(self.add_files_async(file_paths))

    async def add_files_async(self, file_paths):
        logging.debug(f"add_files_async called with: {file_paths}")
        tasks = []
        for path in file_paths:
            if path.lower().endswith(".m3u"):
                tasks.append(self.load_playlist_from_file_async(path))
            elif os.path.isdir(path):
                tasks.append(self.add_folder_to_playlist_async(path))
            else:
                tasks.append(self.add_single_file_async(path))

        await asyncio.gather(*tasks)
        if self.playlist and self.current_sound is None:
                self.play_current_track()

    async def add_single_file_async(self, file_path):
        logging.debug(f"add_single_file_async called with: {file_path}")
        if file_path not in self.playlist:
            try:
                if file_path not in self.audio_cache:
                    logging.info(f"Loading {file_path} from disk")
                    audio = await load_audio_file_async(file_path)
                    self.audio_cache[file_path] = audio
                else:
                    logging.info(f"Loading {file_path} from cache")
                self.playlist.append(file_path)
                self.update_status_label()
            except Exception as e:
                logging.exception(f"Error loading {file_path}: {e}")
                QMessageBox.critical(self, "Error", f"Error loading {file_path}: {e}")

    async def add_folder_to_playlist_async(self, folder_path):
        logging.debug(f"add_folder_to_playlist_async called with: {folder_path}")
        tasks = []
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac')):
                file_path = os.path.join(folder_path, filename)
                logging.debug(f"  Found audio file in folder: {file_path}")
                tasks.append(self.add_single_file_async(file_path))
        await asyncio.gather(*tasks)

    async def load_playlist_from_file_async(self, file_path):
        logging.debug(f"load_playlist_from_file_async called with: {file_path}")
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                async for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and os.path.exists(line):
                        logging.debug(f"  Found audio file in playlist: {line}")
                        await self.add_single_file_async(line)
        except Exception as e:
            logging.exception(f"Error loading playlist: {e}")
            QMessageBox.critical(self, "Error", f"Error loading playlist: {e}")

    async def load_files_async(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files or Playlists",
            "",
            "Audio Files (*.mp3 *.wav *.flac *.ogg *.m4a *.aac);;Playlist Files (*.m3u);;All Files (*)"
        )
        if file_paths:
            await self.add_files_async(file_paths)


    def load_files(self):
        asyncio.run(self.load_files_async())


    def play_current_track(self):
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound.close()
            self.current_sound = None

        if self.playlist:
            if self.current_track_index >= len(self.playlist) or self.current_track_index < 0:
                self.current_track_index = 0
            try:
                logging.debug(f"Trying to play from cache: {self.playlist[self.current_track_index]}")
                audio = self.audio_cache[self.playlist[self.current_track_index]]
                self.current_sound, self.current_data, self.current_sr = play_audio(self, audio, self.volume)
                self.update_status_label()
                self.play_pause_button.setIcon(qtawesome.icon('mdi.pause'))
                self.play_pause_button.setText("Pause")
                if self.current_sound:
                    self.current_frame = 0 # Reset playback position
                    QApplication.processEvents()

            except KeyError:
                logging.error(f"Cached audio not found for: {self.playlist[self.current_track_index]}")
                QMessageBox.critical(self,"Error", "Cached audio not found. Try reloading.")
                self.current_sound = None
                self.update_status_label()
            except Exception as e:
                logging.exception(f"Error during playback: {e}")
                QMessageBox.critical(self, "Error", f"Error playing file: {e}")
                self.current_sound = None
                self.update_status_label()
                self.play_pause_button.setIcon(qtawesome.icon('mdi.play'))
                self.play_pause_button.setText("Play")

    def play_pause(self):
        if self.current_sound:
            if self.current_sound.active:
                self.current_sound.stop()
                self.play_pause_button.setIcon(qtawesome.icon('mdi.play'))
                self.play_pause_button.setText("Play")
            else:
                #Crucial bit: Recreate the stream
                self.current_sound = sd.OutputStream(
                    samplerate=self.current_sr,
                    channels=self.current_data.shape[1],
                    callback=self.audio_callback,
                    blocksize=1024,
                )
                self.current_sound.start()

                self.play_pause_button.setIcon(qtawesome.icon('mdi.pause'))
                self.play_pause_button.setText("Pause")
        elif self.playlist:
            self.play_current_track()

    def stop(self):
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound.close()
            self.current_sound = None
            self.current_data = None
            self.current_sr = None
            self.current_frame = 0
            self.update_status_label()
            self.play_pause_button.setIcon(qtawesome.icon('mdi.play'))
            self.play_pause_button.setText("Play")


    def next_track(self):
        if self.playlist:
            if self.repeat_mode != "one":
                self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
            self.play_current_track()

    def previous_track(self):
        if self.playlist:
            if self.repeat_mode != "one":
                self.current_track_index = (self.current_track_index - 1) % len(self.playlist)
            self.play_current_track()

    def set_volume(self, val):
        # Only store the volume value.  Scaling is done in play_audio.
        self.volume = float(val) / 100.0
        logging.debug(f"Volume set to: {self.volume}")

    def toggle_mute(self):
        if self.current_sound:
            if self.volume > 0.0:
                # Mute: Store current volume and set to 0
                self.previous_volume = self.volume
                self.volume = 0.0
                self.volume_slider.setValue(0)  # Update the slider visually
                self.mute_button.setIcon(qtawesome.icon('mdi.volume-off'))
                logging.debug("Muted")
            else:
                # Unmute: Restore previous volume
                self.volume = self.previous_volume
                self.volume_slider.setValue(int(self.volume * 100))  # Update the slider
                self.mute_button.setIcon(qtawesome.icon('mdi.volume-high'))
                logging.debug("Unmuted")
            if self.current_sound.active: #Refresh if playing.
                self.play_current_track()


    def update_status_label(self):
        if self.current_sound and self.playlist:
            filename = os.path.basename(self.playlist[self.current_track_index])
            self.status_label.setText(f"Now Playing: {filename}")
        elif not self.playlist:
            self.status_label.setText("No files in playlist")
        else:
            self.status_label.setText("Stopped")


    def check_playback_status(self):
        if self.current_sound:
             if not self.current_sound.active:
                if self.repeat_mode == "one":
                    self.play_current_track()
                elif self.repeat_mode == "all":
                    self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
                    self.play_current_track()
                elif self.repeat_mode == 'off':
                    self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
                    if self.current_track_index != 0:
                        self.play_current_track()
                    else:
                        self.stop()

                elif not self.playlist:
                    self.current_sound = None
        #Removed recursive call

    def audio_callback(self, outdata, frames, time, status):
        if status:
            logging.warning(f"Sounddevice status: {status}")

        chunksize = min(len(self.current_data) - self.current_frame, frames)
        outdata[:chunksize] = self.current_data[self.current_frame:self.current_frame + chunksize]

        if chunksize < frames:
            outdata[chunksize:] = 0
            self.stop()
            raise sd.CallbackStop()

        self.current_frame += chunksize
        #NO VOLUME SCALING HERE

async def load_audio_file_async(file_path):
    logging.debug(f"load_audio_file_async: Loading {file_path}")
    try:
        async with aiofiles.open(file_path, 'rb') as f:
            file_data = await f.read()
            logging.debug(f"load_audio_file_async: Read file data, size: {len(file_data)}")
            audio = AudioSegment.from_file(io.BytesIO(file_data), format=file_path.split('.')[-1])
            logging.debug(f"load_audio_file_async: AudioSegment created successfully")

            # --- CRITICAL FIX: Convert to 16-bit PCM here ---
            audio = audio.set_sample_width(2)
            return audio

    except Exception as e:
        logging.exception(f"load_audio_file_async: Exception: {e}")
        raise

def play_audio(self, audio_segment, volume=1.0):
    try:
        sr = audio_segment.frame_rate
        samples = audio_segment.get_array_of_samples()
        samples = np.array(samples).astype(np.int16)
        channels = audio_segment.channels
        data = samples.reshape(-1, channels)

        # --- Apply volume scaling to the NumPy array *before* creating the stream ---
        data = (data * self.volume).astype(np.int16)  # Apply volume and keep int16

        stream = sd.OutputStream(
            samplerate=sr,
            channels=channels,
            callback=self.audio_callback,
            blocksize=1024,
            )
        stream.start()

        return stream, data, sr

    except Exception as e:
        logging.exception(f"Error during playback setup: {e}")
        return None, None, None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = KtiseosNyxPlayer()
    player.show()
    sys.exit(app.exec())
