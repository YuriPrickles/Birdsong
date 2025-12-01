


import kivy
import os

from appdata import AppDataPaths

from kivy.app import App
from kivy.uix.bubble import Bubble, BubbleContent, BubbleButton
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem, TabbedPanelHeader
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.uix.checkbox import CheckBox
from kivy.clock import Clock
import uyts
import random
import yt_dlp
import sys
import os

from kivy.uix.widget import Widget


def log(message):
    sys.stderr.write("%s\n" % (message,))
    sys.stderr.flush()

class Logger:
    debug = log
    warning = log
    error = log
    info = log
    critical = log

print(sys.executable)

app_paths = AppDataPaths("Birdsong")
app_paths.setup()
print(app_paths.app_data_path)

library_path = app_paths.app_data_path + "\\MusicLibrary\\"
print(library_path)

library:list[str] = []
playlists:list[str] = []
print(library)

search_term = ""

selected_song_path:str = ""

class BabyInt:
	def __init__(self, number):
		self.integer = number
	def set_number(self, value):
		self.integer = value

audio_queue:list[str] = []
queue_index:BabyInt = BabyInt(-1)



class MusicPlayer(BoxLayout):

	def update_buttons(self, button):
		self.play_button.text = "Stop" if self.playing else "Play"
		self.pause_button.text = "Pause" if not self.paused else "Resume"
		self.pause_button.disabled = not self.loaded_sound

	def play_song(self, button):
		global selected_song_path
		if self.playing:
			self.loaded_sound.stop()
			self.playing = False
			self.paused = False
			self.update_buttons(None)
			return

		if len(library) == 0:
			print("Library is empty!")
			return
		self.saved_seek_value = 0
		self.soundloader = SoundLoader()
		self.loaded_sound.stop()
		queue_index.set_number(0 if queue_index.integer <= -1 else queue_index.integer)
		selected_song_path = audio_queue[queue_index.integer] if len(audio_queue) > 0 else (selected_song_path if selected_song_path != "" else library[0])
		self.loaded_sound = self.soundloader.load(selected_song_path)
		if self.soundloader:
			self.playing = True
			self.paused = False
			print("Sound found at %s" % self.loaded_sound.source)
			print("Sound is %.3f seconds" % self.loaded_sound.length)
			if len(audio_queue) == 0:
				audio_queue.append(selected_song_path)
			self.loaded_sound.play()
			print(audio_queue)
			print(queue_index.integer)
			self.update_buttons(None)

	def pause_song(self, button):
		if self.soundloader:
			if self.loaded_sound.state == "play":
				self.saved_seek_value = self.loaded_sound.get_pos()
				self.paused = True
				print(self.saved_seek_value)
				self.loaded_sound.stop()
			else:
				self.paused = False
				self.loaded_sound.play()
				self.loaded_sound.seek(self.saved_seek_value)
	def play_prev(self, button):
		global selected_song_path
		if self.soundloader:
			if queue_index.integer <= 0:
				return
			queue_index.integer -= 1
			self.loaded_sound.stop()
			selected_song_path = audio_queue[queue_index.integer]
			self.loaded_sound = self.soundloader.load(selected_song_path)
			self.playing = True
			self.paused = False
			self.loaded_sound.play()
			self.update_buttons(None)
	def play_next(self, button):
		global selected_song_path
		if self.soundloader:
			if queue_index.integer >= len(audio_queue) - 1:
				return
			queue_index.integer += 1
			self.loaded_sound.stop()
			selected_song_path = audio_queue[queue_index.integer]
			self.loaded_sound = self.soundloader.load(selected_song_path)
			self.playing = True
			self.paused = False
			self.loaded_sound.play()
			self.update_buttons(None)
	def __init__(self):
		global selected_song_path
		selected_song_path = library[0] if len(library) > 0 else ""
		super(MusicPlayer, self).__init__()
		self.orientation = "vertical"
		self.song_info = SongInfoDisplay()
		self.add_widget(self.song_info)
		self.playing = False
		self.paused = False
		self.saved_seek_value:float = 0
		self.soundloader = SoundLoader()
		self.loaded_sound:kivy.core.audio.Sound = kivy.core.audio.Sound()
		self.button_container = BoxLayout(orientation = "horizontal")
		self.play_button:Button = Button(text='Play')
		self.pause_button:Button = Button(text='Pause')
		self.playprev:Button = Button(text='Play Previous')
		self.playnext:Button = Button(text='Play Next')

		self.play_button.bind(on_release=self.play_song)
		self.pause_button.bind(on_release=self.pause_song)
		self.playprev.bind(on_release=self.play_prev)
		self.playnext.bind(on_release=self.play_next)


		self.play_button.bind(on_release=self.update_buttons)
		self.pause_button.bind(on_release=self.update_buttons)

		self.button_container.add_widget(self.playprev)
		self.button_container.add_widget(self.play_button)
		self.button_container.add_widget(self.pause_button)
		self.button_container.add_widget(self.playnext)

		self.add_widget(self.button_container)
		self.update_buttons(None)
		self.play_button.text = "Play"
		self.pause_button.disabled = True

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
		self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None,width=400,pos_hint=(0,0))
		self.layout.bind(minimum_height=self.layout.setter("height"))
		self.add_widget(self.layout)
	def update_library(self):
		self.layout.clear_widgets()
		for song in library:
			item_container = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)
			item_container.bind(minimum_height=self.layout.setter("height"))
			artist_label:Label = Label(text="Unknown Artist",shorten_from="right")
			album_label:Label = Label(text="Unknown Album",shorten_from="right")
			btn = Button(text=song.removeprefix(library_path).removesuffix(".wav"), size_hint_y=None, height=40, width=400,shorten_from="right", size_hint=(2.0, 1.0), halign="left", valign="middle")
			btn.bind(size=btn.setter('text_size'))
			btn.path=song
			btn.padding = (20,0)
			btn.halign = "left"
			btn.valign = "middle"
			btn.bind(on_release=self.button_select)
			addqueue = Button(text="+",width=40,height=40,size_hint_x=0.25)
			addqueue.bind(on_release=self.add_to_queue)
			addqueue.path = song
			item_container.add_widget(btn)
			item_container.add_widget(artist_label)
			item_container.add_widget(album_label)
			item_container.add_widget(addqueue)
			self.layout.add_widget(item_container)
	def add_to_queue(self,button):
		audio_queue.append(button.path)
		print(audio_queue)
		print(queue_index.integer)
	def button_select(self, button):
		print(button.path)
		global selected_song_path
		selected_song_path = button.path

class ContextMenu(Bubble):
	def __init__(self):
		super(ContextMenu,self).__init__()
		bc:BubbleContent = BubbleContent()
		add_to_playlist:BubbleButton(text="A")

class PlaylistMenu(ScrollView):
	def __init__(self):
		super(PlaylistMenu, self).__init__()
		self.layout = GridLayout(cols=1, spacing=10, size_hint_y=1,width=400,pos_hint=(0,0))
		self.layout.bind(minimum_height=self.layout.setter("height"))
		self.popup = None
		self.index = 0
		self.addbutton = Button(text="+ Add new playlist...", size_hint_y=None, height=40, width=400,shorten_from="right", size_hint=(2.0, 1.0), halign="left", valign="middle")
		self.box = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)
		self.box.bind(minimum_height=self.layout.setter("height"))
		self.addbutton.bind(size=self.addbutton.setter('text_size'))
		self.addbutton.bind(on_release=self.add_playlist)
		self.box.add_widget(self.addbutton)
		self.add_widget(self.layout)
		self.to_add: list[str] = []
		self.selected_playlist = None
	def update_playlists(self):
		self.layout.clear_widgets()
		for pl in playlists:
			item_container = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)
			item_container.bind(minimum_height=self.layout.setter("height"))
			btn = Button(text=pl.removeprefix(library_path).removesuffix(".txt"), size_hint_y=None, height=40, width=400,shorten_from="right", size_hint=(2.0, 1.0), halign="left", valign="middle")
			btn.bind(size=btn.setter('text_size'))
			btn.path=pl
			btn.padding = (20,0)
			btn.halign = "left"
			btn.valign = "middle"
			btn.bind(on_release=self.button_select)
			remove = Button(text="X", size_hint_y=None, height=40, width=400, size_hint=(0.1, 1.0), halign="center", valign="middle")
			remove.bind(size=remove.setter('text_size'))
			remove.padding = (8,0)
			remove.path = pl
			remove.bind(on_release=self.remove_playlist)
			item_container.add_widget(btn)
			item_container.add_widget(remove)
			self.layout.add_widget(item_container)
		self.layout.add_widget(self.box)
	def remove_playlist(self,button):
		if os.path.exists(button.path):
			os.remove(str(button.path))
	def button_select(self, button):
		print(button.path)
		popup_layout = ScrollView()
		box = BoxLayout(orientation="vertical")
		grid = GridLayout(cols=1, spacing=10, size_hint_y=1,width=400,pos_hint=(0,0))
		play_button = Button(text="Play",size_hint_y=0.2)
		play_shuffle = Button(text="Shuffle Play",size_hint_y=0.2)
		add_to_q = Button(text="Add to\nQueue",size_hint_y=0.2)
		add_to_q_shuffle = Button(text="Shuffle\nto Queue",size_hint_y=0.2)
		closeButton = Button(text="Close",size_hint_y=0.2)
		playlist_file =open(button.path,"r")
		songlist_data:list[str] = eval(playlist_file.readline())
		self.selected_playlist = button.path
		self.index = 0
		for song in songlist_data:
			playlist_item_container = BoxLayout(orientation="horizontal")
			song_name:Label = Label(text=(song.removeprefix(library_path)).removesuffix(".wav"), size_hint=(1.0, 1.0), halign="left", valign="middle")
			song_name.bind(size=song_name.setter('text_size'))
			move_up = Button(text="^", size_hint_y=None, height=40, width=400, size_hint=(0.04, 1.0), halign="center", valign="middle")
			move_up.bind(size=move_up.setter('text_size'))
			move_up.padding = (8,0)
			move_up.index = self.index
			move_down = Button(text="V", size_hint_y=None, height=40, width=400, size_hint=(0.04, 1.0), halign="center", valign="middle")
			move_down.bind(size=move_down.setter('text_size'))
			move_down.padding = (8,0)
			move_down.index = self.index
			remove = Button(text="X", size_hint_y=None, height=40, width=400, size_hint=(0.04, 1.0), halign="center", valign="middle")
			remove.bind(size=remove.setter('text_size'))
			remove.padding = (8,0)
			remove.index = self.index

			move_up.popup = button
			move_down.popup = button
			remove.popup = button
			move_up.bind(on_release=self.move_up)
			move_down.bind(on_release=self.move_down)
			remove.bind(on_release=self.remove_song)
			playlist_item_container.add_widget(song_name)
			playlist_item_container.add_widget(move_up)
			playlist_item_container.add_widget(move_down)
			playlist_item_container.add_widget(remove)
			grid.add_widget(playlist_item_container)
			self.index += 1
		popup_layout.add_widget(grid)
		box.add_widget(popup_layout)
		button_box = BoxLayout(orientation="horizontal")
		button_box.add_widget(play_button)
		button_box.add_widget(play_shuffle)
		button_box.add_widget(add_to_q)
		button_box.add_widget(add_to_q_shuffle)
		button_box.add_widget(closeButton)
		box.add_widget(button_box)

		self.popup = Popup(
			title='Contents of playlist', content=box,
			auto_dismiss=False, size_hint=(None, None),
			size=(800, 600)
		)
		self.popup.open()
		play_button.songlist = songlist_data.copy()
		play_shuffle.songlist = songlist_data.copy()
		add_to_q.songlist = songlist_data.copy()
		add_to_q_shuffle.songlist = songlist_data.copy()
		random.shuffle(play_shuffle.songlist)
		random.shuffle(add_to_q_shuffle.songlist)
		closeButton.bind(on_release=self.on_close)
		play_button.bind(on_release=self.play_playlist)
		play_shuffle.bind(on_release=self.play_playlist)
		add_to_q.bind(on_release=self.queue_playlist)
		add_to_q_shuffle.bind(on_release=self.queue_playlist)

	def play_playlist(self, button):
		global selected_song_path
		audio_queue.clear()
		queue_index.integer = -1
		for song in button.songlist:
			audio_queue.append(song)
		music_player.loaded_sound.stop()
		music_player.playing = False
		music_player.paused = False
		music_player.update_buttons(None)
		music_player.play_song(button)
		selected_song_path = audio_queue[0]
		self.popup.dismiss()
		self.popup = None
	def queue_playlist(self, button):
		for song in button.songlist:
			audio_queue.append(song)
		self.popup.dismiss()
		self.popup = None
	def add_playlist(self, button):
		popup_layout = ScrollView()
		box = BoxLayout(orientation="vertical")
		grid = GridLayout(cols=1, spacing=10, size_hint_y=None, width=800)
		grid.bind(minimum_height=grid.setter("height"))
		button_container = BoxLayout(orientation="horizontal",size_hint_y=None)
		open_button = Button(text="OK")
		close_button = Button(text="CANCEL")
		text_input = TextInput(hint_text="Enter playlist name")
		text_input.multiline = False
		text_input.size_hint_y = None
		open_button.widget_corpse:TextInput = text_input
		for song in library:
			checkbox = CheckBox(width=40,size_hint_x=0.1)
			checkbox.metadata = song
			checkbox.bind(active=self.on_checkbox_active)
			label = Label(text=song.removeprefix(library_path).removesuffix(".wav"), halign="left", valign="middle", height= "40")
			label.bind(size=label.setter('text_size'))
			songselect = BoxLayout(orientation="horizontal", size_hint_y=None, width=800,height=20)
			songselect.bind(minimum_height=songselect.setter("height"))
			songselect.add_widget(checkbox)
			songselect.add_widget(label)
			grid.add_widget(songselect)
		box.add_widget(text_input)
		popup_layout.add_widget(grid)
		box.add_widget(popup_layout)
		button_container.add_widget(open_button)
		button_container.add_widget(close_button)
		box.add_widget(button_container)
		self.popup = Popup(
			title='Contents of playlist', content=box,
			auto_dismiss=False, size_hint=(None, None),
			size=(800, 600)
		)
		self.popup.open()
		open_button.bind(on_release=self.on_accept)
		close_button.bind(on_release=self.on_close)
	def on_checkbox_active(self, checkbox, value):
		print("bing")
		if value:
			self.to_add.append(checkbox.metadata)
			print(checkbox.metadata)
		else:
			self.to_add.remove(checkbox.metadata)
	def on_accept(self, button):
		file = open(library_path + button.widget_corpse.text + ".txt", 'w')
		file.write(str(self.to_add).replace("\\", "\\"))
		file.close()
		self.popup.dismiss()
		self.popup = None
	def on_close(self, event):
		self.popup.dismiss()
		self.popup = None

	def move_up(self, button):
		temp_playlist_arr = eval(open(self.selected_playlist,"r").readline())
		if not (button.index < 0 or len(temp_playlist_arr) == 1):
			temp = temp_playlist_arr[button.index]
			temp_playlist_arr[button.index] = temp_playlist_arr[button.index - 1]
			temp_playlist_arr[button.index - 1] = temp
			file = open(self.selected_playlist,"w")
			file.truncate(0)
			file.write(str(temp_playlist_arr).replace("\\", "\\"))
			file.close()
			self.popup.dismiss()
			self.popup = None
			self.button_select(button.popup)

	def move_down(self, button):
		temp_playlist_arr = eval(open(self.selected_playlist,"r").readline())
		if not (button.index >= len(temp_playlist_arr) - 1 or len(temp_playlist_arr) == 1):
			temp = temp_playlist_arr[button.index + 1]
			temp_playlist_arr[button.index + 1] = temp_playlist_arr[button.index]
			temp_playlist_arr[button.index] = temp
			file = open(self.selected_playlist,"w")
			file.truncate(0)
			file.write(str(temp_playlist_arr).replace("\\", "\\"))
			file.close()
			self.popup.dismiss()
			self.popup = None
			self.button_select(button.popup)

	def remove_song(self, button):
		temp_playlist_arr = eval(open(self.selected_playlist,"r").readline())
		temp_playlist_arr.pop(button.index)
		file = open(self.selected_playlist,"w")
		file.truncate(0)
		file.write(str(temp_playlist_arr).replace("\\", "\\"))
		file.close()
		self.popup.dismiss()
		self.popup = None
		self.button_select(button.popup)

class ImporterMenu(BoxLayout):
	def __init__(self):
		super(ImporterMenu, self).__init__()
		self.orientation = "vertical"
		self.nestedbox = BoxLayout(orientation="horizontal")
		self.search_box = TextInput(hint_text="Search from YouTube...",multiline=False)
		self.start_search = Button(text="Search!", size_hint_x=0.2)
		self.search_menu:SearchMenu = SearchMenu()
		self.start_search.bind(on_release=self.call_search)
		self.nestedbox.add_widget(self.search_box)
		self.nestedbox.add_widget(self.start_search)
		self.nestedbox.size_hint_y = 0.1
		self.add_widget(self.nestedbox)
		self.add_widget(self.search_menu)
	def call_search(self, button):
		self.search_menu.search_by_keyword(self.search_box.text)

class SearchMenu(ScrollView):
	def __init__(self):
		super(SearchMenu, self).__init__()
		self.gridlayout=GridLayout(cols=1,spacing=10,size_hint_y=None)
		self.gridlayout.bind(minimum_height=self.gridlayout.setter("height"))
		self.add_widget(self.gridlayout)
	def search_by_keyword(self, q):

		self.gridlayout.clear_widgets()
		print(q)
		search = uyts.Search(q,minResults=3)
		for res in search.results:
			print(res.resultType)
			if res.resultType == "video":
				button = Button(text="Download",size_hint_x=None)
				button.link = res.id
				button.type = res.resultType
				author_label:Label = Label(size_hint_x=0.3, height=40, text="[%s]" % res.author, size_hint_y=1, shorten = True, shorten_from ="right")
				author_label.bind(size=author_label.setter('text_size'))
				dur_label:Label = Label(size_hint_x=0.1, height=40, text="(%s)" % res.duration, size_hint_y=1, shorten = True, shorten_from ="right")
				dur_label.bind(size=dur_label.setter('text_size'))
				title_label:Label = Label(size_hint_x=0.6, height=40, text="%s" % res.title, size_hint_y=1, shorten = True, shorten_from ="right")
				title_label.bind(size=title_label.setter('text_size'))
				button.bind(on_release=self.download_video)
				grid = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
				grid.add_widget(button)
				grid.add_widget(author_label)
				grid.add_widget(dur_label)
				grid.add_widget(title_label)
				self.gridlayout.add_widget(grid)
			if res.resultType == "playlist":
				button = Button(text="Download",size_hint_x=None)
				button.link = res.id
				button.type = res.resultType
				author_label:Label = Label(size_hint_x=0.3, height=40, text="[%s]" % res.author, size_hint_y=1, shorten = True, shorten_from ="right")
				author_label.bind(size=author_label.setter('text_size'))
				dur_label:Label = Label(size_hint_x=0.1, height=40, text="(%s)" % res.length, size_hint_y=1, shorten = True, shorten_from ="right")
				dur_label.bind(size=dur_label.setter('text_size'))
				title_label:Label = Label(size_hint_x=0.6, height=40, text="%s" % res.title, size_hint_y=1, shorten = True, shorten_from ="right")
				title_label.bind(size=title_label.setter('text_size'))
				button.bind(on_release=self.download_video)
				grid = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
				grid.add_widget(button)
				grid.add_widget(author_label)
				grid.add_widget(dur_label)
				grid.add_widget(title_label)
				self.gridlayout.add_widget(grid)
	def download_video(self, button):
		url = ['https://www.youtube.com/watch?v=%s' % button.link]
		if button.type == "video":
			url = ['https://www.youtube.com/watch?v=%s' % button.link]
		if button.type == "playlist":
			url = ['https://www.youtube.com/playlist?list=%s' % button.link]

		ydl_opts = {
			'format': 'wav/bestaudio/best',
		    'postprocessors': [{  # Extract audio using ffmpeg
		        'key': 'FFmpegExtractAudio',
		        'preferredcodec': 'wav',
		    }],
			'keepvideo': False,
			"logger": Logger,
			"ffmpeg_location": "ffmpeg-6.0-essentials_build/bin"
		}
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			ydl.download(url)

class SongQueue(BoxLayout):
	def __init__(self):
		super(SongQueue, self).__init__(orientation="vertical")
		self.currently_playing = Label(text="Currently Playing: Nothing", halign="left", valign="middle", height= "40",size_hint_y=0.1)
		self.currently_playing.bind(size=self.currently_playing.setter('text_size'))
		scroll = ScrollView()
		self.song_grid_layout=GridLayout(cols=1,spacing=10,size_hint_y=None)
		self.song_grid_layout.bind(minimum_height=self.song_grid_layout.setter("height"))
		scroll.add_widget(self.song_grid_layout)
		self.add_widget(self.currently_playing)
		self.add_widget(scroll)
		self.index = 1
	def update_song_queue(self):
		global selected_song_path
		playing = selected_song_path if len(audio_queue) < 1 else (audio_queue[queue_index.integer] if queue_index.integer == -1 else audio_queue[0])
		self.currently_playing.text = "Currently Playing: %s" % str(playing.removeprefix(library_path).removesuffix(".wav"))
		self.song_grid_layout.clear_widgets()
		self.index = 1
		for song in audio_queue:
			item_container = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)
			item_container.bind(minimum_height=self.song_grid_layout.setter("height"))
			btn = Button(text="#%s:" % self.index + " " + str(song.removeprefix(library_path).removesuffix(".wav")), shorten=True,size_hint_y=None, height=40, width=400,shorten_from="right", size_hint=(1.0, 1.0), halign="left", valign="middle")
			btn.bind(size=btn.setter('text_size'))
			btn.padding = (20,0)
			btn.index = self.index - 1
			move_up = Button(text="^", size_hint_y=None, height=40, width=400, size_hint=(0.1, 1.0), halign="center", valign="middle")
			move_up.bind(size=move_up.setter('text_size'))
			move_up.padding = (20,0)
			move_up.index = self.index - 1
			move_down = Button(text="V", size_hint_y=None, height=40, width=400, size_hint=(0.1, 1.0), halign="center", valign="middle")
			move_down.bind(size=move_down.setter('text_size'))
			move_down.padding = (20,0)
			move_down.index = self.index - 1
			remove = Button(text="X", size_hint_y=None, height=40, width=400, size_hint=(0.1, 1.0), halign="center", valign="middle")
			remove.bind(size=move_down.setter('text_size'))
			remove.padding = (20,0)
			remove.index = self.index - 1
			self.index += 1
			btn.bind(on_release=self.play_from_queue)
			move_up.bind(on_release=self.move_up)
			move_down.bind(on_release=self.move_down)
			remove.bind(on_release=self.remove_song)
			item_container.add_widget(btn)
			item_container.add_widget(move_up)
			item_container.add_widget(move_down)
			item_container.add_widget(remove)
			self.song_grid_layout.add_widget(item_container)
	def move_up(self, button):
		if button.index <= 0: return
		if queue_index.integer == button.index:
			queue_index.integer -= 1
		temp = audio_queue[button.index - 1]
		audio_queue[button.index - 1] = audio_queue[button.index]
		audio_queue[button.index] = temp
	def move_down(self, button):
		if button.index >= len(audio_queue) - 1: return
		if queue_index.integer == button.index:
			queue_index.integer += 1
		temp = audio_queue[button.index + 1]
		audio_queue[button.index + 1] = audio_queue[button.index]
		audio_queue[button.index] = temp
	def remove_song(self, button):
		if queue_index.integer == button.index:
			if queue_index.integer == 0:
				queue_index.integer = 0
			else:
				queue_index.integer -= 1
		if len(audio_queue) == 1:
			queue_index.integer = -1
		audio_queue.pop(button.index)

	def play_from_queue(self, button):
		queue_index.integer = button.index
		music_player.loaded_sound.stop()
		music_player.playing = False
		music_player.paused = False
		music_player.update_buttons(None)
		music_player.play_song(button)


class MenuTabs(TabbedPanel):
	def __init__(self, lib_widget:LibraryScrollView, pl_widget:PlaylistMenu, imp_widget:ImporterMenu, queue_widget:SongQueue):
		super(MenuTabs,self).__init__()

		self.size_hint_x = 1.5
		self.do_default_tab = False

		music_library_tab:TabbedPanelItem = TabbedPanelItem(text="Music Library")
		music_library_tab.add_widget(lib_widget)
		self.add_widget(music_library_tab)

		playlist_tab:TabbedPanelItem = TabbedPanelItem(text="Playlists")
		playlist_tab.add_widget(pl_widget)
		self.add_widget(playlist_tab)

		importer_tab:TabbedPanelItem = TabbedPanelItem(text="Download\nSongs")
		importer_tab.add_widget(imp_widget)
		self.add_widget(importer_tab)

		local_import:TabbedPanelItem = TabbedPanelItem(text="Import\nLocal Songs")
		self.add_widget(local_import)

		song_queue:TabbedPanelItem = TabbedPanelItem(text="Song Queue")
		song_queue.add_widget(queue_widget)
		self.add_widget(song_queue)

library_scroll_view = LibraryScrollView()
playlist_menu = PlaylistMenu()
importer_menu = ImporterMenu()
song_queue = SongQueue()
music_player:MusicPlayer = MusicPlayer()

class BirdsongMain(App):
	def __init__(self):
		super().__init__()
		self.temp_aq = []
		self.temp_pl = []
		self.temp_lib = []
	def build(self):
		get_song_library()
		global library_scroll_view, playlist_menu, importer_menu, song_queue, music_player
		library_scroll_view = LibraryScrollView()
		playlist_menu = PlaylistMenu()
		importer_menu = ImporterMenu()
		song_queue = SongQueue()
		music_player = MusicPlayer()
		self.base_layout = BoxLayout(orientation = 'horizontal')
		self.base_layout.add_widget(MenuTabs(library_scroll_view,playlist_menu,importer_menu,song_queue))
		self.base_layout.add_widget(music_player)
		Clock.schedule_interval(self.update, 0.01)
		return self.base_layout
	def update(self, *args):
		get_song_library()
		playing = selected_song_path if len(audio_queue) < 1 else (audio_queue[queue_index.integer] if queue_index.integer != -1 else audio_queue[0])
		song_queue.currently_playing.text = "Currently Playing: %s" % str(playing.removeprefix(library_path).removesuffix(".wav"))
		if audio_queue != self.temp_aq:
			song_queue.update_song_queue()
		if playlists != self.temp_pl:
			playlist_menu.update_playlists()
		if library != self.temp_lib:
			library_scroll_view.update_library()
		self.temp_pl = playlists.copy()
		self.temp_lib = library.copy()
		self.temp_aq = audio_queue.copy()
def get_song_library():
	if not os.path.exists(library_path):
		print("Music Library does not exist!\nCreating Music Library.")
		os.mkdir(library_path)
	library.clear()
	playlists.clear()
	for wav in os.listdir(library_path):
		if wav.endswith(".wav"):
			library.append(os.path.join(library_path,wav))
	for txt in os.listdir(library_path):
		if txt.endswith(".txt"):
			playlists.append(os.path.join(library_path,txt))

if __name__ == '__main__':
	instance = BirdsongMain()
	instance.run()