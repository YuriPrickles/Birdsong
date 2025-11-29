


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
import uyts

import yt_dlp
with yt_dlp.YoutubeDL() as ydl:
    ydl.download("https://youtube.com/watch?v=Bx1lXJGuo8w")

import sys
print(sys.executable)

app_paths = AppDataPaths("Birdsong")
app_paths.setup()
print(app_paths.app_data_path)

library_path = app_paths.app_data_path + "\\MusicLibrary\\"
print(library_path)

library:list[str] = []
playlists:list[str] = []
print(library)
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
		self.selected_song_path = audio_queue[queue_index.integer] if len(audio_queue) > 0 else (audio_queue[0] if queue_index.integer == -1 else library[0])
		self.loaded_sound = self.soundloader.load(self.selected_song_path)
		if self.soundloader:
			self.playing = True
			self.paused = False
			print("Sound found at %s" % self.loaded_sound.source)
			print("Sound is %.3f seconds" % self.loaded_sound.length)
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
		if self.soundloader:
			if queue_index.integer <= 0:
				return
			queue_index.integer -= 1
			self.loaded_sound.stop()
			self.selected_song_path = audio_queue[queue_index.integer]
			self.loaded_sound = self.soundloader.load(self.selected_song_path)
			self.playing = True
			self.paused = False
			self.loaded_sound.play()
			self.update_buttons(None)
	def play_next(self, button):
		if self.soundloader:
			if queue_index.integer >= len(audio_queue) - 1:
				return
			queue_index.integer += 1
			self.loaded_sound.stop()
			self.selected_song_path = audio_queue[queue_index.integer]
			self.loaded_sound = self.soundloader.load(self.selected_song_path)
			self.playing = True
			self.paused = False
			self.loaded_sound.play()
			self.update_buttons(None)
	def __init__(self):
		self.selected_song_path = library[0] if len(library) > 0 else ""
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
		layout = GridLayout(cols=1, spacing=10, size_hint_y=None,width=400,pos_hint=(0,0))
		layout.bind(minimum_height=layout.setter("height"))
		for song in library:
			item_container = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)
			item_container.bind(minimum_height=layout.setter("height"))
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
			layout.add_widget(item_container)

		self.add_widget(layout)
	def add_to_queue(self,button):
		audio_queue.append(button.path)
		print(audio_queue)
		print(queue_index.integer)
	def button_select(self, button):
		print(button.path)
		music_player.selected_song_path = button.path

class ContextMenu(Bubble):
	def __init__(self):
		super(ContextMenu,self).__init__()
		bc:BubbleContent = BubbleContent()
		add_to_playlist:BubbleButton(text="A")

class PlaylistMenu(ScrollView):
	def __init__(self):
		super(PlaylistMenu, self).__init__()
		layout = GridLayout(cols=1, spacing=10, size_hint_y=None,width=400,pos_hint=(0,0))
		layout.bind(minimum_height=layout.setter("height"))
		for pl in playlists:
			item_container = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)
			item_container.bind(minimum_height=layout.setter("height"))
			btn = Button(text=pl.removeprefix(library_path).removesuffix(".txt"), size_hint_y=None, height=40, width=400,shorten_from="right", size_hint=(2.0, 1.0), halign="left", valign="middle")
			btn.bind(size=btn.setter('text_size'))
			btn.path=pl
			btn.padding = (20,0)
			btn.halign = "left"
			btn.valign = "middle"
			btn.bind(on_release=self.button_select)
			item_container.add_widget(btn)
			layout.add_widget(item_container)
		self.popup = None
		box = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=40)
		box.bind(minimum_height=layout.setter("height"))
		self.addbutton = Button(text="+ Add new playlist...", size_hint_y=None, height=40, width=400,shorten_from="right", size_hint=(2.0, 1.0), halign="left", valign="middle")
		self.addbutton.bind(size=self.addbutton.setter('text_size'))
		self.addbutton.bind(on_release=self.add_playlist)
		box.add_widget(self.addbutton)
		layout.add_widget(box)
		self.add_widget(layout)
		self.to_add: list[str] = []
	def button_select(self, button):
		print(button.path)
		popup_layout = ScrollView()
		box = BoxLayout(orientation="vertical")
		grid = GridLayout(cols=1, spacing=10, size_hint_y=None,width=400,pos_hint=(0,0))
		closeButton = Button(text="Close",size_hint_y=0.2)
		playlist_file =open(button.path,"r")
		songlist_data:list[str] = eval(playlist_file.readline())

		for song in songlist_data:
			song_name:Label = Label(text=song, size_hint=(1.0, 1.0), halign="left", valign="middle")
			song_name.bind(size=song_name.setter('text_size'))
			grid.add_widget(song_name)
		popup_layout.add_widget(grid)
		box.add_widget(popup_layout)
		box.add_widget(closeButton)
		self.popup = Popup(
			title='Contents of playlist', content=box,
			auto_dismiss=False, size_hint=(None, None),
			size=(800, 600)
		)
		self.popup.open()
		closeButton.bind(on_press=self.on_close)

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
			checkbox = CheckBox(width=40)
			checkbox.metadata = song
			checkbox.bind(active=self.on_checkbox_active)
			label = Label(text=song.removeprefix(library_path).removesuffix(".wav"), halign="left", valign="middle", height= "40")
			label.bind(size=label.setter('text_size'))
			songselect = BoxLayout(orientation="horizontal", size_hint_y=None, width=800,height=40)
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
		search = uyts.Search(q,minResults=5)
		for res in search.results\
				:
			if res.resultType == "channel" or res.resultType == "playlist": continue
			button = Button(text="Download",size_hint_x=None)
			button.link = res.id
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
	def download_video(self, button):
		url = ['https://www.youtube.com/watch?v=%s' % button.link]
		ydl_opts = {
			'format': 'wav/bestaudio/best',
		    'postprocessors': [{  # Extract audio using ffmpeg
		        'key': 'FFmpegExtractAudio',
		        'preferredcodec': 'wav',
		    }],
			'keepvideo': False,
		}
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			ydl.download(url)
class MenuTabs(TabbedPanel):
	def __init__(self, lib_widget:LibraryScrollView, pl_widget:PlaylistMenu, imp_widget:ImporterMenu):
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
music_player:MusicPlayer = MusicPlayer()
class BirdsongMain(App):
	global selected_song_path
	def build(self):
		library_scroll_view = LibraryScrollView()
		playlist_menu = PlaylistMenu()
		importer_menu = ImporterMenu()
		self.base_layout = BoxLayout(orientation = 'horizontal')
		self.base_layout.add_widget(MenuTabs(library_scroll_view,playlist_menu,importer_menu))
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
		for txt in os.listdir(library_path):
			if txt.endswith(".txt"):
				print(os.path.join(library_path,txt))
				playlists.append(os.path.join(library_path,txt))

if __name__ == '__main__':
	instance = BirdsongMain()
	instance.get_song_library()
	instance.run()