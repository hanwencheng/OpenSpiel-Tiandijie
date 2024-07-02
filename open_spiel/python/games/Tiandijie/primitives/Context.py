from __future__ import annotations

import random
from collections import Counter
from typing import List, TYPE_CHECKING, Dict
from open_spiel.python.games.Tiandijie.primitives.map.BattleMap import BattleMap

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.buff.buffs import BuffTemps
    from open_spiel.python.games.Tiandijie.primitives.fieldbuff.fieldbuffs import FieldBuffsTemps
    from open_spiel.python.games.Tiandijie.primitives import Action
    from open_spiel.python.games.Tiandijie.primitives.buff.BuffTemp import BuffTemp
    from open_spiel.python.games.Tiandijie.primitives.fieldbuff.FieldBuffTemp import FieldBuffTemp
from open_spiel.python.games.Tiandijie.primitives.formation.Formation import Formation
from open_spiel.python.games.Tiandijie.primitives.equipment.Equipments import Equipments
from open_spiel.python.games.Tiandijie.primitives.hero.Hero import Hero
from open_spiel.python.games.Tiandijie.primitives.hero.heroes import HeroeTemps
from open_spiel.python.games.Tiandijie.primitives.buff.BuffTemp import BuffTypes
from open_spiel.python.games.Tiandijie.primitives.Stone import Stones
from open_spiel.python.games.Tiandijie.primitives.skill.Skill import Skill
from open_spiel.python.games.Tiandijie.primitives.skill.skills import Skills
from open_spiel.python.games.Tiandijie.primitives.map.maps import Maps

from open_spiel.python.games.Tiandijie.calculation.Range import (
    calculate_square_area,
    calculate_diamond_area,
    calculate_cross_area,
)

from open_spiel.python.games.Tiandijie.primitives.map.Terrain import Terrain

TerrainMap = List[List[Terrain]]


class Context:
    def __init__(self):
        self.heroes: List[Hero] = []
        self.formation: List[Formation] = []
        self.actions: List[Action] = []
        self.harm_buffs_temps: List[BuffTemp] = []
        self.benefit_buffs_temps: Dict[str, BuffTemp] = {}
        self.fieldbuffs_temps: Dict[str, FieldBuffTemp] = {}
        self.all_buffs_temps: Dict[str, BuffTemp] = {}
        self.battlemap = None
        self.cemetery = []

    def add_action(self, action):
        self.actions.append(action)

    def get_last_action(self) -> Action:
        if self.actions:
            return self.actions[-1]
        else:
            return None  # Return None if there are no actions

    def get_partners_in_diamond_range(self, actor_instance: Hero, range_value: int) -> List[Hero]:
        base_position = actor_instance.position
        positions_list_in_range = calculate_diamond_area(base_position, range_value, self.battlemap)
        return [
            hero
            for hero in self.heroes
            if hero.position in positions_list_in_range and hero.player_id == actor_instance.player_id
        ]

    def get_all_partners(self, hero: Hero) -> List[Hero]:
        return [partner_hero for partner_hero in self.heroes if partner_hero.player_id == hero.player_id]

    def get_all_partners_position(self, hero: Hero):
        return [partner_hero.position for partner_hero in self.heroes if partner_hero.player_id == hero.player_id]

    def get_enemies_in_diamond_range(self, actor_instance: Hero, range_value: int) -> List[Hero]:
        base_position = actor_instance.position
        positions_list_in_range = calculate_diamond_area(base_position, range_value, self.battlemap)
        return [
            hero
            for hero in self.heroes
            if hero.position in positions_list_in_range and hero.player_id != actor_instance.player_id
        ]

    def get_enemies_in_diamond_range_by_target_point(self, actor_instance, base_position, range_value: int) -> List[Hero]:
        positions_list_in_range = calculate_diamond_area(base_position, range_value, self.battlemap)
        return [
            hero
            for hero in self.heroes
            if hero.position in positions_list_in_range and hero.player_id != actor_instance.player_id
        ]

    def get_enemies_in_square_range(self, actor_instance, base_position, range_value: int) -> List[Hero]:
        positions_list_in_range = calculate_square_area(base_position, range_value)
        return [
            hero
            for hero in self.heroes
            if hero.position in positions_list_in_range and hero.player_id != actor_instance.player_id
        ]

    def get_enemies_in_cross_range(self, actor_instance: Hero, range_value: int) -> List[Hero]:
        base_position = actor_instance.position
        positions_list_in_range = calculate_cross_area(base_position, range_value)
        return [
            hero
            for hero in self.heroes
            if hero.position in positions_list_in_range and hero.player_id != actor_instance.player_id
        ]

    def get_partner_in_square_range(self, actor_instance: Hero, range_value: int) -> List[Hero]:
        base_position = actor_instance.position
        positions_list_in_range = calculate_square_area(base_position, range_value)
        return [
            hero
            for hero in self.heroes
            if hero.position in positions_list_in_range and hero.player_id == actor_instance.player_id
        ]

    def load_buffs(self):
        from open_spiel.python.games.Tiandijie.primitives.buff.buffs import BuffTemps

        all_buffs = {}
        harm_buffs = []
        benefit_buffs = {}
        fieldbuffs = {}
        for buff in BuffTemps:
            all_buffs[buff.value.id] = buff.value
            if buff.value.type == BuffTypes.Harm:
                harm_buffs.append(buff.value)
            elif buff.value.type == BuffTypes.Benefit:
                benefit_buffs[buff.value.id] = buff.value
        self.all_buffs_temps = all_buffs
        self.harm_buffs_temps = harm_buffs
        self.benefit_buffs_temps = benefit_buffs
        from open_spiel.python.games.Tiandijie.primitives.fieldbuff.fieldbuffs import FieldBuffsTemps

        for buff in FieldBuffsTemps:
            fieldbuffs[buff.value.id] = buff.value
        self.fieldbuffs_temps = fieldbuffs

    def init_heroes(self, heroes: List[Hero]):
        self.heroes = heroes

    def get_current_player_id(self) -> int:
        return self.get_last_action().player_id

    def get_counter_player_id(self) -> int:
        return 1 - self.get_current_player_id()

    def get_formation_by_player_id(self, player_id: int) -> Formation:
        formations = [
            formation
            for formation in self.formation
            if formation.player_id == player_id
        ]
        from open_spiel.python.games.Tiandijie.helpers import random_select
        return random_select(formations, 1)[0] if formations else None

    def get_heroes_by_player_id(self, player_id: int) -> List[Hero]:
        return [hero for hero in self.heroes if hero.player_id == player_id]

    def get_died_heroes_by_player_id(self, player_id: int) -> List[Hero]:
        return [hero for hero in self.cemetery if hero.player_id == player_id]

    def get_heroes_by_counter_player_id(self, player_id: int) -> List[Hero]:
        return [hero for hero in self.heroes if hero.player_id != player_id]

    def set_hero_died(self, hero: Hero):
        if not hero.is_alive:
            return
        hero.is_alive = False
        # print(hero.id, "died in position", hero.position)
        self.heroes.remove(hero)
        self.cemetery.append(hero)
        self.battlemap.remove_hero(hero.position)

    def get_actor_by_side_in_battle(self, is_attacker: bool) -> Hero:
        current_action = self.get_last_action()
        if is_attacker:
            return current_action.actor
        else:
            return current_action.target[0]

    def get_targets_by_id(self, hero_id: str) -> List[Hero]:
        current_action = self.get_last_action()
        if current_action.is_attacker(hero_id):
            return current_action.targets
        else:
            return [current_action.actor]

    def get_hero_by_id(self, hero_id: str) -> Hero:
        target = None
        for hero in self.heroes:
            if hero.id == hero_id:
                target = hero
        for hero in self.cemetery:
            if hero.id == hero_id:
                target = hero
        return target

    def get_hero_list_by_id(self, hero_id: str) -> List[Hero]:
        return [hero for hero in self.heroes if hero.temp.temp_id == hero_id]

    def teleport_hero(self, hero, new_position):
        old_position = hero.position
        hero.position = new_position
        # print(hero.id, old_position, new_position)
        self.battlemap.hero_move(old_position, new_position)

    def init_formation(self):
        for hero in self.heroes:
            formation_temp = hero.temp.formation_temp
            if hero.temp.has_formation:
                heroes = self.get_heroes_by_player_id(hero.player_id)
                requirements = (
                    formation_temp.activation_requirements
                )  # [{'profession': Professions.SORCERER}, {'profession': Professions.GUARD}]

                # Remove the current hero from the check to only consider other heroes
                other_heroes = [h for h in heroes if h != hero]

                def is_requirement_satisfied(req, check_heroes):
                    key = next(iter(req))
                    return sum(
                        getattr(h.temp, key, None) == req[key] for h in check_heroes
                    )

                # Count how many times each requirement appears
                req_counts = Counter(
                    str(req) for req in requirements
                )  # Convert dict to str for immutability

                # Check each unique requirement against the number of heroes that satisfy it
                satisfied_counts = Counter(
                    {
                        str(req): is_requirement_satisfied(req, other_heroes)
                        for req in requirements
                    }
                )
                # Ensure for each requirement type, the number of heroes that satisfy it meets or exceeds the requirement count
                if all(
                        satisfied_counts[str(req)] >= count
                        for req, count in req_counts.items()
                ):
                    formation = Formation(hero.player_id, formation_temp)
                    formation.active_formation()
                    self.formation.append(formation)

    def get_harm_buff_temp_by_id(self, buff_temp_id: str) -> BuffTemp:
        for buff in self.harm_buffs_temps:
            if buff.id == buff_temp_id:
                return buff

    def get_buff_by_id(self, buff_id: str) -> BuffTemp:
        return self.all_buffs_temps[buff_id]

    def get_field_buff_temp_by_id(self, buff_id: str) -> FieldBuffTemp:
        return self.fieldbuffs_temps[buff_id]

    def get_enemy_by_id(self, hero: Hero, hero_id: str) -> Hero:
        return [
            h for h in self.heroes if h.id == hero_id and h.player_id != hero.player_id
        ][0]

    def get_enemy_list_by_id(self, player_id: int) -> [Hero]:
        return [h for h in self.heroes if h.player_id != player_id]

    def init_battlemap(self, map_id: str):
        if not map_id:
            map_id = round(random.random() * 10)
        initial_terrain_map = getattr(Maps, map_id).value
        self.battlemap = BattleMap(11, 11, initial_terrain_map)

    def init_game_heroes(self):
        from open_spiel.python.games.Tiandijie.primitives.Passive import Passives
        hero_list = []
        mohuahuangfushen = Hero(
            0,
            HeroeTemps.mohuahuangfushen.value,
            (8, 2),
            [Equipments.monibaozhu.value, Equipments.dingbizan.value,
             Equipments.xuanqueyaodai.value, Equipments.sheshoulingjie_yan.value]
        )
        mohuahuangfushen.enabled_passives = [Passives.sanquehuisheng.value]
        mohuahuangfushen.enabled_skills = [Skill(0, Skills.anshayouyan.value), Skill(0, Skills.leiyinwanyu.value)]
        mohuahuangfushen.stones = [Stones.get_stone_by_id("wanghuan"), Stones.get_stone_by_id("wanghuan"),
                                   Stones.get_stone_by_id("wanghuan")]
        hero_list.append(mohuahuangfushen)

        fuyayu = Hero(
            0,
            HeroeTemps.fuyayu.value,
            (8, 1),
            # (8, 9),
            [Equipments.longguxianglian_chen.value, Equipments.pixieyupei_yan.value,
             Equipments.jiaorenbeige_yan.value, Equipments.youyaoxiuhuan.value]
        )
        fuyayu.enabled_passives = []
        fuyayu.enabled_skills = [Skill(0, Skills.shenqiliuzhuan.value), Skill(0, Skills.zaizhouhaoling.value),
                                 Skill(0, Skills.liwankuanglan.value)]
        fuyayu.stones = [Stones.get_stone_by_id("minkui"), Stones.get_stone_by_id("minkui"),
                         Stones.get_stone_by_id("minkui")]
        hero_list.append(fuyayu)

        huoyong = Hero(
            0,
            HeroeTemps.huoyong.value,
            (8, 0),
            [Equipments.tianhezhusha.value, Equipments.qingshenjingyu.value,
             Equipments.tianjingfuhun.value, Equipments.zhongyaoyuzhuo.value]
        )
        huoyong.enabled_passives = [Passives.bianmou.value]

        huoyong.enabled_skills = [Skill(0, Skills.huntiantuixing.value), Skill(0, Skills.lihuoshenjue.value), Skill(0, Skills.wutianheiyan.value), Skill(0, Skills.tianshuangxuewu.value)]
        huoyong.stones = [Stones.get_stone_by_id("yuanhu"), Stones.get_stone_by_id("yuanhu"),
                          Stones.get_stone_by_id("yuanhu")]
        hero_list.append(huoyong)

        zhenyin = Hero(
            0,
            HeroeTemps.zhenyin.value,
            (9, 1),
            [Equipments.feiquanmingyu.value, Equipments.lingyuepeihuan_yan.value,
             Equipments.yanshanpei.value, Equipments.huanniaojie.value]
        )
        zhenyin.enabled_passives = []
        # zhenyin.enabled_skills = [Skill(0, Skills.shiguizhaohuan.value), Skill(0, Skills.jingangfalun.value), Skill(0, Skills.diyuzhizhen.value)]
        zhenyin.enabled_skills = [Skill(0, Skills.jingangfalun.value), Skill(0, Skills.diyuzhizhen.value)]
        zhenyin.stones = [Stones.get_stone_by_id("zhoushibing"), Stones.get_stone_by_id("zhoushibing"), Stones.get_stone_by_id("zhoushibing")]
        hero_list.append(zhenyin)

        zhujin = Hero(
            0,
            HeroeTemps.zhujin.value,
            (9, 2),
            [Equipments.tianhezhusha.value, Equipments.yurenjinpei.value,
             Equipments.xuanqueyaodai.value, Equipments.shuangzhijie.value]
        )
        zhujin.enabled_passives = []
        zhujin.enabled_skills = [Skill(0, Skills.juezhanwushuang.value), Skill(0, Skills.yanranchuanyun.value), Skill(0, Skills.chiqilingyao.value)]
        zhujin.stones = [Stones.get_stone_by_id("zhuyanmohuo"),Stones.get_stone_by_id("zhuyanmohuo"),Stones.get_stone_by_id("zhuyanmohuo")]
        hero_list.append(zhujin)

        mohuahuangfushen = Hero(
            1,
            HeroeTemps.mohuahuangfushen.value,
            (2, 8),
            [Equipments.monibaozhu.value, Equipments.dingbizan.value,
             Equipments.xuanqueyaodai.value, Equipments.sheshoulingjie_yan.value]
        )
        mohuahuangfushen.enabled_passives = [Passives.sanquehuisheng.value]
        mohuahuangfushen.enabled_skills = [Skill(0, Skills.anshayouyan.value), Skill(0, Skills.leiyinwanyu.value)]
        mohuahuangfushen.stones = [Stones.get_stone_by_id("wanghuan"), Stones.get_stone_by_id("wanghuan"),
                                   Stones.get_stone_by_id("wanghuan")]
        hero_list.append(mohuahuangfushen)

        fuyayu = Hero(
            1,
            HeroeTemps.fuyayu.value,
            (2, 9),
            # (7, 10),
            [Equipments.binglinyinhuan_yan.value, Equipments.yuanyujinling.value,
             Equipments.xuanwuyu.value, Equipments.youyaoxiuhuan.value]
        )
        fuyayu.enabled_passives = []
        fuyayu.enabled_skills = [Skill(0, Skills.shenqiliuzhuan.value), Skill(0, Skills.zaizhouhaoling.value),
                                 Skill(0, Skills.liwankuanglan.value)]
        fuyayu.stones = [Stones.get_stone_by_id("minkui"), Stones.get_stone_by_id("minkui"),
                         Stones.get_stone_by_id("minkui")]
        hero_list.append(fuyayu)

        huoyong = Hero(
            1,
            HeroeTemps.huoyong.value,
            (2, 10),
            [Equipments.fengxiyaxuan.value, Equipments.canghaiyueming.value,
                              Equipments.tianjingfuhun.value, Equipments.yujilingzhuo_chen.value]
        )
        huoyong.enabled_passives = [Passives.bianmou.value]

        huoyong.enabled_skills = [Skill(0, Skills.huntiantuixing.value), Skill(0, Skills.lihuoshenjue.value), Skill(0, Skills.wutianheiyan.value), Skill(0, Skills.tianshuangxuewu.value)]
        huoyong.stones = [Stones.get_stone_by_id("zhuyanmohuo"), Stones.get_stone_by_id("zhuyanmohuo"),
                          Stones.get_stone_by_id("zhuyanmohuo")]
        hero_list.append(huoyong)

        zhenyin = Hero(
            1,
            HeroeTemps.zhenyin.value,
            (1, 8),
            # (7, 9),
            [Equipments.feiquanmingyu.value, Equipments.lingyuepeihuan_yan.value,
                              Equipments.yanshanpei.value, Equipments.huanniaojie.value]
        )
        zhenyin.enabled_passives = []
        # zhenyin.enabled_skills = [Skill(0, Skills.shiguizhaohuan.value), Skill(0, Skills.jingangfalun.value), Skill(0, Skills.diyuzhizhen.value)]
        zhenyin.enabled_skills = [Skill(0, Skills.jingangfalun.value), Skill(0, Skills.diyuzhizhen.value)]
        zhenyin.stones = [Stones.get_stone_by_id("zhoushibing"), Stones.get_stone_by_id("zhoushibing"), Stones.get_stone_by_id("zhoushibing")]
        hero_list.append(zhenyin)

        zhujin = Hero(
            1,
            HeroeTemps.zhujin.value,
            (1, 9),
            [Equipments.tianhezhusha.value, Equipments.xuanzhutianhu.value,
             Equipments.xuanqueyaodai.value, Equipments.yujilingzhuo_yan.value]
        )
        zhujin.enabled_passives = []
        zhujin.enabled_skills = [Skill(0, Skills.juezhanwushuang.value), Skill(0, Skills.chiqilingyao.value), Skill(0, Skills.yanranchuanyun.value)]
        zhujin.stones = [Stones.get_stone_by_id("yuanhu"),Stones.get_stone_by_id("yuanhu"),Stones.get_stone_by_id("yuanhu")]
        hero_list.append(zhujin)

        self.init_heroes(hero_list)

    def init_heroes_position(self):
        for hero in self.heroes:
            self.battlemap.add_hero(hero.position)

    def calculate_score(self, player: int) -> float:
        score = 0.0
        for hero in self.cemetery:
            if hero.player_id != player:
                score += 100000
        #         score += hero.receive_damage
        # for hero in self.heroes:
        #     if hero.player_id != player:
        #         score += hero.receive_damage
        return score

    def get_hero_by_hero_id(self, id: str) -> Hero:
        return [hero for hero in self.heroes if hero.id == id][0]

def transform_map_id(map_id: str):
    transform_rule = {"妖山幻境": "yaoshanhuanjing"}
    return transform_rule[map_id]