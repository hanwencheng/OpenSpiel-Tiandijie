import math
import tkinter as tk
from tkinter import messagebox, StringVar, OptionMenu
from absl import flags, app
from PIL import Image, ImageTk
import pyspiel
import logging
import Pmw
import numpy as np
from open_spiel.python import games  # pylint: disable=unused-import
from open_spiel.python import rl_environment
from open_spiel.python import rl_tools
from open_spiel.python.algorithms import tabular_qlearner
from open_spiel.python.algorithms import random_agent
from open_spiel.python.games.Tiandijie.primitives.map.TerrainType import TerrainType
from open_spiel.python.games.Tiandijie.primitives.ActionTypes import ActionTypes
from open_spiel.python.games.Tiandijie.primitives.hero.heroes import HeroeTemps
from open_spiel.python.games.Tiandijie.calculation.attribute_calculator import get_max_life, get_attack, get_defense, get_luck
import threading
import time
import os
import pickle

FLAGS = flags.FLAGS
flags.DEFINE_string("game_string", "tiandijie", "Game string")
EpisodeTime = int(1000)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

WIDTH = 4
HEIGHT = 2

PICTURE_WIDTH = 50
PICTURE_HEIGHT = 50
PICTURE_SIZE = (50, 50)
SPACING_X = 10
SPACING_Y = 6
HUMAN_PLAYER = 1    # 0 为先手， 1为后手

Q_LEARNER_AGENTS = []
for idx in range(2):
    if os.path.exists(f"2xqlearner_model_{idx}x{EpisodeTime}.pkl"):
        with open(f"2xqlearner_model_{idx}x{EpisodeTime}.pkl", "rb") as f:
            Q_LEARNER_AGENTS.append(pickle.load(f))
        print("读取")
    else:
        print("创建")
        Q_LEARNER_AGENTS.append(tabular_qlearner.QLearner(player_id=idx, num_actions=1000))
RANDOM_AGENTS = [
          random_agent.RandomAgent(player_id=idx, num_actions=1000)
          for idx in range(2)
]


class TIANDIJIEGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TianDiJieAISimulation")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._terminal = False
        self.env = rl_environment.Environment("tiandijie")
        self.num_players = self.env.num_players
        self.num_actions = self.env.action_spec()["num_actions"]

        # random agents for evaluation
        self.data_dict = {}
        self.image_cache = {}
        self.heroes = []
        self.cemetery = []
        self.button_dic = {}
        self.skill_dic = {}
        self.tool_tip = Pmw.Balloon(root)
        self.input = None
        self.confirm_action_button = None
        self.tentative_position = {'hero': None, 'position': None}
        self.map = None

        # 创建一个 Frame 来包含所有小部件
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(pady=10)

        self.map_options = ["妖山幻境", "天宫幻境", "城隅幻境"]
        self.map_name = self.map_options[0]
        self.hero_options = [member.value.temp_id for member in HeroeTemps]
        self.choose_heroes_0 = self.hero_options[:5]
        self.choose_heroes_1 = self.hero_options[:5]

        self.init_config_frame()

    def init_config_frame(self):
        self.config_frame = tk.Frame(self.main_frame)
        self.config_frame.pack()
        tk.Label(self.config_frame, text="map:").grid(row=0, column=1)
        tk.Label(self.config_frame, text=self.map_name).grid(row=0, column=2)
        for i in range(len(self.choose_heroes_0)):
            tk.Label(self.config_frame, text=self.choose_heroes_0[i], fg="blue").grid(row=i + 1, column=0)
        for i in range(len(self.choose_heroes_1)):
            tk.Label(self.config_frame, text=self.choose_heroes_1[i], fg="red").grid(row=i + 1, column=10)

        tk.Button(self.config_frame, text="confirm", command=self.go_tiandijie).grid(row=len(self.choose_heroes_0) + 1,
                                                                                  column=1)
        tk.Button(self.config_frame, text="hero_config", command=self.create_new_window).grid(
            row=len(self.choose_heroes_0) + 1, column=2)

    def create_new_window(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("New Window")
        new_window_frame = tk.Frame(new_window)
        new_window_frame.pack(pady=10)

        # 创建一个StringVar以保持当前选择的值
        self.selected_map_option = tk.StringVar(self.root)
        self.selected_map_option.set(self.map_options[0])  # 默认选项

        # 创建下拉菜单
        self.dropdown = tk.OptionMenu(new_window_frame, self.selected_map_option, *self.map_options)
        self.dropdown.grid(row=0, column=1)

        self.vars_0 = [tk.IntVar() for _ in range(len(self.hero_options))]
        self.vars_1 = [tk.IntVar() for _ in range(len(self.hero_options))]
        for idx, option in enumerate(self.hero_options):
            # 创建第一列的 Checkbutton
            cb0 = tk.Checkbutton(new_window_frame, text=option, foreground="blue", variable=self.vars_0[idx],
                                 command=self.checkbutton_clicked)
            cb0.grid(row=idx + 1, column=0, sticky='w')

            # 创建第二列的 Checkbutton，并设置垂直对齐
            cb1 = tk.Checkbutton(new_window_frame, text=option, foreground="red", variable=self.vars_1[idx],
                                 command=self.checkbutton_clicked)
            cb1.grid(row=idx + 1, column=10, sticky='w')

        self.button_show = tk.Button(new_window_frame, text="确认配置",
                                     command=lambda: self.confirm_new_config(new_window), state="disabled")
        self.button_show.grid(row=len(self.hero_options) + 1, column=1, pady=10)

    def checkbutton_clicked(self):
        if sum(1 for var in self.vars_0 if var.get() == 1) == 0 or sum(1 for var in self.vars_1 if var.get() == 1) == 0:
            self.button_show.config(state="disabled")
        elif sum(1 for var in self.vars_0 if var.get() == 1) >= 6 or sum(
                1 for var in self.vars_1 if var.get() == 1) >= 6:
            self.button_show.config(state="disabled")
        else:
            self.button_show.config(state="active")

    def confirm_new_config(self, new_window):
        self.map_name = self.selected_map_option.get()
        self.choose_heroes_0 = [option for idx, option in enumerate(self.hero_options) if self.vars_0[idx].get()]
        self.choose_heroes_1 = [option for idx, option in enumerate(self.hero_options) if self.vars_1[idx].get()]
        self.remove_other_frame()
        self.init_config_frame()
        new_window.destroy()

    def go_tiandijie(self):
        self.time_step = self.env.reset()
        self.now_state = self.env.get_state
        self.heroes = self.now_state.context.heroes
        self.cemetery = self.now_state.context.cemetery
        self.map = self.now_state.context.battlemap.map
        self.remove_other_frame()
        self.create_map()
        self.init_hero_map()
        # 更改英灵位置

    def start_simulation(self):
        self.button_dic["button_train"].config(state="disabled")
        self.button_dic["button_simulate"].config(state="disabled")
        self.button_dic["button_paused"].config(state="active")
        self.time_step = self.env.reset()
        self.now_state = self.env.get_state
        self.heroes = self.now_state.context.heroes
        self.cemetery = self.now_state.context.cemetery
        self.init_hero_map()
        self.add_text("SIMULATE_START")
        self._paused = False
        threading.Thread(target=self.simulation_worker).start()

    def simulation_worker(self):
        while not self.time_step.last() and not self._terminal and not self._paused:
            player_id = self.time_step.observations["current_player"]
            if player_id == pyspiel.PlayerId.TERMINAL:
                print(self.time_step.rewards)
                break
            agent_output = Q_LEARNER_AGENTS[player_id].step(self.time_step)
            self.add_text(f"Agent {player_id} chooses {self.env.get_state.action_to_string(agent_output.action)}")
            self.time_step = self.env.step([agent_output.action])
            self.redraw_hero_map()

        print(self.time_step.rewards)

    def battle_with_qlearner(self):
        self.button_dic["button_train"].config(state="disabled")
        self.button_dic["button_simulate"].config(state="disabled")
        self.button_dic["button_paused"].config(state="disabled")
        self.time_step = self.env.reset()
        self.now_state = self.env.get_state
        self.heroes = self.now_state.context.heroes
        self.cemetery = self.now_state.context.cemetery
        self.init_hero_map()
        self.add_text("BATTLE_WITH_AI")

        threading.Thread(target=self.battle_with_qlearner_worker).start()

    def battle_with_qlearner_worker(self):
        while not self.time_step.last() and not self._terminal:
            player_id = self.time_step.observations["current_player"]
            if player_id == pyspiel.PlayerId.TERMINAL:
                self.add_text("GAME_OVER")
                print(self.time_step.rewards)
                return
            if player_id == HUMAN_PLAYER:
                action = self.command_line_action(self.time_step)
                self.time_step = self.env.step([action], self.add_text)
                logging.info(f"player_reward for 0 {self.time_step.rewards[0]}, player_reward for 1 {self.time_step.rewards[1]}")
                self.redraw_all()
            else:
                agent_output = Q_LEARNER_AGENTS[player_id].step(self.time_step, is_evaluation=True)
                self.time_step = self.env.step([agent_output.action], self.add_text)
                self.redraw_hero_map()
            self.redraw_skill_terrain()

        print(self.time_step.rewards)

    def command_line_action(self, time_step):
        self.input = None
        current_player = time_step.observations["current_player"]
        if current_player == pyspiel.PlayerId.TERMINAL:
            print(self.time_step.rewards)
            return
        legal_actions = time_step.observations["legal_actions"][current_player]
        action = -1
        while action not in legal_actions and not self._terminal:
            action_str = self.input
            try:
                action = int(action_str)
            except (ValueError, TypeError):
                continue
        return action

    def thread_paused(self):
        self.button_dic["button_paused"].config(command=self.thread_continue, text="GO_ON")
        self.button_dic["button_next_step"].config(state="active")
        self._paused = True

    def thread_continue(self):
        self.button_dic["button_paused"].config(command=self.thread_paused, text="PAUSED")
        self.button_dic["button_next_step"].config(state="disabled")
        self._paused = False
        threading.Thread(target=self.simulation_worker).start()

    def next_step(self):
        player_id = self.time_step.observations["current_player"]
        if player_id == pyspiel.PlayerId.TERMINAL:
            return
        agent_output = Q_LEARNER_AGENTS[player_id].step(self.time_step)
        self.add_text(f"Agent {player_id} chooses {self.env.get_state.action_to_string(agent_output.action)}")
        self.time_step = self.env.step([agent_output.action])
        self.redraw_hero_map()

        print(self.time_step.rewards)

    def get_hero_by_id(self, player_id):
        for hero in self.heroes:
            if hero.id == str(player_id):
                return hero

    def redraw_skill_terrain(self):
        for position, data in self.data_dict.items():
            if self.now_state.context.battlemap.get_terrain(position).terrain_type.value[0] == TerrainType.JINWUQI.value[0]:
                image_path = f"open_spiel/python/games/Tiandijie/res/布旗.png"
                image = self.load_image(image_path, PICTURE_SIZE)
                data["button"].config(image=image, width=PICTURE_WIDTH, height=PICTURE_HEIGHT)
                data["button"].image = image

    def remove_other_frame(self):
        self.config_frame.destroy()

    def create_map(self):
        # map_Frame
        self.map_container = tk.Frame(self.main_frame)
        self.map_container.pack(padx=SPACING_X, pady=SPACING_Y)

        for row in range(len(self.map)):
            for column in range(len(self.map[0])):
                # 创建一个不可编辑的标签
                button = tk.Button(self.map_container, borderwidth=1, relief="solid", width=WIDTH, height=HEIGHT,# text=100,compound='left',
                                  state="disabled")
                button.grid(row=row, column=column, padx=SPACING_X, pady=SPACING_Y)
                if self.map[row][column].terrain_type.value[0] == TerrainType.IMPASSABLE_OBSTACLE.value[0]:
                    self.set_grid_to_impassable(button)
                self.data_dict[(row, column)] = {'button': button, 'hero': None}

        # 创建第一个按钮
        self.button_dic["button_train"] = tk.Button(self.map_container, text="TRAIN", command=self.Episode_for_agent, font=(None, 8))
        self.button_dic["button_train"].grid(row=len(self.map) + 1, column=0, padx=SPACING_X, pady=SPACING_Y)

        # 创建第二个按钮
        self.button_dic["button_simulate"] = tk.Button(self.map_container, text="SIMULATE", command=self.start_simulation, font=(None, 7))
        self.button_dic["button_simulate"].grid(row=len(self.map) + 1, column=1, padx=SPACING_X, pady=SPACING_Y)

        self.button_dic["button_paused"] = tk.Button(self.map_container, text="PAUSED", command=self.thread_paused, font=(None, 7),
                                                     state="disabled")
        self.button_dic["button_paused"].grid(row=len(self.map) + 1, column=2, padx=SPACING_X, pady=SPACING_Y)

        self.button_dic["button_next_step"] = tk.Button(self.map_container, text="NEXT_STEP", command=self.next_step, font=(None, 7),
                                                        state="disabled")
        self.button_dic["button_next_step"].grid(row=len(self.map) + 1, column=3, padx=SPACING_X, pady=SPACING_Y)

        self.button_dic["battle_with_qlearner"] = tk.Button(self.map_container, text="VS_Q_LEARNER", font=(None, 5),
                                                            command=self.battle_with_qlearner)
        self.button_dic["battle_with_qlearner"].grid(row=len(self.map) + 1, column=4, padx=SPACING_X, pady=SPACING_Y)

        # 创建文本框
        self.text_entry = tk.Text(self.map_container, state="disabled", bg="#D9D9D9", width=35, height=3, wrap=tk.WORD)
        self.text_entry.grid(row=0, column=len(self.map[0]) + 3, padx=SPACING_X, pady=SPACING_Y, rowspan=len(self.map),
                             sticky='nsew', )

        # 创建垂直滚动条
        self.scrollbar = tk.Scrollbar(self.map_container, orient="vertical", command=self.text_entry.yview,
                                      highlightthickness=8)
        self.scrollbar.grid(row=0, column=len(self.map[0]) + 4, rowspan=len(self.map), sticky='ns')
        self.text_entry.config(yscrollcommand=self.scrollbar.set)
        self.text_entry.see("end")

    def add_text(self, text):
        # 激活文本框以便写入内容
        self.text_entry.config(state="normal")
        self.text_entry.insert(tk.END, text + "\n")
        self.text_entry.config(state="disabled")
        self.text_entry.yview_moveto(1.0)

    def init_hero_map(self):
        for hero in self.heroes:
            self.data_dict[hero.position]['hero'] = hero
            self.update_hero_position(hero, self.data_dict[hero.position])

    def redraw_hero_map(self):
        for hero in self.heroes:
            if not self.data_dict[hero.position]["hero"]:
                self.remove_hero_position_in_data_dict(hero)
                self.data_dict[hero.position]["hero"] = hero
                self.update_hero_position(hero, self.data_dict[hero.position])
        for hero in self.cemetery:
            self.remove_hero_position_in_data_dict(hero)
        self.check_all_actionable_heroes()

    def redraw_all(self):
        self.check_all_heroes_position()
        for position, data in self.data_dict.items():
            if data["button"].cget("bg") in {"green", "yellow", "orange"}:
                data["button"].config(bg="#D9D9D9", state="disabled", command=None)

        action = self.now_state.context.get_last_action()
        if action.has_additional_action:
            for position, data in self.data_dict.items():
                if data["hero"] and data["hero"].id == action.actor.id:
                    data["button"].config(state="normal", command=lambda p=position: self.expected_move_hero(action.actor, p))
                    self.show_action(action.actor)
                elif data["button"].cget("bg") != "green":
                    data["button"].config(state="disabled", command=None)
        else:
            self.check_all_actionable_heroes()

    def check_all_heroes_position(self):
        for position, data in self.data_dict.items():
            if data["hero"] and data["hero"].position != position:
                hero = self.get_hero_by_id(data["hero"].id)
                self.remove_hero_position_in_data_dict(data["hero"])
                if hero:
                    self.data_dict[hero.position]['hero'] = hero
                    self.update_hero_position(hero, self.data_dict[hero.position])
                data["hero"] = None
            if data["button"].cget("image") and not data["hero"] and self.map[position[0]][position[1]].terrain_type.value[0] != TerrainType.IMPASSABLE_OBSTACLE.value[0]:
                self.remove_hero_photo(data)

        self.check_all_actionable_heroes()

    def check_all_actionable_heroes(self):
        for hero in self.heroes:
            self.update_hero_attribute(hero, hero.position)
            if hero.actionable and self.data_dict[hero.position]['button'].cget("state") == "disabled":
                self.data_dict[hero.position]['button'].config(state="normal",
                                                               command=lambda p=hero: self.show_action(p))
            elif not hero.actionable and self.data_dict[hero.position]['button'].cget("state") == "normal":
                self.data_dict[hero.position]['button'].config(state="disabled", command=None)

            if hero.player_id == 1 and self.data_dict[hero.position]['button'].cget("bg") != "blue":
                self.data_dict[hero.position]['button'].config(bg="blue", command=lambda p=hero: self.show_action(p))
            if hero.player_id == 0 and self.data_dict[hero.position]['button'].cget("bg") != "red":
                self.data_dict[hero.position]['button'].config(bg="red", command=lambda p=hero: self.show_action(p))

    def remove_hero_position_in_data_dict(self, hero):
        for position, data in self.data_dict.items():
            if data["hero"] and data["hero"].id == hero.id:
                data["hero"] = None
                data["button"].config(image='', width=WIDTH, height=HEIGHT, bg="#D9D9D9", state="disabled")
                self.config_tooltip_hide(data["button"])
                break

    def expected_move_hero(self, hero, position):
        self.data_dict[self.tentative_position['position']]["button"].config(image='', width=WIDTH, height=HEIGHT, bg="green")
        self.config_tooltip_hide(self.data_dict[self.tentative_position['position']]["button"])
        self.update_hero_photo(hero, position)
        self.tentative_position['position'] = position
        self.show_normal_attack_action()

    def show_normal_attack_action(self):
        for action in self.now_state.legal_actions_dic[HUMAN_PLAYER]:
            if action.actor == self.tentative_position['hero'] and action.move_point == self.tentative_position['position']:
                if action.type.value == ActionTypes.NORMAL_ATTACK.value:
                    self.data_dict[action.action_point]["button"].config(bg="orange", state="normal", command=lambda p=action.action_point: self.confirm_target(p))

    def show_action(self, hero):
        if self.tentative_position['hero']:
            self.remove_hero_photo(self.data_dict[self.tentative_position['position']])
            self.update_hero_position(self.tentative_position['hero'], self.data_dict[self.tentative_position['hero'].position])
        self.tentative_position = {'hero': hero, 'position': hero.position}
        action_test = []
        skill_list = []
        self.move_range_set = set()
        for action in self.now_state.legal_actions_dic[HUMAN_PLAYER]:
            if action.actor == hero:
                action_test.append(action)
                if action.move_point not in self.move_range_set:
                    self.move_range_set.add(action.move_point)
                if action.skill and action.skill not in skill_list:
                    skill_list.append(action.skill)

        for position, data in self.data_dict.items():
            if data["hero"] is None:
                if position in self.move_range_set:
                    data['button'].config(bg="green", state="normal",
                                          command=lambda p=position: self.expected_move_hero(hero, p))
                else:
                    if data['button'].cget("bg") != "#D9D9D9":
                        data['button'].config(bg="#D9D9D9", state="disabled", command=None)

        self.draw_skill_button(hero, skill_list)
        self.update_hero_attribute(hero, hero.position)

    def update_hero_attribute(self, hero, position):
        hero_id = hero.id
        shield_text = f"shield: {hero.shield} / {math.ceil(get_max_life(hero, None, self.now_state.context))}\n" if hero.temp.has_shield else ""
        buff_text = "buff:\n"
        for buff in hero.buffs:
            duration_text = f"{buff.duration}" if buff.duration < 15 else "no limit"
            if buff.stack > 1:
                buff_text += f"     {buff.temp.id}X{buff.stack}: {duration_text},\n"
            else:
                buff_text += f"     {buff.temp.id}: {duration_text},\n"
        text = (
            f"{hero_id[:-1]}  life: {math.ceil(hero.get_current_life(self.now_state.context))} / "
            f"{math.ceil(get_max_life(hero, None, self.now_state.context))}\n"
            f"{shield_text}"
            f"physical_attack: {math.ceil(get_attack(hero, None, self.now_state.context, False))}  magic_attack: {math.ceil(get_attack(hero, None, self.now_state.context, True))}\n"
            f"physical_defense: {math.ceil(get_defense(hero, None, False, self.now_state.context))}  magic_defense: {math.ceil(get_defense(hero, None, True, self.now_state.context))}\n"
            f"luck: {math.ceil(get_luck(hero, None, self.now_state.context))}\n"
            f"{buff_text}"
        )

        self.config_tooltip_text(self.data_dict[position]["button"], text)


    def draw_skill_button(self, hero, skill_list):
        if self.confirm_action_button is not None:
            self.confirm_action_button.destroy()
        for button in self.skill_dic.values():
            button.destroy()
        self.skill_dic = {}
        temp = 0
        for i, skill in enumerate(hero.enabled_skills):
            temp += 1
            image_path = f"open_spiel/python/games/Tiandijie/res/{skill.temp.chinese_name}.png"
            image = self.load_image(image_path, PICTURE_SIZE)
            self.skill_dic[skill.temp.chinese_name] = tk.Button(
                self.map_container,
                width=4,
                height=2,
                command=lambda t=skill.temp.chinese_name: self.select_skill(t)
            )
            self.skill_dic[skill.temp.chinese_name].grid(row=len(self.map) + 1, column=4 + temp, padx=SPACING_X, pady=SPACING_Y)
            self.skill_dic[skill.temp.chinese_name].config(image=image, width=PICTURE_WIDTH, height=PICTURE_HEIGHT, state="normal" if skill in skill_list else "disabled")
            self.config_tooltip_text(self.skill_dic[skill.temp.chinese_name], f"{skill.temp.id}, CD:{skill.cool_down}")

        for i, skill in enumerate(hero.enabled_passives):
            if skill.temp.passive_from == "skill":
                continue
            temp += 1
            image_path = f"open_spiel/python/games/Tiandijie/res/{skill.temp.chinese_name}.png"
            image = self.load_image(image_path, PICTURE_SIZE)
            self.skill_dic[skill.temp.chinese_name] = tk.Button(self.map_container, width=PICTURE_WIDTH, height=PICTURE_HEIGHT)
            self.skill_dic[skill.temp.chinese_name].grid(row=len(self.map) + 1, column=4 + temp, padx=SPACING_X, pady=SPACING_Y)
            self.skill_dic[skill.temp.chinese_name].config(image=image, width=PICTURE_WIDTH, height=PICTURE_HEIGHT, state="disabled")
            self.config_tooltip_text(self.skill_dic[skill.temp.chinese_name], f"passive: {skill.temp.id}")

        for i, skill in enumerate(skill_list):
            if skill in hero.enabled_skills:
                continue
            temp += 1
            image_path = f"open_spiel/python/games/Tiandijie/res/{skill.temp.chinese_name}.png"
            image = self.load_image(image_path, PICTURE_SIZE)
            self.skill_dic[skill.temp.chinese_name] = tk.Button(
                self.map_container,
                width=PICTURE_WIDTH,
                height=PICTURE_HEIGHT,
                command=lambda t=skill.temp.chinese_name: self.select_skill(t)
            )
            self.skill_dic[skill.temp.chinese_name].grid(row=len(self.map) + 1, column=4 + temp, padx=SPACING_X, pady=SPACING_Y)
            self.skill_dic[skill.temp.chinese_name].config(image=image, width=PICTURE_WIDTH, height=PICTURE_HEIGHT)
            self.config_tooltip_text(self.skill_dic[skill.temp.chinese_name], f"{skill.temp.id}, CD:{skill.cool_down}")

        self.confirm_action_button = tk.Button(self.map_container, text="confirm_AC", command=lambda h=hero: self.confirm_action(h), font=(None, 6))
        self.confirm_action_button.grid(row=len(self.map) + 1, column=5 + temp, padx=SPACING_X, pady=SPACING_Y)

    def select_skill(self, name):
        if self.skill_dic[name].cget("bg") == "red":
            self.skill_dic[name].config(bg="#d9d9d9")
        else:
            for button in self.skill_dic.values():
                if button.cget("bg") == "red":
                    button.config(bg="#d9d9d9")
            self.skill_dic[name].config(bg="red")
            self.show_skill_action(name)

    def show_skill_action(self, skill_name):
        for action in self.now_state.legal_actions_dic[HUMAN_PLAYER]:
            if action.actor == self.tentative_position['hero'] and action.move_point == self.tentative_position['position']:
                if action.skill and action.skill.temp.chinese_name == skill_name:
                    self.data_dict[action.action_point]["button"].config(bg="orange", state="normal", command=lambda p=action.action_point: self.confirm_target(p))
        for position, data in self.data_dict.items():
            if data["button"].cget("bg") == "orange" and data["button"].cget("state") == "normal" and data["button"].cget("command") is None:
                data["button"].config(bg="#D9D9D9", state="disabled")

    def confirm_target(self, position):
        if self.data_dict[position]["button"].cget("bg") == "yellow":
            self.data_dict[position]["button"].config(bg="orange")
        else:
            self.data_dict[position]["button"].config(bg="yellow")

    def confirm_action(self, hero):
        temp_skill = None
        temp_target = None

        for name, button in self.skill_dic.items():
            if button.cget("bg") == "red":
                temp_skill = name
                break

        for position, data in self.data_dict.items():
            if data["button"].cget("bg") == "yellow":
                temp_target = position
                break
        legal_actions = self.now_state.legal_actions_dic[HUMAN_PLAYER]
        for action in legal_actions:
            if action.actor == hero and action.move_point == self.tentative_position['position']:
                if temp_skill:
                    if action.skill and action.skill.temp.chinese_name == temp_skill:
                        if action.skill.temp.target_type.value == 3:
                            self.input = legal_actions.index(action)
                        else:
                            if action.action_point == temp_target:
                                self.input = legal_actions.index(action)
                                break
                else:
                    if temp_target:
                        if temp_skill is None and action.type.value == ActionTypes.NORMAL_ATTACK.value and action.action_point == temp_target:
                            self.input = legal_actions.index(action)
                            break
                    elif action.type.value in {ActionTypes.MOVE.value, ActionTypes.PASS.value}:
                        self.input = legal_actions.index(action)
                        break

    def update_hero_position(self, hero, data):
        hero_id = hero.id
        image_path = f"open_spiel/python/games/Tiandijie/res/{hero_id[:-1]}.png"
        image = self.load_image(image_path, PICTURE_SIZE)
        data["button"].config(image=image, width=PICTURE_WIDTH, height=PICTURE_HEIGHT, bg="red" if hero_id[-1] == "0" else "blue",
                      state="normal" if hero.actionable else "disabled", command=lambda p=hero: self.show_action(p))
        self.update_hero_attribute(hero, hero.position)

    def update_hero_photo(self, hero, position):
        hero_id = hero.id
        image_path = f"open_spiel/python/games/Tiandijie/res/{hero_id[:-1]}.png"
        image = self.load_image(image_path, PICTURE_SIZE)
        self.data_dict[position]["button"].config(image=image, width=PICTURE_WIDTH, height=PICTURE_HEIGHT, bg="red" if hero_id[-1] == "0" else "blue",
                      state="normal" if hero.actionable else "disabled")
        self.update_hero_attribute(hero, position)

    def remove_hero_photo(self, data):
        data["button"].config(image='', width=WIDTH, height=HEIGHT, bg="#D9D9D9")
        self.config_tooltip_hide(data["button"])

    def set_grid_to_impassable(self, button):
        image_path = f"open_spiel/python/games/Tiandijie/res/IMPASSABLE_OBSTACLE.png"
        image = self.load_image(image_path, PICTURE_SIZE)
        button.config(image=image, width=PICTURE_WIDTH, height=PICTURE_HEIGHT)
        button.image = image

    def load_image(self, path, size):
        if path not in self.image_cache:
            image = Image.open(path).resize(size, Image.LANCZOS)
            self.image_cache[path] = ImageTk.PhotoImage(image)
        return self.image_cache[path]

    def Episode_for_agent(self):
        threading.Thread(target=self.Episode_for_agent_worker2).start()

    def eval_against_random_bots(self, env, trained_agents, random_agents, num_episodes):
        """Evaluates `trained_agents` against `random_agents` for `num_episodes`."""
        wins = np.zeros(2)
        for player_pos in range(2):
            if player_pos == 0:
                cur_agents = [trained_agents[0], random_agents[1]]
            else:
                cur_agents = [random_agents[0], trained_agents[1]]
            for _ in range(num_episodes):
                if self._terminal:
                    return
                time_step = env.reset()
                while not time_step.last():
                    player_id = time_step.observations["current_player"]
                    if player_id == pyspiel.PlayerId.TERMINAL:
                        break
                    agent_output = cur_agents[player_id].step(time_step, is_evaluation=True)
                    time_step = env.step([agent_output.action])
                if time_step.rewards[player_pos] > 0:
                    wins[player_pos] += 1
        return wins / num_episodes

    def Episode_for_agent_worker2(self):
        self.add_text("Episode_Start")
        for cur_episode in range(EpisodeTime):
            logging.info("Starting episode %s", cur_episode)
            # if cur_episode == 0:
            #     win_rates = self.eval_against_random_bots(self.env, Q_LEARNER_AGENTS, RANDOM_AGENTS, 100)
            #     logging.info("Starting episode %s, win_rates %s", cur_episode, win_rates)
            time_step = self.env.reset()
            if self._terminal:
                return
            while not time_step.last():
                player_id = time_step.observations["current_player"]
                if player_id == pyspiel.PlayerId.TERMINAL:
                    break
                agent_output = Q_LEARNER_AGENTS[player_id].step(time_step)
                time_step = self.env.step([agent_output.action])

            # Episode is over, step all agents with final info state.
            # if cur_episode % int(1000) == 0 and cur_episode != 0:
            #     win_rates = self.eval_against_random_bots(self.env, Q_LEARNER_AGENTS, RANDOM_AGENTS, 100)
            #     logging.info("Starting episode %s, win_rates %s", cur_episode, win_rates)
            # elif cur_episode == EpisodeTime:
            #     win_rates = self.eval_against_random_bots(self.env, Q_LEARNER_AGENTS, RANDOM_AGENTS, 100)
            #     logging.info("Starting episode %s, win_rates %s", cur_episode, win_rates)

            for agent in Q_LEARNER_AGENTS:
                agent.step(time_step)

        with open(f"2xqlearner_model_0x{EpisodeTime}.pkl", "wb") as f:
            pickle.dump(Q_LEARNER_AGENTS[0], f)
        with open(f"2xqlearner_model_1x{EpisodeTime}.pkl", "wb") as f:
            pickle.dump(Q_LEARNER_AGENTS[1], f)
        print("Done")

    def on_closing(self):
        self._terminal = True
        self.root.destroy()

    def config_tooltip_hide(self, button):
        self.tool_tip.bind(button, None)

    def config_tooltip_text(self, button, text):
        self.tool_tip.bind(button, text)



if __name__ == "__main__":
    root = tk.Tk()
    app = TIANDIJIEGUI(root)
    root.mainloop()

