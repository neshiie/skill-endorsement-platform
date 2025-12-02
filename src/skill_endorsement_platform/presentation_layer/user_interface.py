"""Implements the application user interface."""

from skill_endorsement_platform.application_base import ApplicationBase
from skill_endorsement_platform.service_layer.app_services import AppServices

import inspect
from pyfiglet import Figlet

from dataclasses import dataclass
from typing import List
# Rich imports
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt


@dataclass
class MenuItem:
    key: str            # logical action id
    label: str          # what we show in the menu
    aliases: List[str]  # inputs that map to  action


class UserInterface(ApplicationBase):
    """UserInterface Class Definition."""
    def __init__(self, config: dict) -> None:
        """Initializes object."""
        self._config_dict = config
        self.META = config["meta"]
        super().__init__(
            subclass_name=self.__class__.__name__,
            logfile_prefix_name=self.META["log_prefix"],
        )
        self.DB = AppServices(config)
        self.console = Console()  # Rich console
        self._logger.log_debug(f"{inspect.currentframe().f_code.co_name}: UI initialized!")

    MENU_ITEMS = [
        MenuItem("add_user",        "Add User",         ["1", "add",       "a", "u"]),
        MenuItem("view_users",      "View Users",       ["2", "view",      "vu"    ]),
        MenuItem("add_skill",       "Add Skill",        ["3", "skill",     "s"     ]),
        MenuItem("view_skills",     "View Skills",      ["4", "vskill",    "vs"    ]),
        MenuItem("add_user_skill",  "Add User Skill",   ["5", "uskill", "usrskill" ]),
        MenuItem("write_review",    "Write Review",     ["6", "review",    "r", "w"]),
        MenuItem("read_reviews",    "Read Reviews",     ["7", "read",      "rr"    ]),
        MenuItem("help",            "Help",             ["8", "help",      "h", "?"]),
        MenuItem("quit",            "Quit",             ["9", "quit", "q", "exit"  ]),
    ]

    alias_map = {}
    for item in MENU_ITEMS:
        for alias in item.aliases:
            alias_map[alias.lower()] = item.key

    all_aliases = list(alias_map.keys())

    # ---------- internal helpers ----------

    def _render_table(self, title: str, rows):
        """Render a list[dict] as a Rich table."""
        if not rows:
            self.console.print(Panel.fit(f"[bold yellow]{title}[/]\n(no results)"))
            return

        # assume rows are dicts
        columns = list(rows[0].keys())

        table = Table(title=title, show_lines=True)

        # add columns
        for col in columns:
            table.add_column(col, style="cyan", no_wrap=False)

        # add rows
        for row in rows:
            table.add_row(*(str(row[col]) for col in columns))

        self.console.print(table)
        self.console.print('\n')

    def _menu_loop(self):

        lines = []

        for i, item in enumerate(self.MENU_ITEMS, start=1):
            # show number + label, hide extra aliases
            lines.append(f"[bold cyan]{i}[/] - {item.label}")

        while True:
            self.console.print(Panel("\n".join(lines), title="[bold cyan]Main Menu", expand=False))

            raw = Prompt.ask("[bold cyan]Enter your selection",
                                   choices=self.all_aliases,
                                   case_sensitive=False,
                                   show_choices=False)

            selection = self.alias_map[raw.lower()]
            self.console.print(f"\n[bold red]You picked: [/]{selection}\n")

            match selection:
                case "add_user":
                    s_username      = Prompt.ask("[bold cyan]Enter new username")
                    s_email         = Prompt.ask("[bold cyan]Enter email")
                    s_fullname      = Prompt.ask("[bold cyan]Enter full name")
                    s_role          = Prompt.ask("[bold cyan]Enter user role",
                                                 choices=["student",
                                                          "instructor",
                                                          "admin"])

                    self.DB.query("add user", s_username, s_email, s_fullname, s_role)
                    self.console.print(f"Added user {s_username}")
                    user = self.DB.query("get users by name", s_username)
                    self._render_table(f"{s_username}", user)

                case "view_users":
                    users = self.DB.query("view users")
                    self._render_table(f"All users", users)

                case "view_skills":
                    skills = self.DB.query("view skills")
                    self._render_table(f"All skills", skills)

                case "add_skill":
                    s_name          = Prompt.ask("Enter skill name")
                    s_category      = Prompt.ask("Enter skill category")
                    s_description   = Prompt.ask("Enter skill description")

                    self.DB.query("add skill", s_name, s_category, s_description)
                    self.console.print(f"Added skill {s_name}")
                    skill = self.DB.query("get skills by cat", f"%{s_category}%")
                    self._render_table(f"{s_category}", skill)

                case "add_user_skill":
                    s_name      = Prompt.ask("Enter username")
                    s_skill     = Prompt.ask("Enter skill")
                    s_level     = Prompt.ask("Enter skill level")
                    s_yoe       = Prompt.ask("Enter years of experience")

                    userid = self.DB.query("get user id", s_name)[0]['user_id']
                    skillid = self.DB.query("get skill id", s_skill)[0]['skill_id']

                    self.DB.query("add user skill", userid, skillid, s_level, s_yoe)
                    self.DB.query("get user skills by user id", userid)

                case "write_review":
                    self.console.print("Writing a review...")

                    # fetch input fields
                    s_source = Prompt.ask("Enter endorser username")
                    s_target = Prompt.ask("Enter endorsee username")
                    s_skill  = Prompt.ask("Enter skill name")
                    s_text   = Prompt.ask("Enter endorsement description")
                    s_rating = Prompt.ask("Enter rating")

                    # fetch ids from given user and skill names
                    source_userid = (self.DB.query("get user id", s_source))[0]['user_id']
                    target_userid = self.DB.query("get user id", s_target)[0]['user_id']
                    skill_id = self.DB.query("get skill id", s_skill)[0]['skill_id']

                    self.DB.query("add endorsement",
                                  source_userid,
                                  target_userid,
                                  skill_id,
                                  s_text,
                                  s_rating)
                    endorsement = self.DB.query("get endorsements by endorser",
                                                source_userid)

                    self._render_table(
                        (
                            f"{s_skill} endorsement for {s_target}"
                            f"by {s_source}"
                        ),
                        endorsement,
                    )

                case "read_reviews":
                    self.console.print("Reading reviews...")
                    s_username = Prompt.ask("Enter endorsee name")

                    user = self.DB.query("get users by name", s_username)

                    if user:
                        user_id = self.DB.query("get user id", s_username)[0]['user_id']
                        endorsements = self.DB.query("get endorsements by endorsee",
                                                     user_id)
                        if not endorsements:
                            self.console.print(f"No endorsements from user {s_username}")
                        else:
                            self._render_table(f"Endorsements for {s_username}",
                                               endorsements)

                    else:
                        self.console.print(
                            (
                                f"\n[bold red]error: "
                                f"[/]no user named \"{s_username}\"\n"
                            )
                        )

                case "help":
                    self.console.print(self.MENU_ITEMS)
                case "quit":
                    self.console.print("Quitting...")
                    break

            self.console.print()


    def start(self):
        self._logger.log_debug("UI started!")
        fig = Figlet(font="slant")
        title = fig.renderText("skill\nendorsement\nplatform")
        self.console.print(f"[bold red]{title}")
        self._menu_loop();


    def test_tables(self):
        # 1. Get all users
        users = self.DB.query("get all users")
        self._render_table("All Users", users)

        # 2. Get users by ID
        user = self.DB.query("get users by id", 1)
        self._render_table("User with ID 1", user)

        # 3. Get skills by category
        skills = self.DB.query("get skills by cat", "%b%")
        self._render_table("Skills (category LIKE '%Prog%')", skills)

        # 4. Endorsements for a given user
        endorsements = self.DB.query("get endorsements by endorser", 3)
        self._render_table("Endorsements by user 3", endorsements)

