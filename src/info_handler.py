import re
import os
import threading

from customtkinter import *
import requests
from bs4 import BeautifulSoup


class InfoFrame(CTkFrame):
	def __init__(self, master):
		super().__init__(master)
		self.rowconfigure(1, weight=1)
		self.columnconfigure(0, weight=1)

		self.textbox = CTkTextbox(self, font=("Arial", 16), wrap="word")
		self.textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
		self.textbox.configure(state="disabled")

		self.definitions_cache = {}


	def set_text(self, text):
		self.textbox.configure(state="normal")
		self.textbox.delete("1.0", "end")
		self.textbox.insert("1.0", text)
		self.textbox.configure(state="disabled")


	def _fetch_and_update(self, clean_word):
		if not clean_word:
			self.set_text(f"{clean_word}: (Invalid word)")
			return

		if clean_word in self.definitions_cache:
			definition = self.definitions_cache[clean_word]
		else:
			definition = self.get_definition(clean_word)
			self.definitions_cache[clean_word] = definition

		self.set_text(f"{clean_word}:\n\n{definition}")


	def get_definition(self, word):
		url = f"https://www.vocabulary.com/dictionary/{word}"
		headers = {
			"User-Agent": "Mozilla/5.0"
		}

		try:
			response = requests.get(url, headers=headers, timeout=5)
			if response.status_code != 200:
				return "Definition not found."

			soup = BeautifulSoup(response.content, 'lxml')
			definition_section = soup.find('div', class_='word-definitions')
			if not definition_section:
				return "No definitions found."

			output = []

			senses = definition_section.find_all('li', class_='sense')
			for sense in senses:
				definition_div = sense.find('div', class_='definition')
				if not definition_div:
					continue

				pos_icon = definition_div.find('div', class_='pos-icon')
				if pos_icon:
					pos = pos_icon.extract().get_text(strip=True)
				else:
					pos = "unknown"

				definition = definition_div.get_text(strip=True)
				output.append(f"[{pos}] {definition}")

				ex = sense.find('div', class_='example')
				if ex:
					output.append(f"• Example: {ex.get_text(strip=True, separator=' ')}")

				synonyms_section = sense.find('div', class_='div-replace-dl')
				if synonyms_section:
					synonyms = [syn.text.strip() for syn in synonyms_section.find_all('a', class_='word')[:2]]
					if synonyms:
						output.append(f"• Synonyms: {', '.join(synonyms)}")

				output.append("")  # blank line between senses

			return "\n".join(output).strip()

		except Exception as e:
			return f"Error: {str(e)}"


	def change(self, word):
		clean_word = re.sub(r'[^a-zA-Z]', '', word).lower()
		self.set_text(f"{clean_word}: Loading...")
		threading.Thread(target=self._fetch_and_update, args=(clean_word,), daemon=True).start()
