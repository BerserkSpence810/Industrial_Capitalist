import pygame, os, math, time, random, json, shutil, platform, getpass



def _gather_sys_info():
    info = {}
    try:
        info["user"] = getpass.getuser().lower()
    except Exception:
        info["user"] = "user"

    try:
        hn = platform.node().lower()
        if hn.endswith(".local"):
            hn = hn[:-6]
        info["host"] = hn or "localhost"
    except Exception:
        info["host"] = "localhost"

    try:
        sys_name = platform.system()
        rel = platform.release()
        if sys_name == "Darwin":
            mac_ver = platform.mac_ver()[0]
            info["os"] = f"macOS {mac_ver}" if mac_ver else "macOS"
            info["kernel"] = f"darwin {rel}"
            info["sys_short"] = "darwin"
        elif sys_name == "Linux":
            info["os"] = "Linux"
            info["kernel"] = f"linux {rel}"
            info["sys_short"] = "linux"
        elif sys_name == "Windows":
            info["os"] = f"Windows {rel}"
            info["kernel"] = f"nt {platform.version()}"
            info["sys_short"] = "windows"
        else:
            info["os"] = sys_name
            info["kernel"] = rel
            info["sys_short"] = sys_name.lower()
    except Exception:
        info["os"] = "unknown"
        info["kernel"] = "unknown"
        info["sys_short"] = "unknown"

    try:
        info["arch"] = platform.machine() or "x86_64"
    except Exception:
        info["arch"] = "x86_64"

    try:
        info["cores"] = os.cpu_count() or 1
    except Exception:
        info["cores"] = 1

    try:
        info["py"] = platform.python_version()
    except Exception:
        info["py"] = "3.x"

    try:
        total, used, free = shutil.disk_usage("/")
        info["disk_total_gb"] = total // (1024 ** 3)
        info["disk_free_gb"] = free // (1024 ** 3)
    except Exception:
        info["disk_total_gb"] = 0
        info["disk_free_gb"] = 0

    try:
        info["pg_ver"] = pygame.version.ver
    except Exception:
        info["pg_ver"] = "?"

    try:
        sdl = pygame.version.SDL
        info["sdl_ver"] = f"{sdl.major}.{sdl.minor}.{sdl.patch}"
    except Exception:
        info["sdl_ver"] = "?"

    try:
        dinfo = pygame.display.Info()
        info["screen_w"] = dinfo.current_w
        info["screen_h"] = dinfo.current_h
    except Exception:
        info["screen_w"] = 0
        info["screen_h"] = 0

    return info


SYS = _gather_sys_info()


def _shell_prompt(cwd="~"):
    return f"{SYS['user']}@{SYS['host']}:{cwd}$ "


def _build_boot_lines():
    arch = SYS["arch"]
    cores = SYS["cores"]
    os_name = SYS["os"]
    kernel = SYS["kernel"]
    sys_short = SYS["sys_short"]
    py = SYS["py"]
    pg_ver = SYS["pg_ver"]
    sdl_ver = SYS["sdl_ver"]
    disk_total = SYS["disk_total_gb"]
    disk_free = SYS["disk_free_gb"]
    sw = SYS["screen_w"]
    sh = SYS["screen_h"]
    user = SYS["user"]
    host = SYS["host"]

    disk_line = (f"Storage: {disk_total} GB total, {disk_free} GB available"
                 if disk_total > 0 else "Storage: detected")

    if sw and sh:
        display_line = f"Display: {sw} x {sh}"
    else:
        display_line = "Display: detected"

    return [
        ("",         f"Industrial Capitalist v6.0 (BETA)  -  build 1024A", AMBER_HOT, 0.30),
        ("",         f"(c) 2026 Anthracite Industries.  All rights reserved.", AMBER_DIM, 0.18),
        ("",         "", AMBER, 0.08),
        ("",         f"Host: {user}@{host}", AMBER, 0.08),
        ("",         f"OS:   {os_name}  ({arch})", AMBER, 0.08),
        ("",         f"Kernel: {kernel}", AMBER, 0.08),
        ("",         f"CPU:  {cores} logical core{'s' if cores != 1 else ''}", AMBER, 0.10),
        ("",         disk_line, AMBER, 0.10),
        ("",         display_line, AMBER, 0.10),
        ("",         f"Python {py}  /  pygame {pg_ver}  /  SDL {sdl_ver}", AMBER_DIM, 0.18),
        ("",         "", AMBER, 0.08),
        ("",         "Performing startup checks...", AMBER, 0.20),
        ("[  OK  ]", "Verifying runtime ............ PASS", GREEN_OK, 0.06),
        ("[  OK  ]", "Loading configuration ........ PASS", GREEN_OK, 0.05),
        ("[  OK  ]", "Locating asset directory ..... ./SFX, ./data", GREEN_OK, 0.06),
        ("[  OK  ]", "Initializing audio mixer ..... 8 channels", GREEN_OK, 0.08),
        ("[  OK  ]", "Initializing display ......... pygame surface", GREEN_OK, 0.08),
        ("",         "", AMBER, 0.05),
        ("",         "Loading game subsystems...", AMBER, 0.18),
        ("[  OK  ]", "Power grid ................... STABLE", GREEN_OK, 0.10),
        ("[  OK  ]", "Logistics network ............ 4 REGIONS", GREEN_OK, 0.10),
        ("[ WARN ]", "Atmospheric sensor: BASELINE  -- monitor levels", AMBER, 0.18),
        ("[  OK  ]", "Market feed .................. LIVE", GREEN_OK, 0.10),
        ("[  OK  ]", "Machine drivers loaded ....... 117", GREEN_OK, 0.10),
        ("[  OK  ]", "Recipes loaded ............... 280", GREEN_OK, 0.10),
        ("[  OK  ]", "Tech tree synchronized ....... 71 NODES", GREEN_OK, 0.10),
        ("[  OK  ]", "Contract registry ............ 25 ACTIVE", GREEN_OK, 0.10),
        ("[  OK  ]", "Pollution model loaded ....... v2.1", GREEN_OK, 0.10),
        ("[  OK  ]", "Save manager ................. 3 SLOTS", GREEN_OK, 0.10),
        ("",         "", AMBER, 0.10),
        ("[  OK  ]", "All subsystems nominal.", GREEN_OK, 0.20),
        ("",         "", AMBER, 0.10),
        ("",         f"Welcome, {user}.  System ready.", AMBER_HOT, 0.30),
        ("",         "", AMBER, 0.10),
    ]



BG          = (8, 6, 4)
AMBER       = (255, 176, 60)
AMBER_HOT   = (255, 215, 130)
AMBER_DIM   = (180, 110, 30)
AMBER_LOW   = (110, 65, 18)
AMBER_FAINT = (60, 35, 10)
GREEN_OK    = (110, 240, 130)
GREEN_DIM   = (50, 130, 60)
RED_ERR     = (255, 70, 60)
RED_HOT     = (255, 130, 120)
RED_DIM     = (140, 30, 30)
WHITE       = (240, 240, 230)



_sfx_cache = {}
_music_volume = 0.5
_sfx_volume = 0.7

def init_audio():
    try:
        pygame.mixer.init()
        pygame.mixer.set_num_channels(8)
    except Exception:
        pass

def set_volumes(music_vol, sfx_vol):
    global _music_volume, _sfx_volume
    _music_volume = music_vol
    _sfx_volume = sfx_vol
    try:
        pygame.mixer.music.set_volume(_music_volume)
    except Exception:
        pass

def play_music(path, loops=-1):
    try:
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(_music_volume)
            pygame.mixer.music.play(loops)
    except Exception:
        pass

def stop_music():
    try: pygame.mixer.music.stop()
    except Exception: pass

def play_sfx(path):
    try:
        if path not in _sfx_cache:
            if os.path.exists(path):
                _sfx_cache[path] = pygame.mixer.Sound(path)
            else: return
        snd = _sfx_cache[path]
        snd.set_volume(_sfx_volume)
        snd.play()
    except Exception: pass

def play_button_sfx():        play_sfx("SFX/Hud/Play.wav")
def play_click_sfx():         play_sfx("SFX/Game/Click.wav")
def play_sell_sfx():          play_sfx("SFX/Game/Sell.wav")
def play_quit_sfx():          play_sfx("SFX/Hud/Quit.wav")
def play_error_sfx():         play_sfx("SFX/Hud/Error.mp3")
def play_research_sfx():      play_sfx("SFX/IGH/Research.wav")
def play_power_connect_sfx(): play_sfx("SFX/Game/PowerConnection.wav")
def play_power_fail_sfx():    play_sfx("SFX/Game/PowerConnectionComplete.wav")



SAVE_SLOTS = 3
SAVE_DIR = "data"

def _slot_dir(s): return os.path.join(SAVE_DIR, f"slot_{s}")
def _slot_meta_path(s): return os.path.join(_slot_dir(s), "meta.json")

def _slot_info(s):
    wf = os.path.join(_slot_dir(s), "world.json")
    if not os.path.exists(wf): return None
    info = {"slot": s}
    try: info["modified"] = time.strftime("%d %b %Y  %H:%M", time.localtime(os.path.getmtime(wf)))
    except: info["modified"] = "Unknown"
    try:
        with open(os.path.join(_slot_dir(s), "money.json")) as f:
            d = json.load(f)
            info["money"] = d.get("money", 0) if isinstance(d, dict) else d
    except: info["money"] = 0
    info["company"] = "UNNAMED CO."
    mp = _slot_meta_path(s)
    if os.path.exists(mp):
        try:
            with open(mp) as f:
                m = json.load(f)
                info["company"] = m.get("company", "UNNAMED CO.")
        except: pass
    return info

def _save_slot_meta(s, company):
    d = _slot_dir(s); os.makedirs(d, exist_ok=True)
    with open(_slot_meta_path(s), "w") as f:
        json.dump({"company": company}, f)

def _delete_slot(s):
    d = _slot_dir(s)
    if os.path.exists(d): shutil.rmtree(d)

_SLOT_FILES = ["world.json","money.json","pollution.json","research.json",
               "contracts.json","loans.json","protest.json","supply_demand.json",
               "milestones.json"]
_BACKUP_COUNT = 3

def _activate_slot(s):
    d = _slot_dir(s); os.makedirs(d, exist_ok=True)
    for fn in _SLOT_FILES:
        sf, af = os.path.join(d,fn), os.path.join(SAVE_DIR,fn)
        if os.path.exists(sf): shutil.copy2(sf, af)
        elif os.path.exists(af): os.remove(af)

def _rotate_slot_backups(d):
    try:
        oldest = os.path.join(d, f"backup_{_BACKUP_COUNT}")
        if os.path.exists(oldest):
            shutil.rmtree(oldest)
        for i in range(_BACKUP_COUNT - 1, 0, -1):
            src = os.path.join(d, f"backup_{i}")
            if os.path.exists(src):
                os.rename(src, os.path.join(d, f"backup_{i+1}"))
        snap = os.path.join(d, "backup_1")
        os.makedirs(snap, exist_ok=True)
        for fn in _SLOT_FILES + ["meta.json"]:
            sf = os.path.join(d, fn)
            if os.path.exists(sf):
                shutil.copy2(sf, os.path.join(snap, fn))
    except OSError:
        pass

def _save_active_to_slot(s):
    d = _slot_dir(s); os.makedirs(d, exist_ok=True)
    _rotate_slot_backups(d)
    for fn in _SLOT_FILES:
        af, sf = os.path.join(SAVE_DIR,fn), os.path.join(d,fn)
        if os.path.exists(af): shutil.copy2(af, sf)



_flicker_t = 0.0
_flicker_amount = 1.0

_menu_crt_surf  = None
_menu_crt_size  = None

def _get_menu_crt(W, H):
    global _menu_crt_surf, _menu_crt_size
    if _menu_crt_surf is None or _menu_crt_size != (W, H):
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        for y in range(0, H, 2):
            pygame.draw.line(s, (0, 0, 0, 25), (0, y), (W, y), 1)
        corner = min(50, W // 12, H // 8)
        for i in range(corner):
            alpha = int(35 * ((corner - i) / corner) ** 2.0)
            inset = i * 2
            r = pygame.Rect(inset, inset, W - inset * 2, H - inset * 2)
            if r.width > 2 and r.height > 2:
                pygame.draw.rect(s, (0, 0, 0, alpha), r, 3)
        _menu_crt_surf = s
        _menu_crt_size = (W, H)
    return _menu_crt_surf


def _apply_crt(scr, W, H):
    tint = pygame.Surface((W, H), pygame.SRCALPHA)
    tint.fill((8, 20, 6, 10))
    scr.blit(tint, (0, 0))
    scr.blit(_get_menu_crt(W, H), (0, 0))


def _clear_terminal(scr, W, H, elapsed, dt):
    global _flicker_t, _flicker_amount
    scr.fill(BG)

    _flicker_t -= dt
    if _flicker_t <= 0:
        _flicker_t = random.uniform(1.0, 5.0)
        _flicker_amount = random.choice([1.0, 1.0, 1.0, 1.0, 1.0, 0.92, 0.96])
    if _flicker_amount < 0.99:
        flick = pygame.Surface((W, H), pygame.SRCALPHA)
        flick.fill((255, 130, 40, int(255 * (1 - _flicker_amount) * 0.08)))
        scr.blit(flick, (0, 0))


def _blink(elapsed, rate=2.0):
    return int(elapsed * rate) % 2 == 0


def _term_text(scr, font, text, x, y, color):
    s = font.render(text, True, color)
    scr.blit(s, (x, y))
    return s.get_width()


def _draw_cursor(scr, x, y, font, color, elapsed):
    if _blink(elapsed, 2.5):
        h = font.get_height() - 4
        w = font.size("X")[0]
        pygame.draw.rect(scr, color, (x, y + 2, w, h))



BOOT_LINES = None


def _ensure_boot_lines():
    global BOOT_LINES
    if BOOT_LINES is None:
        SYS.update(_gather_sys_info())
        BOOT_LINES = _build_boot_lines()
    return BOOT_LINES


def run_splash(scr, clk):
    W, H = scr.get_size()

    boot_lines = _ensure_boot_lines()

    play_sfx("SFX/Hud/Start.mp3")

    f_term  = pygame.font.SysFont("consolas,couriernew,monospace", 14)
    f_termb = pygame.font.SysFont("consolas,couriernew,monospace", 14, bold=True)

    line_idx = 0
    pause_t = 0.5
    typed_lines = []
    char_progress = 0
    type_speed = 280.0
    final_pause = 0.0
    boot_complete = False
    cursor_t = 0.0
    t0 = time.time()
    last_t = t0

    while True:
        now = time.time()
        dt = now - last_t
        last_t = now
        elapsed = now - t0
        cursor_t += dt
        clk.tick(60)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if (ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN) and elapsed > 0.4:
                return True

        if not boot_complete:
            if pause_t > 0:
                pause_t -= dt
            else:
                if line_idx < len(boot_lines):
                    tag, msg, col, delay = boot_lines[line_idx]
                    full_text = f"{tag}  {msg}" if tag else msg
                    if full_text == "":
                        typed_lines.append((tag, msg, col))
                        char_progress = 0
                        line_idx += 1
                        pause_t = delay
                    else:
                        char_progress += type_speed * dt
                        if char_progress >= len(full_text):
                            typed_lines.append((tag, msg, col))
                            char_progress = 0
                            line_idx += 1
                            pause_t = delay
                else:
                    boot_complete = True
        else:
            final_pause += dt
            if final_pause > 1.6:
                return True

        _clear_terminal(scr, W, H, elapsed, dt)

        log_x = 20
        log_y_start = 16
        line_h = 18
        max_visible = (H - log_y_start - 30) // line_h

        currently_typing = None
        if not boot_complete and line_idx < len(boot_lines) and pause_t <= 0:
            tag, msg, col, _ = boot_lines[line_idx]
            full_text = f"{tag}  {msg}" if tag else msg
            if full_text != "":
                partial = full_text[:int(char_progress)]
                currently_typing = (partial, col, tag != "")

        total_lines = len(typed_lines) + (1 if currently_typing else 0)
        first_visible = max(0, total_lines - max_visible)
        visible_typed = typed_lines[first_visible: first_visible + max_visible]

        for i, (tag, msg, col) in enumerate(visible_typed):
            ly = log_y_start + i * line_h
            if tag:
                _term_text(scr, f_termb, tag, log_x, ly, col)
                _term_text(scr, f_term, msg, log_x + 90, ly, AMBER)
            elif msg:
                _term_text(scr, f_term, msg, log_x, ly, col)

        if currently_typing:
            partial, col, is_tagged = currently_typing
            ty_idx = min(max_visible - 1, len(visible_typed))
            ly = log_y_start + ty_idx * line_h
            if is_tagged and "  " in partial:
                tag_part = partial.split("  ", 1)[0]
                msg_part = partial[len(tag_part) + 2:]
                _term_text(scr, f_termb, tag_part, log_x, ly, col)
                msw = _term_text(scr, f_term, msg_part, log_x + 90, ly, AMBER)
                cur_x = log_x + 90 + msw
            else:
                tw = _term_text(scr, f_term, partial, log_x, ly, col if not is_tagged else AMBER)
                cur_x = log_x + tw
            _draw_cursor(scr, cur_x + 2, ly, f_term, col, cursor_t)
        elif boot_complete:
            ly = log_y_start + min(max_visible - 1, len(visible_typed)) * line_h
            _term_text(scr, f_term, "$", log_x, ly, AMBER_HOT)
            _draw_cursor(scr, log_x + 18, ly, f_term, AMBER_HOT, cursor_t)

        progress = min(1.0, line_idx / len(boot_lines))
        if not boot_complete:
            prog_str = f"booting... [{int(progress * 100):3d}%]"
        else:
            prog_str = "ready."
        prog_col = AMBER_DIM if not boot_complete else GREEN_OK
        ps = f_term.render(prog_str, True, prog_col)
        scr.blit(ps, (W - ps.get_width() - 20, H - 28))

        pygame.display.flip()



ASCII_TITLE = [
    " ___ _   _ ____  _   _ ____ _____ ____  ___    _    _     ",
    "|_ _| \\ | |  _ \\| | | / ___|_   _|  _ \\|_ _|  / \\  | |    ",
    " | ||  \\| | | | | | | \\___ \\ | | | |_) || |  / _ \\ | |    ",
    " | || |\\  | |_| | |_| |___) || | |  _ < | | / ___ \\| |___ ",
    "|___|_| \\_|____/ \\___/|____/ |_| |_| \\_\\___/_/   \\_\\_____|",
    "",
    "    ____    _    ____ ___ _____  _    _     ___ ____ _____ ",
    "   / ___|  / \\  |  _ \\_ _|_   _|/ \\  | |   |_ _/ ___|_   _|",
    "  | |     / _ \\ | |_) | |  | | / _ \\ | |    | |\\___ \\ | |  ",
    "  | |___ / ___ \\|  __/| |  | |/ ___ \\| |___ | | ___) || |  ",
    "   \\____/_/   \\_\\_|  |___| |_/_/   \\_\\_____|___|____/ |_|  ",
]


def run_main_menu(scr, clk):
    W, H = scr.get_size()

    f_title = pygame.font.SysFont("consolas,couriernew,monospace", 13, bold=True)
    f_term  = pygame.font.SysFont("consolas,couriernew,monospace", 16)
    f_termb = pygame.font.SysFont("consolas,couriernew,monospace", 16, bold=True)
    f_input = pygame.font.SysFont("consolas,couriernew,monospace", 18, bold=True)
    f_small = pygame.font.SysFont("consolas,couriernew,monospace", 13)
    f_tiny  = pygame.font.SysFont("consolas,couriernew,monospace", 11)

    fade_in = 0.0
    typed = ""
    history = []
    error_msg = None
    error_t = 0.0
    transition_out = 0.0
    transition_target = None
    cursor_t = 0.0
    t0 = time.time()
    last_t = t0

    PLAY_CMDS = {"play", "p", "1", "start", "new"}
    QUIT_CMDS = {"quit", "q", "2", "exit", "bye"}

    while True:
        now = time.time()
        dt = now - last_t
        last_t = now
        elapsed = now - t0
        cursor_t += dt
        clk.tick(60)
        fade_in = min(1.0, fade_in + dt / 0.6)

        if transition_target is not None:
            transition_out = min(1.0, transition_out + dt / 0.5)
            if transition_out >= 1.0:
                return transition_target

        if transition_target is None:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return "quit"
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        cmd = typed.strip().lower()
                        if cmd in PLAY_CMDS:
                            play_button_sfx()
                            history.append((typed, None))
                            transition_target = "play"
                            typed = ""
                        elif cmd in QUIT_CMDS:
                            play_error_sfx()
                            history.append((typed, None))
                            return "quit"
                        elif cmd == "":
                            pass
                        else:
                            error_msg = f"command not found: {typed}"
                            error_t = elapsed
                            history.append((typed, f"command not found: {typed}"))
                            typed = ""
                            history = history[-6:]
                    elif ev.key == pygame.K_BACKSPACE:
                        typed = typed[:-1]
                    elif ev.key == pygame.K_ESCAPE:
                        typed = ""
                    else:
                        if ev.unicode and ev.unicode.isprintable() and len(typed) < 24:
                            typed += ev.unicode
        else:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return "quit"

        _clear_terminal(scr, W, H, elapsed, dt)

        status = f"{_shell_prompt()} ./industrial_capitalist --version 6.0(BETA)"
        _term_text(scr, f_tiny, status, 20, 14, AMBER_DIM)
        t_str = time.strftime("%H:%M:%S")
        ts = f_tiny.render(t_str, True, AMBER_DIM)
        scr.blit(ts, (W - ts.get_width() - 20, 14))

        title_y = 60
        for i, line in enumerate(ASCII_TITLE):
            col = AMBER_HOT if i < 5 else AMBER
            ts_ = f_title.render(line, True, col)
            scr.blit(ts_, (W // 2 - ts_.get_width() // 2, title_y + i * 16))

        tagline_y = title_y + len(ASCII_TITLE) * 16 + 12
        ts_ = f_term.render("build  ::  produce  ::  profit", True, AMBER_DIM)
        scr.blit(ts_, (W // 2 - ts_.get_width() // 2, tagline_y))

        sep_y = tagline_y + 26
        ds = f_term.render("-" * 60, True, AMBER_LOW)
        scr.blit(ds, (W // 2 - ds.get_width() // 2, sep_y))

        cmd_y = sep_y + 24
        prompt_x = W // 2 - 280

        _term_text(scr, f_term, "> available commands:", prompt_x, cmd_y, AMBER_DIM)

        entries = [
            ("play",    "start or continue a factory"),
            ("quit",    "exit the simulation"),
        ]
        for i, (c, desc) in enumerate(entries):
            ly = cmd_y + 26 + i * 22
            _term_text(scr, f_termb, f"    {c:<6}", prompt_x, ly, AMBER_HOT)
            _term_text(scr, f_term, f"- {desc}", prompt_x + 80, ly, AMBER_DIM)

        hist_y = cmd_y + 26 + len(entries) * 22 + 20
        for i, (cmd_str, err) in enumerate(history[-4:]):
            line_y = hist_y + i * 36
            _term_text(scr, f_term, f"$ {cmd_str}", prompt_x, line_y, AMBER)
            if err == "help":
                msg = "  commands: play, quit"
                msg_col = AMBER_DIM
            elif err:
                msg = f"  {err}"
                msg_col = RED_HOT
            else:
                msg = "  ..."
                msg_col = AMBER_LOW
            _term_text(scr, f_term, msg, prompt_x, line_y + 16, msg_col)

        prompt_y = H - 130
        prefix = _shell_prompt()
        ps = f_input.render(prefix, True, AMBER_HOT)
        scr.blit(ps, (prompt_x, prompt_y))
        ts_typed = f_input.render(typed, True, WHITE)
        scr.blit(ts_typed, (prompt_x + ps.get_width(), prompt_y))
        cur_x = prompt_x + ps.get_width() + ts_typed.get_width()
        if _blink(cursor_t, 2.0):
            pygame.draw.rect(scr, AMBER_HOT,
                             (cur_x + 2, prompt_y + 4, 10, f_input.get_height() - 8))

        hint_y = prompt_y + 36
        hint_str = ""
        ts_ = f_tiny.render(hint_str, True, AMBER_LOW)
        scr.blit(ts_, (prompt_x, hint_y))

        _term_text(scr, f_small, "V6.0 (BETA)", 20, H - 36, AMBER_DIM)

        if transition_out > 0:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            wipe_h = int(H * transition_out)
            for y in range(0, wipe_h, 3):
                pygame.draw.line(overlay, (*AMBER, 180), (0, y), (W, y), 1)
            scr.blit(overlay, (0, 0))

        if fade_in < 1.0:
            fade = pygame.Surface((W, H), pygame.SRCALPHA)
            fade.fill((0, 0, 0, int(255 * (1 - fade_in))))
            scr.blit(fade, (0, 0))

        pygame.display.flip()



PANIC_LINES = [
    ("[ ERR ]", "Connection to grid LOST.", 0.10),
    ("[FAULT]", "kernel: power_subsystem stalled at PC=0xDEADBEEF", 0.06),
    ("[FAULT]", "kernel: market_feed: SIGTERM received", 0.06),
    ("[FAULT]", "kernel: NULL pointer dereference at 0x00000000", 0.06),
    ("[ ERR ]", "Unable to flush /var/log/sim.log: I/O error", 0.06),
    ("[ ERR ]", "Pollution sensor offline.", 0.06),
    ("[ ERR ]", "Workforce: dispersed.", 0.06),
    ("[ ERR ]", "Investors: notified.", 0.08),
    ("",        "", 0.08),
    ("",        "*** KERNEL PANIC: not syncing: SHUTDOWN INITIATED", 0.30),
    ("",        "*** SYSTEM HALTED ***", 0.40),
]


def run_quit_panic(scr, clk):
    W, H = scr.get_size()
    play_quit_sfx()

    f_term  = pygame.font.SysFont("consolas,couriernew,monospace", 15)
    f_termb = pygame.font.SysFont("consolas,couriernew,monospace", 15, bold=True)
    f_big   = pygame.font.SysFont("consolas,couriernew,monospace", 28, bold=True)
    f_tiny  = pygame.font.SysFont("consolas,couriernew,monospace", 11)

    phase = 0
    phase_t = 0.0
    typed_lines = []
    line_idx = 0
    pause_t = 0.0
    char_progress = 0
    halt_fade = 0.0
    t0 = time.time()
    last_t = t0
    SHAKE_AMP = 5.0
    DURATION_TOTAL = 4.5

    while True:
        now = time.time()
        dt = now - last_t
        last_t = now
        elapsed = now - t0
        phase_t += dt
        clk.tick(60)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if (ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN) and elapsed > 0.8:
                return

        if elapsed > DURATION_TOTAL:
            return

        shake_decay = max(0.0, 1.0 - elapsed / 3.0)
        shake_x = random.uniform(-SHAKE_AMP, SHAKE_AMP) * shake_decay
        shake_y = random.uniform(-SHAKE_AMP, SHAKE_AMP) * shake_decay

        temp = pygame.Surface((W, H))
        temp.fill((15, 4, 4))

        if phase == 0:
            if phase_t < 0.5:
                strobe = (math.sin(phase_t * 38) + 1) / 2
                flash = pygame.Surface((W, H), pygame.SRCALPHA)
                flash.fill((255, 30, 25, int(160 * strobe)))
                temp.blit(flash, (0, 0))
            else:
                phase = 1
                phase_t = 0.0

        if phase == 1:
            if pause_t > 0:
                pause_t -= dt
            elif line_idx < len(PANIC_LINES):
                tag, msg, delay = PANIC_LINES[line_idx]
                full = f"{tag}  {msg}" if tag else msg
                char_progress += 200 * dt
                if char_progress >= len(full):
                    typed_lines.append((tag, msg))
                    char_progress = 0
                    line_idx += 1
                    pause_t = delay
            else:
                phase = 2
                phase_t = 0.0

        if phase >= 1:
            blink = _blink(elapsed, 4)
            bt_col = RED_HOT if blink else WHITE
            bs = f_termb.render("*** SYSTEM FAULT — ABNORMAL TERMINATION REQUESTED ***",
                                True, bt_col)
            temp.blit(bs, (W // 2 - bs.get_width() // 2, 20))

        log_x = 30
        log_y_start = 60
        line_h = 22
        for i, (tag, msg) in enumerate(typed_lines):
            ly = log_y_start + i * line_h
            if tag:
                col = RED_HOT if tag.strip() in ("[ERR]", "[ ERR ]", "[FAULT]") else AMBER_HOT
                temp.blit(f_termb.render(tag, True, col), (log_x, ly))
                msg_col = RED_HOT if ("kernel" in msg.lower() or "PANIC" in msg) else WHITE
                temp.blit(f_term.render(msg, True, msg_col), (log_x + 90, ly))
            elif msg:
                temp.blit(f_termb.render(msg, True, RED_HOT), (log_x, ly))

        if phase == 1 and line_idx < len(PANIC_LINES) and pause_t <= 0:
            tag, msg, _ = PANIC_LINES[line_idx]
            full = f"{tag}  {msg}" if tag else msg
            partial = full[:int(char_progress)]
            ly = log_y_start + len(typed_lines) * line_h
            ts = f_term.render(partial, True, RED_HOT)
            temp.blit(ts, (log_x, ly))
            if _blink(elapsed, 2.5):
                pygame.draw.rect(temp, RED_HOT,
                                 (log_x + ts.get_width() + 2, ly + 3, 8, f_term.get_height() - 6))

        if phase == 2:
            halt_fade = min(1.0, halt_fade + dt / 0.6)
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((180, 20, 20, int(120 * halt_fade)))
            temp.blit(ov, (0, 0))
            ht = f_big.render("[ SYSTEM HALTED ]", True, RED_HOT)
            ht.set_alpha(int(255 * halt_fade))
            scale = 1.0 + 0.04 * math.sin(elapsed * 6)
            sw, sh = int(ht.get_width() * scale), int(ht.get_height() * scale)
            ht_s = pygame.transform.scale(ht, (sw, sh))
            temp.blit(ht_s, (W // 2 - sw // 2, H // 2 - sh // 2))
            sub = f_term.render("press any key to terminate", True, WHITE)
            sub.set_alpha(int(255 * halt_fade * (0.5 + 0.5 * math.sin(elapsed * 3))))
            temp.blit(sub, (W // 2 - sub.get_width() // 2, H // 2 + 40))
            if phase_t > 1.5:
                end_fade = min(1.0, (phase_t - 1.5) / 0.6)
                bk = pygame.Surface((W, H), pygame.SRCALPHA)
                bk.fill((0, 0, 0, int(255 * end_fade)))
                temp.blit(bk, (0, 0))
                if end_fade >= 1.0:
                    return

        scr.fill((0, 0, 0))
        scr.blit(temp, (int(shake_x), int(shake_y)))

        if random.random() < 0.3:
            gy = random.randint(0, H - 1)
            gh = random.randint(1, 5)
            gs = pygame.Surface((W, gh), pygame.SRCALPHA)
            gs.fill((255, 60, 50, 100))
            scr.blit(gs, (random.randint(-20, 20), gy))

        pygame.display.flip()



def run_company_name_entry(scr, clk):
    W, H = scr.get_size()

    f_term  = pygame.font.SysFont("consolas,couriernew,monospace", 16)
    f_termb = pygame.font.SysFont("consolas,couriernew,monospace", 16, bold=True)
    f_input = pygame.font.SysFont("consolas,couriernew,monospace", 22, bold=True)
    f_tiny  = pygame.font.SysFont("consolas,couriernew,monospace", 11)

    name = ""
    max_len = 22
    fade_in = 0.0
    cursor_t = 0.0
    t0 = time.time()
    last_t = t0

    while True:
        now = time.time()
        dt = now - last_t
        last_t = now
        elapsed = now - t0
        cursor_t += dt
        fade_in = min(1.0, fade_in + dt / 0.4)
        clk.tick(60)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return None
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE: return None
                elif ev.key == pygame.K_RETURN:
                    if name.strip():
                        play_button_sfx()
                        return name.strip().upper()
                elif ev.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if ev.unicode and ev.unicode.isprintable() and len(name) < max_len:
                        name += ev.unicode

        _clear_terminal(scr, W, H, elapsed, dt)

        _term_text(scr, f_tiny, f"{_shell_prompt()} register_company --new", 20, 14, AMBER_DIM)

        x = 60
        y = 80
        lines = [
            ("[ COMPANY REGISTRATION ]", AMBER_HOT, f_termb),
            ("", AMBER, f_term),
            ("> a new corporation must be registered before deployment.", AMBER, f_term),
            ("> choose a name. it will appear in market reports and", AMBER_DIM, f_term),
            ("  news headlines across the simulation.", AMBER_DIM, f_term),
            ("", AMBER, f_term),
            ("> name must be 1-22 characters.", AMBER_DIM, f_term),
            ("", AMBER, f_term),
            (f"{_shell_prompt()} enter_company_name", AMBER, f_term),
            ("", AMBER, f_term),
        ]
        for ln, col, fn in lines:
            _term_text(scr, fn, ln, x, y, col)
            y += fn.get_height() + 4

        prompt = "> "
        ps = f_input.render(prompt, True, AMBER_HOT)
        scr.blit(ps, (x, y))
        prompt_w = ps.get_width()

        ns = f_input.render(name.upper(), True, WHITE)
        scr.blit(ns, (x + prompt_w, y))
        cur_x = x + prompt_w + ns.get_width()
        if _blink(cursor_t):
            pygame.draw.rect(scr, AMBER_HOT, (cur_x + 2, y + 4, 12, f_input.get_height() - 8))

        cc_str = f"[{len(name):02d}/{max_len:02d}]"
        scr.blit(f_tiny.render(cc_str, True, AMBER_LOW), (x, y + f_input.get_height() + 8))

        y_stat = y + f_input.get_height() + 36
        if name.strip():
            stat_str = "  [READY]  press [ENTER] to register"
            stat_col = GREEN_OK
        else:
            stat_str = "  [WAITING]  type a name to continue"
            stat_col = AMBER_DIM
        _term_text(scr, f_term, stat_str, x, y_stat, stat_col)

        _term_text(scr, f_tiny, "[ESC] cancel registration",
                   x, H - 30, AMBER_LOW)

        if fade_in < 1.0:
            fade = pygame.Surface((W, H), pygame.SRCALPHA)
            fade.fill((0, 0, 0, int(255 * (1 - fade_in))))
            scr.blit(fade, (0, 0))

        pygame.display.flip()



def run_save_select(scr, clk):
    W, H = scr.get_size()

    f_termb = pygame.font.SysFont("consolas,couriernew,monospace", 16, bold=True)
    f_term  = pygame.font.SysFont("consolas,couriernew,monospace", 15)
    f_tiny  = pygame.font.SysFont("consolas,couriernew,monospace", 11)

    confirm_delete = None
    fade_in = 0.0
    selected = 0
    t0 = time.time()
    last_t = t0

    while True:
        now = time.time()
        dt = now - last_t
        last_t = now
        elapsed = now - t0
        clk.tick(60)
        mx, my = pygame.mouse.get_pos()
        fade_in = min(1.0, fade_in + dt / 0.3)

        row_y_start = 130
        row_h = 60
        row_rects = {}
        action_rects = {}
        for sl in range(1, SAVE_SLOTS + 1):
            ry = row_y_start + (sl - 1) * row_h
            row_rects[sl] = pygame.Rect(20, ry, W - 40, row_h - 6)
            info = _slot_info(sl)
            if info is not None:
                play_zone = pygame.Rect(W - 280, ry + 14, 80, 26)
                del_zone  = pygame.Rect(W - 180, ry + 14, 100, 26)
                action_rects[sl] = (play_zone, del_zone)

        back_y = H - 50
        back_rect = pygame.Rect(20, back_y, 100, 30)

        yes_rect = pygame.Rect(W // 2 - 100, H // 2 + 30, 80, 30)
        no_rect  = pygame.Rect(W // 2 + 20,  H // 2 + 30, 80, 30)

        for sl in range(1, SAVE_SLOTS + 1):
            if row_rects[sl].collidepoint(mx, my):
                selected = sl - 1

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: return None
            if ev.type == pygame.KEYDOWN:
                if confirm_delete is not None:
                    if ev.key == pygame.K_y:
                        play_quit_sfx()
                        _delete_slot(confirm_delete)
                        confirm_delete = None
                    elif ev.key in (pygame.K_n, pygame.K_ESCAPE):
                        play_button_sfx()
                        confirm_delete = None
                    continue
                if ev.key == pygame.K_ESCAPE:
                    return None
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % SAVE_SLOTS
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % SAVE_SLOTS
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sl = selected + 1
                    info = _slot_info(sl)
                    play_button_sfx()
                    return (sl, info is None)
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if confirm_delete is not None:
                    if yes_rect.collidepoint(mx, my):
                        play_quit_sfx()
                        _delete_slot(confirm_delete)
                        confirm_delete = None
                    elif no_rect.collidepoint(mx, my):
                        play_button_sfx()
                        confirm_delete = None
                    continue
                if back_rect.collidepoint(mx, my):
                    play_quit_sfx()
                    return None
                for sl in range(1, SAVE_SLOTS + 1):
                    info = _slot_info(sl)
                    if info is not None and sl in action_rects:
                        play_zone, del_zone = action_rects[sl]
                        if play_zone.collidepoint(mx, my):
                            play_button_sfx()
                            return (sl, False)
                        if del_zone.collidepoint(mx, my):
                            play_button_sfx()
                            confirm_delete = sl
                            break
                    elif row_rects[sl].collidepoint(mx, my):
                        play_button_sfx()
                        return (sl, info is None)

        _clear_terminal(scr, W, H, elapsed, dt)

        _term_text(scr, f_tiny, f"{_shell_prompt()} ls -la ./saves/", 20, 14, AMBER_DIM)
        t_str = time.strftime("%H:%M:%S")
        ts = f_tiny.render(t_str, True, AMBER_DIM)
        scr.blit(ts, (W - ts.get_width() - 20, 14))

        _term_text(scr, f_termb, "[ SAVE SLOTS ]", 20, 50, AMBER_HOT)
        _term_text(scr, f_term, f"{SAVE_SLOTS} slot(s) available  /  click to select",
                   20, 76, AMBER_DIM)

        col_y = 110
        _term_text(scr, f_tiny, "   #   COMPANY                       CAPITAL          LAST PLAYED              ACTIONS",
                   20, col_y, AMBER_LOW)
        pygame.draw.line(scr, AMBER_LOW, (20, col_y + 14), (W - 20, col_y + 14), 1)

        for sl in range(1, SAVE_SLOTS + 1):
            ry = row_y_start + (sl - 1) * row_h
            info = _slot_info(sl)
            is_selected = (selected == sl - 1)

            arrow = "> " if is_selected else "  "
            row_col = AMBER_HOT if is_selected else AMBER

            slot_str = f"{arrow}[{sl:02d}]"
            _term_text(scr, f_term, slot_str, 20, ry + 14, row_col)

            if info is None:
                empty_col = AMBER_HOT if is_selected else AMBER_DIM
                _term_text(scr, f_term, "<empty>  -- click to create new save",
                           110, ry + 14, empty_col)
                plus_col = AMBER_HOT if is_selected else AMBER_LOW
                _term_text(scr, f_termb, "[ + new ]", W - 130, ry + 14, plus_col)
            else:
                co = info.get("company", "UNNAMED CO.").upper()
                if len(co) > 24: co = co[:23] + "…"
                _term_text(scr, f_term, co, 110, ry + 14, row_col)

                ms_v = f"${info['money']:,.0f}" if isinstance(info['money'], (int, float)) else "$0"
                _term_text(scr, f_term, ms_v, 360, ry + 14, GREEN_OK if is_selected else GREEN_DIM)

                _term_text(scr, f_term, info["modified"], 510, ry + 14,
                           AMBER if is_selected else AMBER_DIM)

                play_zone, del_zone = action_rects[sl]
                play_hov = play_zone.collidepoint(mx, my)
                del_hov  = del_zone.collidepoint(mx, my)

                play_col = AMBER_HOT if play_hov else (AMBER if is_selected else AMBER_DIM)
                del_col  = RED_HOT   if del_hov  else (RED_DIM if is_selected else AMBER_LOW)

                _term_text(scr, f_termb, "[load]", play_zone.x, ry + 14, play_col)
                _term_text(scr, f_termb, "[delete]", del_zone.x, ry + 14, del_col)

            if sl < SAVE_SLOTS:
                pygame.draw.line(scr, (35, 25, 10),
                                 (20, ry + row_h - 6), (W - 20, ry + row_h - 6), 1)

        hint_y = row_y_start + SAVE_SLOTS * row_h + 20
        _term_text(scr, f_tiny,
                   "",
                   20, hint_y, AMBER_LOW)

        back_hov = back_rect.collidepoint(mx, my)
        bk_str = "< back"
        bk_col = AMBER_HOT if back_hov else AMBER_DIM
        _term_text(scr, f_term, bk_str, 20, back_y + 8, bk_col)

        if confirm_delete is not None:
            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 210))
            scr.blit(ov, (0, 0))

            cy = H // 2 - 50
            warn = "!!! WARNING — destructive operation !!!"
            ws = f_termb.render(warn, True, RED_HOT if _blink(elapsed, 3) else AMBER_HOT)
            scr.blit(ws, (W // 2 - ws.get_width() // 2, cy))

            ds = f_term.render(f"# rm -rf /saves/slot_{confirm_delete}/", True, RED_HOT)
            scr.blit(ds, (W // 2 - ds.get_width() // 2, cy + 30))

            us = f_term.render("this action cannot be undone.", True, AMBER_DIM)
            scr.blit(us, (W // 2 - us.get_width() // 2, cy + 56))

            yes_hov = yes_rect.collidepoint(mx, my)
            no_hov  = no_rect.collidepoint(mx, my)
            yes_col = RED_HOT if yes_hov else RED_DIM
            no_col  = AMBER_HOT if no_hov else AMBER
            ys = f_termb.render("[y] delete", True, yes_col)
            ns = f_termb.render("[n] cancel", True, no_col)
            scr.blit(ys, (W // 2 - 100, cy + 100))
            scr.blit(ns, (W // 2 + 20,  cy + 100))

        if fade_in < 1.0:
            fade = pygame.Surface((W, H), pygame.SRCALPHA)
            fade.fill((0, 0, 0, int(255 * (1 - fade_in))))
            scr.blit(fade, (0, 0))

        pygame.display.flip()



STORY_PAGES = [
    {"header": "/var/log/personal/chapter_01.txt", "title": "SIX MONTHS AGO",
     "lines": ["You were a production engineer at MegaCorp Industries —",
               "the largest manufacturer in the region.", "",
               "The factory floors were inefficient.",
               "Outdated machines choked out pollution.",
               "Waste piled up. Output was falling.", "",
               "You saw what nobody else wanted to see."]},
    {"header": "/var/log/personal/chapter_02.txt", "title": "THE PROPOSAL",
     "lines": ["You spent weeks drafting a plan to modernize everything.",
               "New processing chains. Cleaner energy. Higher throughput.", "",
               "You walked into the boardroom and laid it all out.",
               "Better machines. Less pollution. Triple the output.", "",
               "The numbers were undeniable."]},
    {"header": "/var/log/personal/chapter_03.txt", "title": "THE RESPONSE",
     "lines": ["The board didn't see innovation.",
               "They saw someone making them look incompetent.", "",
               "\"Who does this engineer think they are?\"",
               "\"We've been running things fine for thirty years.\"", "",
               "Three weeks later, you were called into HR."]},
    {"header": "/var/log/personal/chapter_04.txt", "title": "FIRED",
     "lines": ["They handed you a severance package and a handshake.", "",
               "Thirty years of \"running things fine\" had left MegaCorp",
               "drowning in pollution fines and falling profits.", "",
               "But that wasn't your problem anymore.", "",
               "Or was it?"]},
    {"header": "/var/log/personal/chapter_05.txt", "title": "A NEW BEGINNING",
     "lines": ["With your severance, you bought a small plot of land",
               "on the outskirts of town. Empty. Quiet. Full of potential.", "",
               "No board. No bureaucracy. No one telling you no.", "",
               "Just you, your knowledge, and a burning desire",
               "to prove every single one of them wrong."]},
    {"header": "/etc/motd", "title": "YOUR MISSION",
     "lines": ["Build your factory from nothing.",
               "Design efficient production chains.",
               "Keep pollution under control — or pay the price.", "",
               "And one day, surpass MegaCorp's valuation entirely.", "",
               "Welcome to Industrial Capitalist."]},
]


def run_story_intro(scr, clk):
    W, H = scr.get_size()

    f_term   = pygame.font.SysFont("consolas,couriernew,monospace", 17)
    f_termi  = pygame.font.SysFont("consolas,couriernew,monospace", 17, italic=True)
    f_termb  = pygame.font.SysFont("consolas,couriernew,monospace", 17, bold=True)
    f_big    = pygame.font.SysFont("consolas,couriernew,monospace", 24, bold=True)
    f_tiny   = pygame.font.SysFont("consolas,couriernew,monospace", 11)
    f_small  = pygame.font.SysFont("consolas,couriernew,monospace", 13)

    TYPE_SPEED = 60.0
    LINE_PAUSE = 0.18
    BLANK_PAUSE = 0.30

    for page_idx, page in enumerate(STORY_PAGES):
        line_idx = 0
        line_progress = 0.0
        line_pause_t = 0.4
        all_done = False
        page_t = 0.0
        last_t = time.time()

        while True:
            now = time.time()
            dt = now - last_t
            last_t = now
            page_t += dt
            clk.tick(60)

            advance = False
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: return False
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE: return True
                    if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if all_done: advance = True
                        else:
                            line_idx = len(page["lines"])
                            all_done = True
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if all_done: advance = True
                    else:
                        line_idx = len(page["lines"])
                        all_done = True
            if advance: break

            if not all_done:
                if line_pause_t > 0:
                    line_pause_t -= dt
                else:
                    if line_idx < len(page["lines"]):
                        cur_line = page["lines"][line_idx]
                        if cur_line == "":
                            line_pause_t = BLANK_PAUSE
                            line_idx += 1
                            line_progress = 0
                        else:
                            line_progress += TYPE_SPEED * dt
                            if line_progress >= len(cur_line):
                                line_progress = len(cur_line)
                                line_idx += 1
                                line_pause_t = LINE_PAUSE
                    else:
                        all_done = True

            _clear_terminal(scr, W, H, page_t, dt)

            _term_text(scr, f_tiny, f"{_shell_prompt()} cat {page['header']}",
                       20, 14, AMBER_DIM)
            cnt_str = f"chapter {page_idx + 1:02d}/{len(STORY_PAGES):02d}"
            cs = f_tiny.render(cnt_str, True, AMBER_DIM)
            scr.blit(cs, (W - cs.get_width() - 20, 14))

            ti = f_big.render(page["title"], True, AMBER_HOT)
            scr.blit(ti, (60, 60))

            dashes = "-" * (len(page["title"]) + 8)
            ds = f_term.render(dashes, True, AMBER_LOW)
            scr.blit(ds, (60, 96))

            line_h = 28
            body_y = 130
            for i, line in enumerate(page["lines"]):
                if i < line_idx:
                    text = line
                elif i == line_idx and not all_done:
                    text = line[:int(line_progress)]
                else:
                    text = ""
                if text == "" and line == "":
                    continue
                if text == "":
                    continue

                is_quote = line.startswith('"')
                fnt = f_termi if is_quote else f_term
                col = AMBER_HOT if is_quote else WHITE
                surf = fnt.render(text, True, col)
                scr.blit(surf, (60, body_y + i * line_h))

                if i == line_idx and not all_done and _blink(page_t, 2.5):
                    cur_x = 60 + surf.get_width()
                    pygame.draw.rect(scr, AMBER_HOT,
                                     (cur_x + 2, body_y + i * line_h + 2,
                                      10, fnt.get_height() - 6))

            dot_y = H - 60
            dot_total_w = len(STORY_PAGES) * 22
            dot_x_start = W // 2 - dot_total_w // 2
            for i in range(len(STORY_PAGES)):
                dx = dot_x_start + i * 22 + 11
                if i == page_idx:
                    pygame.draw.circle(scr, AMBER_HOT, (dx, dot_y), 5)
                elif i < page_idx:
                    pygame.draw.circle(scr, AMBER, (dx, dot_y), 3)
                else:
                    pygame.draw.circle(scr, AMBER_LOW, (dx, dot_y), 3)

            if all_done:
                pulse = 0.5 + 0.5 * math.sin(page_t * 3)
                col = tuple(int(AMBER_DIM[i] + (AMBER_HOT[i] - AMBER_DIM[i]) * pulse)
                            for i in range(3))
                hint_str = "> press [SPACE] to continue _" if page_idx < len(STORY_PAGES) - 1 \
                           else "> press [SPACE] to begin _"
                hint = f_small.render(hint_str, True, col)
                scr.blit(hint, (W // 2 - hint.get_width() // 2, dot_y + 20))
            else:
                hint = f_tiny.render("[SPACE] skip ahead    [ESC] skip intro", True, AMBER_LOW)
                scr.blit(hint, (W // 2 - hint.get_width() // 2, dot_y + 22))

            pygame.display.flip()

    return True




PLAY_LOAD_LINES = [
    ("[  OK  ]", "Spinning up factory simulation .... v6.0(BETA)", GREEN_OK, 0.06),
    ("[  OK  ]", "Loading world chunks .............. READY", GREEN_OK, 0.06),
    ("[  OK  ]", "Initializing economy model ........ READY", GREEN_OK, 0.06),
    ("[  OK  ]", "Loading save slot manager ......... OK", GREEN_OK, 0.06),
    ("[  OK  ]", "Querying available saves .......... 3 SLOTS", GREEN_OK, 0.10),
    ("",         "", AMBER, 0.05),
    ("",         "$ launching save_select...", AMBER_HOT, 0.40),
]


def run_play_loading(scr, clk):
    W, H = scr.get_size()

    f_term  = pygame.font.SysFont("consolas,couriernew,monospace", 14)
    f_termb = pygame.font.SysFont("consolas,couriernew,monospace", 14, bold=True)
    f_tiny  = pygame.font.SysFont("consolas,couriernew,monospace", 11)

    line_idx = 0
    pause_t = 0.2
    typed = []
    char_progress = 0
    type_speed = 320.0
    done_pause = 0.0
    complete = False
    cursor_t = 0.0
    t0 = time.time()
    last_t = t0

    while True:
        now = time.time()
        dt = now - last_t
        last_t = now
        elapsed = now - t0
        cursor_t += dt
        clk.tick(60)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return

        if not complete:
            if pause_t > 0:
                pause_t -= dt
            else:
                if line_idx < len(PLAY_LOAD_LINES):
                    tag, msg, col, delay = PLAY_LOAD_LINES[line_idx]
                    full = f"{tag}  {msg}" if tag else msg
                    if full == "":
                        typed.append((tag, msg, col))
                        char_progress = 0
                        line_idx += 1
                        pause_t = delay
                    else:
                        char_progress += type_speed * dt
                        if char_progress >= len(full):
                            typed.append((tag, msg, col))
                            char_progress = 0
                            line_idx += 1
                            pause_t = delay
                else:
                    complete = True
        else:
            done_pause += dt
            if done_pause > 0.5:
                return

        _clear_terminal(scr, W, H, elapsed, dt)

        _term_text(scr, f_tiny, f"{_shell_prompt()} ./load_session.sh", 20, 14, AMBER_DIM)
        t_str = time.strftime("%H:%M:%S")
        ts = f_tiny.render(t_str, True, AMBER_DIM)
        scr.blit(ts, (W - ts.get_width() - 20, 14))

        log_x = 20
        log_y_start = 50
        line_h = 20

        for i, (tag, msg, col) in enumerate(typed):
            ly = log_y_start + i * line_h
            if tag:
                _term_text(scr, f_termb, tag, log_x, ly, col)
                _term_text(scr, f_term, msg, log_x + 90, ly, AMBER)
            elif msg:
                _term_text(scr, f_term, msg, log_x, ly, col)

        if not complete and line_idx < len(PLAY_LOAD_LINES) and pause_t <= 0:
            tag, msg, col, _ = PLAY_LOAD_LINES[line_idx]
            full = f"{tag}  {msg}" if tag else msg
            if full != "":
                partial = full[:int(char_progress)]
                ly = log_y_start + len(typed) * line_h
                if tag and "  " in partial:
                    tag_part = partial.split("  ", 1)[0]
                    msg_part = partial[len(tag_part) + 2:]
                    _term_text(scr, f_termb, tag_part, log_x, ly, col)
                    msw = _term_text(scr, f_term, msg_part, log_x + 90, ly, AMBER)
                    cur_x = log_x + 90 + msw
                else:
                    tw = _term_text(scr, f_term, partial, log_x, ly, col if not tag else AMBER)
                    cur_x = log_x + tw
                _draw_cursor(scr, cur_x + 2, ly, f_term, col, cursor_t)

        pygame.display.flip()



def run_menu(scr, clk):
    init_audio()
    if not run_splash(scr, clk):
        return None
    play_music("SFX/Game/game2.wav")
    while True:
        c = run_main_menu(scr, clk)
        if c == "quit":
            stop_music()
            run_quit_panic(scr, clk)
            return None
        run_play_loading(scr, clk)
        r = run_save_select(scr, clk)
        if r is None:
            continue
        slot, is_new = r
        if is_new:
            company = run_company_name_entry(scr, clk)
            if company is None:
                continue
            _save_slot_meta(slot, company)
            if not run_story_intro(scr, clk):
                stop_music()
                return None
        stop_music()
        return r



TUTORIAL_STEPS = [
    {"title": "WELCOME", "lines": ["So you just bought a plot of land.", "Time to build something on it.", "", "This tutorial will walk you through", "the basics step by step.", "Click NEXT when you're ready."]},
    {"title": "MOVING AROUND", "lines": ["Use WASD to move the camera around.", "Scroll wheel zooms in and out.", "", "Try moving around a bit to see", "your empty plot of land."]},
    {"title": "YOUR FIRST MACHINE", "lines": ["Open Build (B) > Extractors tab.", "Click on 'Coal Drill' ($50).", "Then press T to place it somewhere.", "", "Coal Drills dig up coal.", "But it needs power to run!"]},
    {"title": "POWERING UP", "lines": ["Open Build (B) > Power tab.", "Place a Solar Panel ($120) near the drill.", "", "Machines need power from nearby generators.", "Keep them within ~5 tiles."]},
    {"title": "POWER WIRING", "lines": ["Press P to enter POWER MODE.", "", "Click on the power source (solar panel).", "Then click on a machine (the drill).", "This makes a direct power connection.", "", "Press P again to exit power mode."]},
    {"title": "SELLING COAL", "lines": ["Now your drill is making coal but", "you need somewhere to sell it.", "", "Build (B) > Storage > Van Depot ($100).", "Place it adjacent to the drill output", "(visible by pressing Z).", "", "When the depot fills, a truck comes", "and sells everything automatically."]},
    {"title": "MAKING MONEY", "lines": ["Coal sells for $5.22 each.", "Not bad for a start!", "", "Your money is shown at the top left."]},
    {"title": "PROCESSING", "lines": ["Raw stuff is worth way more processed:", "", "  raw_iron ($5) -> furnace -> liquid_iron", "  -> ingot molder -> iron_ingot ($65!)", "", "13x more money per iron."]},
    {"title": "RECIPE BOOK", "lines": ["Press K to open the Recipe Book.", "Every item in the game is listed here.", "", "Click any item to see:", "  - Sell value and RP value", "  - What machines produce it", "  - What recipes use it as input"]},
    {"title": "DELETING", "lines": ["Press X to enter DELETE MODE.", "", "Click a machine to remove it.", "You get 80% of the cost back.", "", "Drag to select multiple at once.", "Press Y to confirm, N to cancel."]},
    {"title": "RESEARCH", "lines": ["You start with a Research Station 1.", "It's $75 in the Utility build tab.", "", "Power it and it generates RP", "(Research Points) over time.", "", "Open the tech tree to spend RP."]},
    {"title": "POLLUTION", "lines": ["Drills and generators produce pollution.", "Check the meter at the top left.", "", "High pollution cuts profits via taxes.", "Research the Scrubber to clean the air."]},
    {"title": "MACHINE MODES", "lines": ["Click a placed machine to see its panel.", "If it has modes, click to switch recipes.", "", "Example: Craft Assembler can make", "concrete, crankshafts, chairs, and more."]},
    {"title": "CONTRACTS", "lines": ["Press C to open Contracts.", "Goals that reward money and RP.", "", "Start with 'First Steps' — sell 20 coal."]},
    {"title": "GOOD LUCK", "lines": ["You know enough to get going now.", "", "Quick reference:", "  B=Build  K=Recipes  C=Contracts", "  P=Power  X=Delete   R=Rotate", "  T=Place  WASD=Move  Scroll=Zoom", "", "Good luck out there!"]},
]


class TutorialOverlay:
    def __init__(self):
        self.active = False
        self.step = 0
        self._fonts_init = False

    def start(self):
        self.active = True
        self.step = 0

    def stop(self):
        self.active = False

    def _init_fonts(self):
        if not self._fonts_init:
            self.f_title = pygame.font.SysFont("consolas,couriernew,monospace", 16, bold=True)
            self.f_body  = pygame.font.SysFont("consolas,couriernew,monospace", 12)
            self.f_btn   = pygame.font.SysFont("consolas,couriernew,monospace", 11, bold=True)
            self.f_label = pygame.font.SysFont("consolas,couriernew,monospace", 10, bold=True)
            self._fonts_init = True

    def _geom(self):
        W, H = pygame.display.get_surface().get_size()
        s = TUTORIAL_STEPS[self.step]
        lc = len(s["lines"])
        pw = 380
        ph = 60 + lc * 18 + 44
        px = W - pw - 16
        py = 50
        return W, H, pw, ph, px, py

    def draw(self, scr):
        if not self.active or self.step >= len(TUTORIAL_STEPS):
            return
        self._init_fonts()
        W, H, pw, ph, px, py = self._geom()
        s = TUTORIAL_STEPS[self.step]
        mx, my = pygame.mouse.get_pos()

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((*BG, 245))
        pygame.draw.rect(panel, AMBER, (0, 0, pw, ph), 1)
        scr.blit(panel, (px, py))

        hdr = self.f_label.render(
            f"[ TUTORIAL  STEP {self.step + 1:02d}/{len(TUTORIAL_STEPS):02d} ]",
            True, AMBER_HOT)
        scr.blit(hdr, (px + 12, py + 8))

        pygame.draw.line(scr, AMBER_LOW, (px + 8, py + 26), (px + pw - 8, py + 26), 1)

        title = self.f_title.render(f"> {s['title']}", True, AMBER_HOT)
        scr.blit(title, (px + 14, py + 32))

        for i, line in enumerate(s["lines"]):
            if line == "":
                continue
            indent = line.startswith("  ")
            col = WHITE if indent else AMBER
            ls = self.f_body.render(line, True, col)
            scr.blit(ls, (px + 14, py + 58 + i * 18))

        by = py + ph - 32
        skip_rect = pygame.Rect(px + 12, by, 56, 22)
        skip_hov = skip_rect.collidepoint(mx, my)
        self._draw_btn(scr, "SKIP", skip_rect, skip_hov, RED_DIM, RED_HOT)

        if self.step > 0:
            back_rect = pygame.Rect(px + pw - 144, by, 64, 22)
            back_hov = back_rect.collidepoint(mx, my)
            self._draw_btn(scr, "< BACK", back_rect, back_hov, AMBER_LOW, AMBER)

        next_rect = pygame.Rect(px + pw - 76, by, 64, 22)
        next_hov = next_rect.collidepoint(mx, my)
        next_lbl = "FINISH" if self.step == len(TUTORIAL_STEPS) - 1 else "NEXT >"
        self._draw_btn(scr, next_lbl, next_rect, next_hov, AMBER, AMBER_HOT)

    def _draw_btn(self, scr, label, rect, hover, base, hot):
        if hover:
            bg = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            bg.fill((*base, 60))
            scr.blit(bg, rect.topleft)
        pygame.draw.rect(scr, hot if hover else base, rect, 1)
        ts = self.f_btn.render(label, True, hot if hover else WHITE)
        scr.blit(ts, (rect.centerx - ts.get_width() // 2,
                      rect.centery - ts.get_height() // 2))

    def handle_click(self, pos):
        if not self.active or self.step >= len(TUTORIAL_STEPS):
            return False
        self._init_fonts()
        W, H, pw, ph, px, py = self._geom()
        mx, my = pos
        by = py + ph - 32

        next_rect = pygame.Rect(px + pw - 76, by, 64, 22)
        if next_rect.collidepoint(mx, my):
            self.step += 1
            if self.step >= len(TUTORIAL_STEPS):
                self.active = False
            return True

        if self.step > 0:
            back_rect = pygame.Rect(px + pw - 144, by, 64, 22)
            if back_rect.collidepoint(mx, my):
                self.step = max(0, self.step - 1)
                return True

        skip_rect = pygame.Rect(px + 12, by, 56, 22)
        if skip_rect.collidepoint(mx, my):
            self.active = False
            return True

        if pygame.Rect(px, py, pw, ph).collidepoint(mx, my):
            return True
        return False