"""
QA harness for Industrial Capitalist.

Runs the REAL game (main.py, including its module-level game loop) with pygame's
input functions redirected to a scripted "bot". Every event the bot sends goes
through the game's own event handling; every frame is a real frame produced by
the game's real render path. Nothing about the game's logic is bypassed.

Time is accelerated by making Clock.tick() not sleep and Clock.get_time()
report a fixed frame delta -- the same thing as sitting in front of the game
for a long time, just faster.
"""
import os
import sys
import types
import traceback

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

def _find_root(start):
    """Walk up until main.py turns up, so this works wherever it is imported
    from."""
    d = os.path.dirname(os.path.abspath(start))
    for _ in range(6):
        if os.path.exists(os.path.join(d, "main.py")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    raise RuntimeError("could not locate main.py above " + start)


ROOT = _find_root(__file__)
SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")


class Bot:
    """Scripted player. Helper methods are generators that yield event batches;
    one yield == one game frame."""

    def __init__(self, driver):
        self.d = driver
        self.mouse = (10, 10)
        self.buttons = [False, False, False, False, False]
        self.keys = {}
        self.mods = 0

    # ---- live game state --------
    @property
    def ns(self):
        return self.d.ns

    def g(self, name, default=None):
        return self.d.ns.get(name, default)

    # ---- primitives --------
    def idle(self, frames=1):
        for _ in range(frames):
            yield []

    wait = idle

    def move(self, x, y):
        old = self.mouse
        self.mouse = (int(x), int(y))
        yield [pygame.event.Event(pygame.MOUSEMOTION, pos=self.mouse,
                                  rel=(self.mouse[0] - old[0], self.mouse[1] - old[1]),
                                  buttons=tuple(int(b) for b in self.buttons[:3]))]

    def click(self, x=None, y=None, button=1, frames_between=2):
        if x is not None:
            yield from self.move(x, y)
        pos = self.mouse
        self.buttons[button - 1] = True
        yield [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=button, touch=False)]
        yield from self.idle(frames_between)
        self.buttons[button - 1] = False
        yield [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=button, touch=False)]
        yield from self.idle(1)

    def drag(self, x0, y0, x1, y1, button=1, steps=6):
        yield from self.move(x0, y0)
        self.buttons[button - 1] = True
        yield [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=self.mouse, button=button, touch=False)]
        for i in range(1, steps + 1):
            yield from self.move(x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps)
        self.buttons[button - 1] = False
        yield [pygame.event.Event(pygame.MOUSEBUTTONUP, pos=self.mouse, button=button, touch=False)]
        yield from self.idle(1)

    def scroll(self, amount, x=None, y=None):
        if x is not None:
            yield from self.move(x, y)
        yield [pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=amount,
                                  flipped=False, precise_x=0.0, precise_y=float(amount),
                                  touch=False)]

    def key(self, k, mod=0, unicode_=""):
        # game code reads modifiers through pygame.key.get_mods(), not ev.mod,
        # so the held-modifier state has to be live while the event is handled
        self.keys[k] = True
        self.mods = mod
        yield [pygame.event.Event(pygame.KEYDOWN, key=k, mod=mod, unicode=unicode_,
                                  scancode=0)]
        self.keys[k] = False
        yield [pygame.event.Event(pygame.KEYUP, key=k, mod=mod, scancode=0)]
        self.mods = 0

    def hold(self, k, frames):
        """Hold a key down for N frames (for key.get_pressed() driven camera)."""
        self.keys[k] = True
        yield [pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="", scancode=0)]
        yield from self.idle(max(0, frames - 1))
        self.keys[k] = False
        yield [pygame.event.Event(pygame.KEYUP, key=k, mod=0, scancode=0)]

    def type_text(self, text):
        for ch in text:
            k = getattr(pygame, "K_" + ch.lower(), None)
            if k is None:
                k = ord(ch) if ord(ch) < 128 else 0
            yield from self.key(k, unicode_=ch)

    # ---- observation --------
    def shot(self, name):
        self.d.pending_shot = name
        yield []

    def log(self, *a):
        self.d.log(*a)


class Driver:
    def __init__(self, scenario, max_frames=200000, dt_ms=50, shot_dir=SHOTS):
        self.scenario = scenario
        self.max_frames = max_frames
        self.dt_ms = dt_ms
        self.frames = 0
        self.ns = {}
        self.pending_shot = None
        self.shot_dir = shot_dir
        self.screen = None
        self.bot = Bot(self)
        self.gen = None
        self.finished = False
        self.error = None
        self.logs = []
        os.makedirs(self.shot_dir, exist_ok=True)

    def log(self, *a):
        msg = " ".join(str(x) for x in a)
        self.logs.append(msg)
        print("[bot]", msg, flush=True)

    # ---- patched pygame surface --------
    def _event_get(self, *args, **kwargs):
        self.frames += 1
        if self.frames > self.max_frames:
            self.finished = True
            return [pygame.event.Event(pygame.QUIT)]
        if self.gen is None:
            self.gen = self.scenario(self.bot)
        try:
            evs = next(self.gen)
        except StopIteration:
            self.finished = True
            return [pygame.event.Event(pygame.QUIT)]
        except Exception:
            self.error = traceback.format_exc()
            self.finished = True
            return [pygame.event.Event(pygame.QUIT)]
        return list(evs or [])

    def _mouse_get_pos(self):
        return self.bot.mouse

    def _mouse_get_pressed(self, num_buttons=3):
        return tuple(bool(b) for b in self.bot.buttons[:num_buttons])

    def _key_get_mods(self):
        return self.bot.mods

    def _key_get_pressed(self):
        keys = self.bot.keys

        class _K:
            def __getitem__(self, k):
                return bool(keys.get(k, False))

            def __len__(self):
                return 512
        return _K()

    def _flip(self, *a, **k):
        if self.pending_shot:
            name = self.pending_shot
            self.pending_shot = None
            try:
                surf = pygame.display.get_surface()
                if surf is not None:
                    path = os.path.join(self.shot_dir, f"{name}.png")
                    pygame.image.save(surf, path)
                    self.log(f"screenshot -> {path}")
            except Exception as e:  # pragma: no cover
                self.log(f"screenshot failed: {e}")

    def run(self):
        pygame.init()

        # --- input redirection
        pygame.event.get = self._event_get
        pygame.event.poll = lambda: pygame.event.Event(pygame.NOEVENT)
        pygame.event.wait = lambda *a, **k: pygame.event.Event(pygame.NOEVENT)
        pygame.event.pump = lambda *a, **k: None
        pygame.event.clear = lambda *a, **k: None
        pygame.mouse.get_pos = self._mouse_get_pos
        pygame.mouse.get_pressed = self._mouse_get_pressed
        pygame.mouse.set_visible = lambda *a, **k: None
        pygame.key.get_pressed = self._key_get_pressed
        pygame.key.get_mods = self._key_get_mods
        pygame.key.set_repeat = lambda *a, **k: None

        # --- no vsync sleeping, fixed frame delta
        dt_ms = self.dt_ms
        driver = self

        class FakeClock:
            def tick(self_, fps=0):
                return dt_ms

            tick_busy_loop = tick

            def get_time(self_):
                return dt_ms

            def get_rawtime(self_):
                return dt_ms

            def get_fps(self_):
                return 1000.0 / dt_ms

        pygame.time.Clock = FakeClock
        pygame.time.delay = lambda ms: None
        pygame.time.wait = lambda ms: None
        pygame.time.get_ticks = lambda: int(driver.frames * dt_ms)

        # --- virtual wall clock so time.time()-driven animations advance too
        import time as _time
        real_time = _time.time
        state = {"t": real_time()}

        def fake_time():
            return state["t"]

        _time.sleep = lambda s: state.__setitem__("t", state["t"] + s)
        _time.time = fake_time

        # --- screenshots
        pygame.display.flip = self._flip
        pygame.display.update = self._flip

        # advance the virtual clock once per frame
        orig_event_get = self._event_get

        def event_get(*a, **k):
            state["t"] += dt_ms / 1000.0
            return orig_event_get(*a, **k)
        pygame.event.get = event_get

        sys.path.insert(0, ROOT)
        os.chdir(ROOT)
        code = compile(open(os.path.join(ROOT, "main.py")).read(), "main.py", "exec")
        self.ns["__name__"] = "__main__"
        self.ns["__file__"] = os.path.join(ROOT, "main.py")
        try:
            exec(code, self.ns)
        except SystemExit:
            pass
        except Exception:
            self.error = traceback.format_exc()
            print("\n=== GAME CRASHED ===", flush=True)
            print(self.error, flush=True)
        return self


def run_scenario(scenario, **kw):
    return Driver(scenario, **kw).run()
