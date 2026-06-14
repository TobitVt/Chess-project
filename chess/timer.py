# import threading
# import time


# def format_time(seconds):
#     seconds = max(0, seconds)
#     minutes, secs = divmod(seconds, 60)
#     return f"{minutes:02d}:{secs:02d}"


# class ChessTimer:
#     def __init__(self, seconds_per_player):
#         self.remaining = {
#             "white": seconds_per_player,
#             "black": seconds_per_player
#         }
#         self.current_color = None
#         self._stop_event = threading.Event()
#         self._thread = None
#         self._lock = threading.Lock()
#         self._turn_start_remaining = 0
#         self._input_prompt = ""

#     def get_remaining(self, player):
#         return max(0, self.remaining.get(player, 0))

#     def has_time(self, player):
#         return self.get_remaining(player) > 0

#     def _countdown(self):
#         while not self._stop_event.is_set() and self.remaining[self.current_color] > 0:
#             mins, secs = divmod(self.remaining[self.current_color], 60)
#             timer_text = f"[{mins:02d}:{secs:02d}] {self._input_prompt}"

#             try:
#                 print(f"\r{timer_text}", end="", flush=True)
#             except Exception:
#                 pass

#             time.sleep(1)
#             with self._lock:
#                 self.remaining[self.current_color] -= 1

#         if self.remaining[self.current_color] == 0:
#             try:
#                 print("\n00:00 - Time's up!\n", end="", flush=True)
#             except Exception:
#                 pass

#     def start_turn(self, player):
#         self.current_color = player
#         self._turn_start_remaining = self.get_remaining(player)
#         self._stop_event.clear()
#         self._thread = None

#     def timed_input(self, prompt):
#         self._input_prompt = prompt
#         try:
#             print(f"[{format_time(self.get_remaining(self.current_color))}] {prompt}", end="", flush=True)
#         except Exception:
#             pass

#         if self._thread is None or not self._thread.is_alive():
#             self._thread = threading.Thread(target=self._countdown)
#             self._thread.daemon = True
#             self._thread.start()

#         return input()

#     def stop_turn(self):
#         self._stop_event.set()

#         if self._thread is not None:
#             self._thread.join(timeout=0.1)

#         elapsed = max(0, self._turn_start_remaining - self.get_remaining(self.current_color))
#         timed_out = self.get_remaining(self.current_color) == 0
#         return elapsed, timed_out