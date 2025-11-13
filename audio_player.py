import random
import wave


import kivy
import os
from appdata import AppDataPaths

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader

app_paths = AppDataPaths("Birdsong")
app_paths.setup()
print(app_paths.app_data_path)

library_path = app_paths.app_data_path + "\\MusicLibrary\\"
print(library_path)

library:list[str] = []
print(library)




class MusicPlayer(BoxLayout):

	def update_buttons(self, button):
		self.play_button.text = "Playing" if not self.playing else "Stop"
		self.pause_button.text = "Pause" if not self.paused else "Resume"
		self.pause_button.disabled = self.playing

	def play_song(self, button):
		if self.playing:
			self.loaded_sound.stop()
			self.playing = False
			self.paused = False
			self.play_button.text = "Play"
			return

		if len(library) == 0:
			print("Library is empty!")
			return
		self.saved_seek_value = 0
		self.soundloader = SoundLoader()
		self.loaded_sound.stop()
		self.loaded_sound = self.soundloader.load(self.selected_song_path)
		if self.soundloader:
			self.playing = True
			self.paused = False
			print("Sound found at %s" % self.loaded_sound.source)
			print("Sound is %.3f seconds" % self.loaded_sound.length)
			self.loaded_sound.play()

	def pause_song(self, button):
		if self.soundloader:
			if self.loaded_sound.state == "play":
				self.paused = True
				self.saved_seek_value = self.loaded_sound.get_pos()
				self.loaded_sound.stop()
			else:
				self.paused = False
				self.loaded_sound.play()
				self.loaded_sound.seek(self.saved_seek_value)

	def __init__(self):
		self.selected_song_path = library[0] if len(library) > 0 else ""
		super(MusicPlayer, self).__init__()
		self.orientation = "vertical"
		self.song_info = SongInfoDisplay()
		self.add_widget(self.song_info)
		self.playing = False
		self.paused = False
		self.saved_seek_value:int = 0
		self.soundloader = SoundLoader()
		self.loaded_sound:kivy.core.audio.Sound = kivy.core.audio.Sound()
		self.button_container = BoxLayout(orientation = "horizontal")
		self.play_button:Button = Button(text='Play')
		self.play_button.bind(on_release=self.play_song)
		self.play_button.bind(on_release=self.update_buttons)
		self.pause_button:Button = Button(text='Pause')
		self.pause_button.bind(on_release=self.pause_song)
		self.play_button.bind(on_release=self.update_buttons)
		self.button_container.add_widget(self.play_button)
		self.button_container.add_widget(self.pause_button)
		self.add_widget(self.button_container)

class SongInfoDisplay(BoxLayout):
	def __init__(self):
		super(SongInfoDisplay, self).__init__()
		self.orientation = "vertical"
		self.title_label = Label(text="Unknown Song")
		self.artist_label = Label(text="Unknown Artist")
		self.album_label = Label(text="Unknown Album")
		self.add_widget(self.title_label)
		self.add_widget(self.artist_label)
		self.add_widget(self.album_label)

class LibraryScrollView(ScrollView):
	def __init__(self):
		super(LibraryScrollView, self).__init__()
		layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
		layout.bind(minimum_height=layout.setter("height"))

		for song in library:
			btn = Button(text=song.removeprefix(library_path).removesuffix(".wav"), size_hint_y=None, height=40)
			btn.path=song
			btn.bind(on_release=self.button_select)
			layout.add_widget(btn)

		self.add_widget(layout)
	def button_select(self, button):
		print(button.path)
		music_player.selected_song_path = button.path

music_player:MusicPlayer = MusicPlayer()
library_scroll_view:LibraryScrollView = LibraryScrollView()
class BirdsongMain(App):
	global selected_song_path
	def build(self):
		library_scroll_view = LibraryScrollView()
		self.base_layout = BoxLayout(orientation = 'horizontal')
		self.base_layout.add_widget(library_scroll_view)
		self.base_layout.add_widget(music_player)
		return self.base_layout
	def get_song_library(self):
		if not os.path.exists(library_path):
			print("Music Library does not exist!\nCreating Music Library.")
			os.mkdir(library_path)
		for wav in os.listdir(library_path):
			if wav.endswith(".wav"):
				print(os.path.join(library_path,wav))
				library.append(os.path.join(library_path,wav))
		music_player.selected_song_path = library[0] if len(library) > 0 else ""

if __name__ == '__main__':
	instance = BirdsongMain()
	instance.get_song_library()
	instance.run()