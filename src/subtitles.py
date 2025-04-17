from customtkinter import *


class SubsFrame(CTkFrame):
	def __init__(self, master, text_line, info_frame):
		super().__init__(master, fg_color="transparent")

		self.info_frame = info_frame
		self.subtitle_font = ("Arial", 24, "bold")

		words = text_line.split()
		for col, word in enumerate(words):
			label = CTkLabel(self, text=word, cursor="hand2", font=self.subtitle_font, fg_color="transparent")
			label.grid(row=0, column=col, padx=4, pady=3)

			label.bind("<Enter>", lambda e, w=word: self.info_frame.change(w))
			# label.bind("<Leave>", lambda e: self.info_frame.set_text(""))
