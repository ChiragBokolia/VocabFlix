from customtkinter import *

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

		self.video_frame = VideoFrame(self)
		self.video_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n", columnspan=2)

		self.subtitle_container = CTkFrame(self, fg_color="transparent")
		self.subtitle_container.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="n", columnspan=2)

		self.info_frame = info_frame

		self.subtitles = []
		self.current_sub_frames = []
		self.current_index = 0

		self.update_subs()
		self.update_time_label()

		self.info_frame.set_text("Click on the `Load Video` button to play a video!")


	def load_video_action(self):
		file_path = filedialog.askopenfilename(
			title="Select a video file",
			filetypes=[
				("Video files", "*.avi *.mkv *.mp4 *.mov *.flv *.webm *.ogg"),
				("All files", "*.*")
			],
			defaultextension=".mp4"
		)

		if not file_path: return
		self.video_frame.load(file_path)

		try: self.load_subs(file_path[:-4] + ".srt")
		except FileNotFoundError:
			try: self.load_subs(file_path[:-4] + ".vtt")
			except FileNotFoundError:
				self.info_frame.set_text("Subtitles file not found!")

		self.info_frame.set_text("Hover on a word in the subtitles to get the definition!")


	def load_subtitle_action(self):
		file_path = filedialog.askopenfilename(
			title="Select a subtitles file",
			filetypes=[
				("Video files", "*.srt *.vtt"),
				("All files", "*.*")
			],
			defaultextension=".srt"
		)

		if not file_path: return
		self.load_subs(file_path)


	def load_subs(self, subtitle_path):
		with open(subtitle_path, encoding="utf-8") as file:
			content = file.read()

			self._clear_current_subs_frames()
			self.subtitles.clear()
			self.current_index = 0

			is_vtt = content.lstrip().startswith("WEBVTT")
			blocks = content.strip().split("\n\n")

			for block in blocks:
				lines = block.strip().split('\n')
				if is_vtt:
					if not lines or '-->' not in lines[0]:
						continue

					timing_line = lines[0]
					text_lines = lines[1:]

					start_str, end_str = timing_line.split(' --> ')
					# Convert . to , for compatibility with _to_ms
					start_str = start_str.strip().split(' ')[0].replace('.', ',')
					end_str = end_str.strip().split(' ')[0].replace('.', ',')

				else:
					if len(lines) < 3: continue

					timing = lines[1].split(' --> ')
					start_str = timing[0].strip()
					end_str = timing[1].strip()
					text_lines = lines[2:]

				self.subtitles.append({
					"start": self._to_ms(start_str),
					"end": self._to_ms(end_str),
					"lines": text_lines
				})


	def update_subs(self):
		time = self.video_frame.player.get_time()

		if self.current_index < len(self.subtitles):
			sub = self.subtitles[self.current_index]

			if time > sub["end"]:
				self._clear_current_subs_frames()
				self.current_index += 1

			elif sub["start"] <= time <= sub["end"]:
				if not self.current_sub_frames:
					self._clear_current_subs_frames()

					for i, line in enumerate(sub["lines"]):
						sub_frame = SubsFrame(self.subtitle_container, line, self.info_frame)
						sub_frame.grid(row=i, column=0, pady=(0 if i == 0 else 5, 0), sticky="n")
						self.current_sub_frames.append(sub_frame)

		self.after(100, self.update_subs)


	def update_time_label(self):
		total_time = self.video_frame.player.get_length() // 1000
		current_time = self.video_frame.player.get_time() // 1000

		current_time_formatted = f"{current_time // 60:02}:{current_time % 60:02}"
		total_time_formatted = f"{total_time // 60:02}:{total_time % 60:02}"

		self.video_frame.time_label.configure(text=f"{current_time_formatted} / {total_time_formatted}")
		self.after(100, self.update_time_label)


	def _to_ms(self, srt_time):
		hours, minutes, rest = srt_time.split(':')
		seconds, milliseconds = rest.split(',')

		return (
			int(hours) * 3600 * 1000 +
			int(minutes) * 60 * 1000 +
			int(seconds) * 1000 +
			int(milliseconds)
		)


	def _clear_current_subs_frames(self):
		for frame in self.current_sub_frames:
			frame.destroy()
		self.current_sub_frames.clear()
