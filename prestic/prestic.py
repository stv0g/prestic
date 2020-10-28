#!/usr/bin/env python3
""" Prestic is a profile manager and task scheduler for restic """

import logging
import os
import shlex
import sys
import time
from argparse import ArgumentParser
from configparser import ConfigParser
from copy import deepcopy
from datetime import datetime, timedelta
from getpass import getpass
from math import floor, ceil
from pathlib import Path, PurePosixPath
from subprocess import Popen, PIPE, STDOUT

try:
    from base64 import b64decode
    from io import BytesIO
    from PIL import Image
    import pystray
except:
    pystray = None

try:
    import keyring
except:
    keyring = None


PROG_NAME = "prestic"
PROG_FOLDER = Path.home().joinpath("." + PROG_NAME)
PROG_ICON = (
    b"iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAC+lBMVEVHcExIQj+FemQSIB8RFRBYLCdaQkBpLTVZTTRMVksfImRGHyFtSDZ8MzVrKStZVVZJQzhWLS+EOz2OP0FpOTE9Ix8hGRVgTUaPN0aNblZziGIzO3WDf32fREWvTE6cRUd9SUp+Q0SeR0ipRUe4Tk+9UFKyS00sLywEBQheNTqYMl9LX20VGkmCd2mSgWtlYVqaQEKvSky9VVeiR0hnWUt7blt2Z1ttZV6pl3C3olaSiE+ok3mWg26LQ0"
    b"TCUVO0TE1kSj+AcV6Je2ZHPTqLOTu0S02qTE18LS+Hd2SZinVeTUSPOz1oJix/enCvpprHsJqgmY1iaGR0MzStV1l8SEllNjd7e3vT1NT6+vv9/v/t7u+enqB8REVCNipqY1xva2bLy8twcHEXEwtdYGMiFhRrb3Pj4+dxcXRSTCrHxsBzcWRZWltiYmRVUUpiWy+/v7ptZDBzajB8czRdWjo1LyROSR8/Liu6qWCvnGMoEhRIGBpdLC+voEvfzGSQdUh3LjB+TD2blUnFs1bZxmCRNThlXTvEs1h1bDXUwV5u"
    b"ZTGQhEG9rVSNgUOCeDrNvFpmXi0AABGTg2GqlIGznYaHdmOqlH2Rf2uklkhcUzV1aE6TgGygkk2vn0yhlUiwolCwgnGQr3THWVvCV1jMWVvLpFzMt2HMw2THVliNfGm2oX+0o2y5qF69qGezn3OynIG9UFKlkXqsmIDBqI66ooi5pHvEua2+tKjPtZjYvJ7HrpG5rZ319vf////HxsW9pZLTuZqtopbe3t/KysrKwrmdinLErJPU0tPv8PB+fn5eXl6Tg3KCdWSRkZCoqKlmWUt5bWCznoe8vLyzsayXlHXc29"
    b"bJuaeGdGXo6Oefm3/q1me/r1SfkkV9cjpyaTyhj26cjkv132z44W57XUXRv1yLfjqJe1OShUrNu1neymLt12nZxV/DsFOpl2mfjmmRgV+4qE/x3Gn/7XP+5m+kl0fk0GT75G6mmFTOvGKdjGG/q3TFsHHLtnHSt6Gym4pGCc3iAAAAn3RSTlMAAggRGxgeKUI/GxQ1Tz91XYl9j18lB06kz8eRE77WyvjO+Pz++u1DJrP29ZF5q1i8/P7YiM/FotT17tDytP3+se3dsPbjuIrn98vMeLP5/NslluvQn2Lf/f77"
    b"wMyHwki4ZAyWM9rIw1PiiYp8MZf9Iqz9/J1mtu/9W2ve/vTexKqH0fVoZ92Nz3dS46Je74M/0qbflfO6lUbUWcmpq+bKfVYgAAADJ0lEQVQ4y2NgwASMTIwMVAKMjAzMDMwsrGxszDAhJnYOTi4om5uHl5ePn0FAUEhYWERUjIFRjJGBUVxCUkqai4FJhomBTUhWTk5egUFRSVlFVU1WhIFNXZRBQ1Nr/gJtHQ1dPX1RA5WFCxctMmRQUTEyWrjYyJjPxNTM3MJyydJly6ysbUxNbO0WL7czWm7PsMhuuf3CxY"
    b"uXSzg4rrBZuWr16tVr1q5b5+Tsorxw8XqjxUAFixavX6/i6ubu4LFh46bNK7esXLdp3WZPL3dhNzWVhYtVGNavX2Sk5O2joeHrt3Wb//YdQLBz17ZdAYEMGkHGwSqGDIbKSiGhfAyMYeG790Ts3bd9//7tBw5G7omKlmFgVHeO8WYQCoqNi2dgYEuIOLR3z+7DG49sOHps96G9x6MSkxg4k8VTGFhFWVKBCgLTIk+cjNpz+NTpFRt2R5w5cXCPLjOTfjIbOFbS+cXEMjL3nD1zPPLw6XPnLxyMvHjpeGRWkkxi"
    b"thg4THOyc5PyLl/Zsyfy4NVT567tv3R9z57d+bEsufz8kGhNMU8sKCy6cWX3lQObdm7evP3CpevHLxWXlMaWCECjpexc+c1bt+/cPb0T6In9+3feu3v3/q0HDyu8KiFWVFU/Wv3w5uOaJ3ee3tt8dNPGp89u1zx/8aC2rrqeHWyHYH1DY1Pzy5uvXt++/+btu2f33z9++eFVU6OIjzsrWAFfCx9La9uDjx8/vXj+/P6dzy++vPz66UU7CwM3KyLx8HS8fPDg4adPH98/efX108MPD752MiMnLrGu7ppXDx8+/P"
    b"rg851XXx9+fXHrRU8BsoKk3r6bXz99/frpy7dnr4HUpw/P+1mRFTAW9JQvffzqy4fv3+6//vDl8dI1P3jQUvCEiWt//vr1++ebN2t+//q5ZYMZet5gnuT/x3/f331H9/39u+/P9snijGJiqCo49DaDkwsQbN95JI4xSYMbLZcETjn1dyoIWE/z+FE+XSAlCT0jzZj5ZqLurFmz4nNbZz+vyWBGl2cQzVs9ewbYbcy9c6YXYMgzsPS/nssBdhljEjO2DM7SPy9DFF0GAMQBYCsctATDAAAAAElFTkSuQmCC"
)


class Profile:
    aliases = {
        "repository": "--repo",
        "limit-download": "--limit-download",
        "limit-upload": "--limit-upload",
        "verbose": "--verbose",
        "repository-file": "env.RESTIC_REPOSITORY_FILE",
        "password": "env.RESTIC_PASSWORD",
        "password-command": "env.RESTIC_PASSWORD_COMMAND",
        "password-file": "env.RESTIC_PASSWORD_FILE",
        "cache-dir": "env.RESTIC_CACHE_DIR",
        "key-hint": "env.RESTIC_KEY_HINT",
        "progress-fps": "env.RESTIC_PROGRESS_FPS",
        "aws-access-key-id": "env.AWS_ACCESS_KEY_ID",
        "aws-secret-access-key": "env.AWS_SECRET_ACCESS_KEY",
        "aws-default-region": "env.AWS_DEFAULT_REGION",
        "st-auth": "env.ST_AUTH",
        "st-user": "env.ST_USER",
        "st-key": "env.ST_KEY",
        "os-auth-url": "env.OS_AUTH_URL",
        "os-region-name": "env.OS_REGION_NAME",
        "os-username": "env.OS_USERNAME",
        "os-password": "env.OS_PASSWORD",
        "os-tenant-id": "env.OS_TENANT_ID",
        "os-tenant-name": "env.OS_TENANT_NAME",
        "os-user-domain-name": "env.OS_USER_DOMAIN_NAME",
        "os-project-name": "env.OS_PROJECT_NAME",
        "os-project-domain-name": "env.OS_PROJECT_DOMAIN_NAME",
        "os-application-credential-id": "env.OS_APPLICATION_CREDENTIAL_ID",
        "os-application-credential-name": "env.OS_APPLICATION_CREDENTIAL_NAME",
        "os-application-credential-secret": "env.OS_APPLICATION_CREDENTIAL_SECRET",
        "os-storage-url": "env.OS_STORAGE_URL",
        "os-auth-token": "env.OS_AUTH_TOKEN",
        "b2-account-id": "env.B2_ACCOUNT_ID",
        "b2-account-key": "env.B2_ACCOUNT_KEY",
        "azure-account-name": "env.AZURE_ACCOUNT_NAME",
        "azure-account-key": "env.AZURE_ACCOUNT_KEY",
        "google-project-id": "env.GOOGLE_PROJECT_ID",
        "google-application-credentials": "env.GOOGLE_APPLICATION_CREDENTIALS",
        "rclone-bwlimit": "env.RCLONE_BWLIMIT",
    }

    def __init__(self, name, properties={}):
        self._properties = {
            "name": name,
            "description": "no description",
            "inherit": [],
            "command": [],
            "args": [],
            "flags": [],
            "wait-for-lock": "0",
            "cpu-priority": "",
            "io-priority": "",
            "schedule": "",
            "restic-path": "restic",
            "global-flags": [],
        }

        self._defined = set({"name"})
        self._parents = []

        self.last_run = None
        self.next_run = None

        for key in properties:
            self[key] = properties[key]

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, key):
        return self._properties.get(self.aliases.get(key, key))

    def __setitem__(self, key, value):
        key = self.aliases.get(key, key)
        if type(self[key]) is list and type(value) is not list:
            value = shlex.split(value)
        self._properties[key] = value
        self._defined.add(key)
        if key == "schedule":
            self.next_run = self.find_next_run()

    def is_defined(self, key):
        return self.aliases.get(key, key) in self._defined

    def inherit(self, profile):
        for key, value in profile._properties.items():
            if not self.is_defined(key) and profile.is_defined(key):
                self[key] = deepcopy(value)
        self._parents.append([profile.name, profile._parents])

    def find_next_run(self, from_time=None):
        weekdays = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

        from_time = (from_time or datetime.now()) + timedelta(minutes=1)
        next_run = from_time.replace(hour=0, minute=0, second=0)

        m_days = set(range(1, 32))
        w_days = set()

        if self.schedule:
            for part in self.schedule.lower().replace(",", " ").split():
                if part == "monthly":
                    m_days = {1}
                elif part == "weekly":
                    w_days = {0}
                elif part[0:3] in weekdays:
                    w_days.add(weekdays.index(part[0:3]))
                elif len(part.split(":")) == 2:
                    hour, minute = part.split(":")
                    hour = from_time.hour + 1 if hour == "*" else int(hour)
                    next_run = next_run.replace(hour=int(hour), minute=int(minute))

            for i in range(from_time.weekday(), from_time.weekday() + 32):
                if next_run.day in m_days and ((i % 7) in w_days or not w_days):
                    if next_run >= from_time:
                        return next_run
                next_run += timedelta(days=1)

        return None

    def is_pending(self):
        return self.next_run and self.next_run <= datetime.now()

    def is_runnable(self):
        return self.command and (self["repository"] or self["repository-file"])

    def get_command(self, cmd_args=[]):
        args = [self["restic-path"]] + self["global-flags"]
        env = {}

        if self["password-keyring"]:
            username = shlex.quote(self["password-keyring"])
            python = shlex.quote(sys.executable)
            env["RESTIC_PASSWORD_COMMAND"] = f"{python} -m keyring get {PROG_NAME} {username}"
            if not keyring:
                logging.warning(f"keyring module missing, required by profile {self.name}")

        for key, value in self._properties.items():
            if value != None:
                if key.startswith("env."):
                    env[key[4:]] = str(value)
                elif key.startswith("-"):
                    args += [key, str(value)]

        # Ignore default command if any argument was given
        if cmd_args:
            args += cmd_args
        elif self.command:
            args += self.command
            args += self.args
            args += self.flags

        return env, args

    def run(self, cmd_args=[], text_output=True, stdout=None, stderr=None):
        env, args = self.get_command(cmd_args)

        p_args = {"args": args, "env": {**os.environ, **env}, "stdout": stdout, "stderr": stderr}

        if text_output:
            p_args["universal_newlines"] = True
            p_args["errors"] = "replace"
            p_args["bufsize"] = 1

        if sys.platform == "win32":
            cpu_priorities = {"idle": 0x0040, "low": 0x4000, "normal": 0x0020, "high": 0x0080}
            p_args["creationflags"] = cpu_priorities.get(self["cpu-priority"], 0)
            # do not create a window/console if we capture ALL output
            if stdout != None or stderr != None:
                p_args["creationflags"] |= 0x08000000  # CREATE_NO_WINDOW

        self.last_run = datetime.now()
        self.next_run = self.find_next_run(self.last_run)

        logging.info(f"running: {' '.join(shlex.quote(s) for s in args)}\n")

        proc_handle = Popen(**p_args)

        if self["wait-for-lock"]:
            pass

        return proc_handle


class BaseHandler:
    def __init__(self, base_path=PROG_FOLDER):
        self.base_path = Path(base_path)
        self.running = False

        if not (self.base_path.is_file() or self.base_path.suffix == ".ini"):
            self.base_path.joinpath("logs").mkdir(parents=True, exist_ok=True)
            self.base_path.joinpath("cache").mkdir(parents=True, exist_ok=True)

        self.load_config()

    def load_config(self):
        config = ConfigParser()
        status = ConfigParser()
        config.optionxform = lambda x: str(x) if x.startswith("env.") else x.lower()

        if config.read(self.base_path):
            logging.info(f"configuration loaded from file {self.base_path}")
        elif config.read(self.base_path.joinpath("config.ini")):
            logging.info(f"configuration loaded from folder {self.base_path}")
            status.read(self.base_path.joinpath("status.ini"))

        self.profiles = {
            "default": Profile("default"),
            **{k: Profile(k, dict(config[k])) for k in config.sections()},
        }

        # Process profile inheritance
        inherits = True
        while inherits:
            inherits = False
            for name, profile in self.profiles.items():
                if not profile["inherit"]:
                    continue

                inherits = True

                parent_name = profile["inherit"][0]
                parent = self.profiles.get(parent_name)

                if not parent:
                    exit(f"[error] profile {name} inherits non-existing parent {parent_name}")
                elif parent_name == profile.name:
                    exit(f"[error] profile {name} cannot inherit from itself")
                elif parent["inherit"]:
                    continue

                profile.inherit(parent)
                profile["inherit"].pop(0)

        self.tasks = [t for t in self.profiles.values() if t.is_runnable()]
        self.state = status

        # Setup task status
        for task in self.tasks:
            try:
                self.save_state(task.name, {"started": 0, "pid": 0}, False)
                task.last_run = datetime.fromtimestamp(self.state[task.name].getfloat("last_run"))
                if task.last_run > datetime.now() - timedelta(hours=24):
                    task.next_run = task.find_next_run(task.last_run)
            except:
                pass

    def save_state(self, section, values, write=True):
        if not self.state.has_section(section):
            self.state.add_section(section)
        self.state[section].update({k: str(v) for k, v in values.items()})
        if write and self.base_path.is_dir():
            with self.base_path.joinpath("status.ini").open("w") as fp:
                self.state.write(fp)

    def run(self, profile=None, args=[]):
        logging.info(f"running {args} on {profile}!")
        self.running = True

    def stop(self):
        logging.info("shutting down...")
        self.running = False


class ServiceHandler(BaseHandler):
    """Run in service mode (task scheduler) and output to files
    The service is also responsible for the GUI.
    """

    def set_status(self, status, busy=False):
        if status != self.status:
            logging.info(f"status: {status}")
            self.status = status
            if self.gui:
                self.gui.title = "Prestic backup manager\n" + (status or "idle")
                icon = self.icons["busy"] if busy else self.icons["norm"]
                if self.gui.icon is not icon:
                    self.gui.icon = icon
                # This can cause issues if the menu is currently open
                # but there is no way to know if it is...
                self.gui.update_menu()

    def notify(self, message, title=None):
        if self.gui:
            self.gui.notify(message, f"{PROG_NAME}: {title}" if title else PROG_NAME)
            time.sleep(1)

    def run_task(self, task):
        self.set_status(f"running task {task.name}", True)

        proc = task.run(stdout=PIPE, stderr=STDOUT)
        output = []

        if self.base_path.is_dir():
            log_file = f"{task.name}-{time.strftime('%Y.%m.%d_%H.%M')}.txt"
            log_fd = self.base_path.joinpath("logs", log_file).open("w")
            log_fd.write(f"Repository: {task['repository'] or task['repository-file']}\n")
            log_fd.write(f"Command line: {' '.join(shlex.quote(s) for s in proc.args)}\n")
            log_fd.write(f"Date: {datetime.now()}\n\n")
            log_fd.flush()
        else:
            log_file = ""
            log_fd = None

        self.save_state(task.name, {"started": time.time(), "pid": proc.pid, "log_file": log_file})

        for line in proc.stdout:
            logging.debug("[restic] " + line.rstrip())
            output.append(line.rstrip())
            if log_fd:
                log_fd.write(line)
                log_fd.flush()

        ret = proc.wait()

        if log_fd:
            log_fd.write(f"\nProcess exit code: {ret}")
            log_fd.close()

        if ret == 0:
            status_txt = f"task {task.name} finished"
        elif ret == 3 and "backup" in task.command:
            status_txt = f"task {task.name} finished with some warnings..."
        else:
            status_txt = f"task {task.name} FAILED! (exit code: {ret})"

        self.notify(("\n".join(output[-4:]))[-220:].strip(), status_txt)
        self.set_status(status_txt)
        self.save_state(task.name, {"last_run": time.time(), "exit_code": ret, "pid": 0})

    def run_gui(self, service_loop):
        """ Build GUI callbacks and parameters """
        icon = Image.open(BytesIO(b64decode(PROG_ICON))).convert("RGBA")
        self.icons = {
            "norm": icon,
            "busy": Image.alpha_composite(Image.new("RGBA", icon.size, (255, 0, 255, 255)), icon),
            "fail": Image.alpha_composite(Image.new("RGBA", icon.size, (255, 0, 0, 255)), icon),
        }

        def gui_setup(icon):
            icon.visible = True
            service_loop(icon)

        def on_run_now_click(task):
            def on_click():
                self.notify(f"{task.name} will run next")
                task.next_run = datetime.now()

            return on_click

        def on_log_click(task):
            def on_click():
                log_file = self.state[task.name].get("log_file", "")
                if log_file:
                    os_open_file(self.base_path.joinpath("logs", log_file))

            return on_click

        def tasks_menu():
            for task in self.tasks:
                task_menu = pystray.Menu(
                    pystray.MenuItem(task.description, on_log_click(task)),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(f"Next run: {time_diff(task.next_run)}", lambda: 1),
                    pystray.MenuItem(f"Last run: {time_diff(task.last_run)}", on_log_click(task)),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem("Run Now", on_run_now_click(task)),
                )
                yield pystray.MenuItem(task.name, task_menu)

        self.gui = pystray.Icon(
            name=PROG_NAME,
            icon=icon,
            menu=pystray.Menu(
                pystray.MenuItem("Tasks", pystray.Menu(tasks_menu)),
                pystray.MenuItem("Open prestic folder", lambda: os_open_file(self.base_path)),
                pystray.MenuItem("Reload config", lambda: (self.load_config())),
                pystray.MenuItem("Quit", lambda: self.quit()),
            ),
        )
        self.gui.run(setup=gui_setup)

    def run(self, profile, args=[]):
        self.status = None
        self.gui = None

        def service_loop(*args):
            self.save_state("__prestic__", {"pid": os.getpid()})
            self.set_status("service started")
            self.running = True

            for task in self.tasks:
                logging.info(f"    > {task.name} will next run {time_diff(task.next_run)}")

            while self.running:
                try:
                    next_task = None
                    sleep_time = 60

                    for task in self.tasks:
                        if task.next_run:
                            if task.is_pending():  # or 'backup' in task['command']:
                                self.run_task(task)
                            if not next_task or task.next_run < next_task.next_run:
                                next_task = task

                    if next_task:
                        sleep_time = max(0, (next_task.next_run - datetime.now()).total_seconds())
                        self.set_status(
                            f"{next_task.name} will run {time_diff(next_task.next_run)}"
                        )

                except Exception as e:
                    logging.error(f"service_loop crashed: {type(e).__name__} '{e}'")
                    self.notify(str(e), f"Unhandled exception: {type(e).__name__}")
                    # raise e

                time.sleep(min(sleep_time, 10))
            self.quit(0)

        if pystray:
            self.run_gui(service_loop)
        else:
            logging.warning("pystray not installed, gui features won't be available")
            service_loop()

    def quit(self, rc=0):
        logging.info("shutting down...")
        self.running = False
        if self.gui:
            self.gui.visible = False
            # self.gui.stop()
        os._exit(rc)


class KeyringHandler(BaseHandler):
    """ Keyring manager (basically a `keyring` clone) """

    def run(self, profile, args=[]):
        if len(args) != 2 or args[0] not in ["get", "set", "del"]:
            exit("Usage: get|set|del username")
        try:
            if args[0] == "get":
                ret = keyring.get_password(PROG_NAME, args[1])
            elif args[0] == "set":
                keyring.set_password(PROG_NAME, args[1], getpass())
                ret = "OK"
            elif args[0] == "del":
                keyring.delete_password(PROG_NAME, args[1])
                ret = "OK"
            if ret is None:
                exit("Error: Not found")
            print(ret, end="")
        except Exception as e:
            exit(f"Error: {repr(e)}")


class CommandHandler(BaseHandler):
    """ Run a single command and output to stdout """

    def run(self, profile_name, args=[]):
        profile = self.profiles.get(profile_name)
        if profile:
            logging.info(f"profile: {profile.name} ({profile.description})")
            try:
                exit(profile.run(args).wait())
            except OSError as e:
                logging.error(f"unable to start restic: {e}")
        else:
            logging.error(f"profile {profile_name} does not exist")
            print(f"\nAvailable profiles:")
            for name, profile in self.profiles.items():
                repository = profile["repository"] or profile["repository-file"] or None
                if repository:
                    command = profile.command if profile.command else ""
                    print(f"    > {name} ({profile.description}) [{repository}] {command}")
        exit(-1)


def time_diff(time, from_time=None):
    if not time:
        return "never"
    from_time = from_time or datetime.now()
    time_diff = (time - from_time).total_seconds()
    days = floor(abs(time_diff) / 86400)
    hours = floor(abs(time_diff) / 3600) % 24
    minutes = floor(abs(time_diff) / 60) % 60
    suffix = "from now" if time_diff > 0 else "ago"
    if abs(time_diff) < 60:
        return "just now"
    return f"{days}d {hours}h {minutes}m {suffix}"


def os_open_file(path):
    if sys.platform == "win32":
        Popen(["start", str(Path(path))], shell=True).wait()
    elif sys.platform == "darwin":
        Popen(["open", str(Path(path))], shell=True).wait()
    else:
        Popen(["xdg-open", str(Path(path))]).wait()


def main(argv=None):
    parser = ArgumentParser(description="Prestic Backup Manager (for restic)")
    parser.add_argument("-c", "--config", default=PROG_FOLDER, help="config file or directory")
    parser.add_argument("-p", "--profile", default="default", help="profile to use")
    parser.add_argument("--service", const=True, action="store_const", help="start service")
    parser.add_argument("--keyring", const=True, action="store_const", help="keyring management")
    parser.add_argument("command", nargs="...", help="restic command to run...")
    args = parser.parse_args(argv)

    logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)

    if args.service:
        handler = ServiceHandler(args.config)
    elif args.keyring:
        handler = KeyringHandler(args.config)
    else:
        handler = CommandHandler(args.config)

    try:
        handler.run(args.profile, args.command)
    except KeyboardInterrupt:
        handler.stop()


def gui():
    main([*sys.argv[1:], "--service"])


if __name__ == "__main__":
    main()
