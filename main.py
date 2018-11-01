import random

import sc2
from sc2 import Race, Difficulty
from sc2.ids.ability_id import *
from sc2.ids.unit_typeid import *
from sc2.player import Bot, Computer


class Hydralisk(sc2.BotAI):
    def select_target(self):
        if self.known_enemy_structures.exists:
            return random.choice(self.known_enemy_structures).position

        return self.enemy_start_locations[0]

    async def on_step(self, iteration):
        if iteration == 0:
            townhall = self.townhalls.first if self.townhalls.exists else None
            drones = self.units(UnitTypeId.DRONE).closer_than(10.0, townhall)
            for drone in drones:
                await self.do(drone.hold_position())

            nearby_minerals = self.state.mineral_field.closer_than(10.0, townhall)
            sc2.logger.info(nearby_minerals)
            drones = self.units(UnitTypeId.DRONE).closer_than(10.0, townhall)
            for mineral in nearby_minerals:
                sc2.logger.info("{0}, {1}, {2}".format(mineral, mineral.assigned_harvesters, mineral.ideal_harvesters))
                for i in range(2):
                    if drones.exists:
                        closest_drone = drones.closest_to(mineral)
                        drones.remove(closest_drone)
                        await self.do(closest_drone.gather(mineral))


def main():
    sc2.run_game(sc2.maps.get("(2)CatalystLE"), [
        Bot(Race.Zerg, Hydralisk()),
        Computer(Race.Terran, Difficulty.Medium)
    ], realtime=False, save_replay_as="ZvT.SC2Replay")


if __name__ == '__main__':
    main()
