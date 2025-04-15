from customtkinter import *
import vlc
import os
import threading
from PyQt5.QtWidgets import QApplication, QFileDialog

from video import VideoFrame
from subtitles import SubsFrame

class VideoAndSubsFrame(CTkFrame):
	def __init__(self, master, info_frame):
		super().__init__(master)
		self.rowconfigure(2, weight=1)
		self.columnconfigure((0, 1), weight=1)

		self.load_video_button = CTkButton(self, text="Load Video", command=self.load_video_action)
		self.load_video_button.grid(row=0, column=0, padx=10, pady=10)

		self.load_subtitle_button = CTkButton(self, text="Load Subtitles", command=self.load_subtitle_action)
		self.load_subtitle_button.grid(row=0, column=1, padx=10, pady=10)

		self.info_frame = info_frame
		self.video_frame = VideoFrame(self)
		self.video_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n", columnspan=2)
		self.video_frame.load()

		self.subtitle_container = CTkFrame(self, fg_color="transparent")
		self.subtitle_container.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="n", columnspan=2)

		self.subtitles = []
		self.current_sub_frames = []
		self.current_index = 0

		self._update_subs()
		self._update_time_label()

	def load_video_action(self):
		# Use PyQt5 file dialog
		app = QApplication.instance()
		if app is None:
			app = QApplication([])

		file_path, _ = QFileDialog.getOpenFileName(
			caption="Select Video File",
			filter="Video Files (*.mp4 *.avi *.mkv);;All Files (*)"
		)

		if not file_path:
			return

		self._clear_old_subs()

		self.video_frame.video_path = file_path
		self.video_frame.load()

		# Auto-load subtitle with same filename and .srt extension
		self.subtitle_path = file_path[:-4] + ".srt"
		self.subtitles.clear()
		self.current_sub_frames.clear()
		self.current_index = 0

		try:
			self._load_subtitles()
		except FileNotFoundError:
			pass

	def load_subtitle_action(self):
		# Use PyQt5 file dialog
		app = QApplication.instance()
		if app is None:
			app = QApplication([])

		file_path, _ = QFileDialog.getOpenFileName(
			caption="Select Subtitle File",
			filter="Subtitle Files (*.srt);;All Files (*)"
		)

		if not file_path:
			return
		self._clear_old_subs()

		self.subtitle_path = file_path
		self.subtitles.clear()
		self.current_sub_frames.clear()
		self.current_index = 0

		self._load_subtitles()

	def _load_subtitles(self):
		with open(self.subtitle_path, encoding="utf-8") as file:
			for subtitle_str in file.read().split("\n\n"):
				lines = subtitle_str.strip().split('\n')
				if len(lines) < 3:
					continue

				timing = lines[1].split(' --> ')
				text_lines = lines[2:]

				self.subtitles.append({
					"start": self._to_ms(timing[0]),
					"end": self._to_ms(timing[1]),
					"lines": text_lines
				})

	def _to_ms(self, srt_time):
		hours, minutes, rest = srt_time.split(':')
		seconds, milliseconds = rest.split(',')

		return (
			int(hours) * 3600 * 1000 +
			int(minutes) * 60 * 1000 +
			int(seconds) * 1000 +
			int(milliseconds)
		)

	def _clear_old_subs(self):
		for frame in self.current_sub_frames:
			frame.destroy()
		self.current_sub_frames.clear()

	def _show_subs(self, lines):
		self._clear_old_subs()

		for i, line in enumerate(lines):
			sub_frame = SubsFrame(self.subtitle_container, line, self.info_frame)
			sub_frame.grid(row=i, column=0, pady=(0 if i == 0 else 5, 0), sticky="n")
			self.current_sub_frames.append(sub_frame)

	def _update_subs(self):
		time = self.video_frame.player.get_time()

		if self.current_index < len(self.subtitles):
			sub = self.subtitles[self.current_index]

			if time > sub["end"]:
				self._clear_old_subs()
				self.current_index += 1

			elif sub["start"] <= time <= sub["end"]:
				if not self.current_sub_frames:
					self._show_subs(sub["lines"])

		self.after(100, self._update_subs)

	def _update_time_label(self):
		total_time = self.video_frame.player.get_length() // 1000
		current_time = self.video_frame.player.get_time() // 1000

		current_time_formatted = f"{current_time // 60:02}:{current_time % 60:02}"
		total_time_formatted = f"{total_time // 60:02}:{total_time % 60:02}"

		self.video_frame.time_label.configure(text=f"{current_time_formatted} / {total_time_formatted}")

		# Call the method again after 100ms to update
		self.after(100, self._update_time_label)

