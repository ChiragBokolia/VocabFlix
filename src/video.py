import platform
import time
from customtkinter import *
import vlc

class VideoFrame(CTkFrame):
	def __init__(self, master):
		super().__init__(master)
		self.rowconfigure(0, weight=1)

		self.canvas = CTkCanvas(self, width=640, height=360, bg="black")
		self.canvas.grid(row=0, column=0, padx=0, pady=0, columnspan=2)

		self.time_label = CTkLabel(self, text="00:00 / 00:00")
		self.time_label.grid(row=2, column=0, padx=10, pady=(0, 10))

		self.playback_control_button = CTkButton(self, text="⏸️", width=40, command=self.pause_play)
		self.playback_control_button.grid(row=2, column=1, padx=10, pady=(0, 10))

		self.slider = CTkSlider(self, from_=0, to=1000, command=lambda value: self.player.set_time(int(value)) if self.player.get_length() > 0 else None)
		self.slider.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

		self.instance = vlc.Instance("--quiet", "--no-video-title-show", "--no-sub-autodetect-file")
		self.player = self.instance.media_player_new()

		self.video_length = -1

		self.update_slider()


	def load(self, video_path):
		media = self.instance.media_new(video_path)
		self.player.set_media(media)

		if platform.system() == 'Windows':
			self.player.set_hwnd(self.canvas.winfo_id())
		elif platform.system() == 'Linux':
			self.player.set_xwindow(self.canvas.winfo_id())
		elif platform.system() == 'Darwin':
			self.player.set_nsobject(self.canvas.winfo_id())

		self.player.play()
		self.playback_control_button.configure(text="⏸️")
		self.after(500, self.set_slider)


	def pause_play(self):
		self.player.pause()

		if self.player.is_playing():
			self.playback_control_button.configure(text="▶️")
		else:
			self.playback_control_button.configure(text="⏸️")


	def set_slider(self):
		self.video_length = self.player.get_length()
		if self.video_length > 0:
			self.slider.configure(to=self.video_length)
		else:
			self.after(500, self.set_slider)


	def update_slider(self):
		current = self.player.get_time()

		if self.video_length > 0:
			self.slider.set(current)

			self.time_label.configure(
				text=f"{self._format_time(current)} / {self._format_time(self.video_length)}"
			)

		self.after(500, self.update_slider)


	def _format_time(self, ms):
		seconds = ms // 1000
		minutes = seconds // 60
		seconds = seconds % 60
		return f"{minutes:02}:{seconds:02}"
