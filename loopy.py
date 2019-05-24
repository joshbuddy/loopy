from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
import mutagen.mp3
import glob, os
import subprocess
import random

class SongCompleter(Completer):
  def __init__(self, player):
    self.player = player

  def get_completions(self, document, complete_event):
    completed = False
    for k in self.player.songs.keys():
      if document.text in k:
        completed = True
        yield Completion(k, start_position=-document.cursor_position)
    if not completed:
      yield Completion("no matches!", start_position=-document.cursor_position)

class Player:
  def __init__(self):
    self.songs = {}
    for file in glob.glob("**/*.mp3", recursive=True):
      metadata = mutagen.mp3.Open(file)
      key = f"{file}"
      if "TALB" in metadata:
        key += f" {' '.join(metadata['TALB'].text)}"
      if "TIT2" in metadata:
        key += f" {' '.join(metadata['TIT2'].text)}"
#
      if "tuning notes" not in key.lower():
        self.songs[key.lower()] = file

    self.completer = SongCompleter(self)
    print(f"loaded {len(self.songs)} songs")

  def run(self):
    running = True
    while running:
      answer = prompt("r/q or type >", completer=self.completer)
      key = None
      if answer.strip() == 'q':
        running = False
      elif answer.strip() == 'r':
        print('picking a random song')
        key = random.choice(list(self.songs.keys()))
      else:
        key = answer.strip()

      print("playing", key)
      if key in self.songs:
        path = self.songs[key]
        process = None
        try:
          process = subprocess.run(["mpg123", "-0", path])
        except KeyboardInterrupt:
          if process:
            process.terminate()

Player().run()


