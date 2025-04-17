from customtkinter import *

from info_handler import InfoFrame
from video_and_subtitles_handler import VideoAndSubsFrame


class App(CTk):
	def __init__(self, title):
		super().__init__()

		self.title(title)
		self.geometry("1280x720")
		self.minsize(1280, 720)

		self.rowconfigure(0, weight=1)
		self.columnconfigure(1, weight=1)

		info_frame = InfoFrame(self)
		info_frame.grid(row=0, column=1, padx=(0,10), pady=10, sticky="nsew")

		video_and_subs_frame = VideoAndSubsFrame(self, info_frame)
		video_and_subs_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")


if __name__ == "__main__":
	set_appearance_mode("system")
	set_default_color_theme("blue")
	app = App("VocabFlix")
	app.mainloop()
