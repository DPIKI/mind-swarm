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
        larvae = self.units(UnitTypeId.LARVA)
        forces = self.units(UnitTypeId.ZERGLING) | self.units(UnitTypeId.HYDRALISK)

        if self.units(UnitTypeId.HYDRALISK).amount > 10 and iteration % 50 == 0:
            for unit in forces.idle:
                await self.do(unit.attack(self.select_target()))

        if self.supply_left < 2:
            if self.can_afford(UnitTypeId.OVERLORD) and larvae.exists:
                await self.do(larvae.random.train(UnitTypeId.OVERLORD))
                return

        if self.units(UnitTypeId.HYDRALISKDEN).ready.exists:
            if self.can_afford(UnitTypeId.HYDRALISK) and larvae.exists:
                await self.do(larvae.random.train(UnitTypeId.HYDRALISK))
                return

        if not self.townhalls.exists:
            for unit in self.units(UnitTypeId.DRONE) | self.units(UnitTypeId.QUEEN) | forces:
                await self.do(unit.attack(self.enemy_start_locations[0]))
            return
        else:
            hq = self.townhalls.first

        for queen in self.units(UnitTypeId.QUEEN).idle:
            abilities = await self.get_available_abilities(queen)
            if AbilityId.EFFECT_INJECTLARVA in abilities:
                await self.do(queen(UnitTypeId.EFFECT_INJECTLARVA, hq))

        if not (self.units(UnitTypeId.SPAWNINGPOOL).exists or self.already_pending(UnitTypeId.SPAWNINGPOOL)):
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self.build(UnitTypeId.SPAWNINGPOOL, near=hq.position)

        if self.units(UnitTypeId.SPAWNINGPOOL).ready.exists:
            if not self.units(UnitTypeId.LAIR).exists and hq.noqueue:
                if self.can_afford(UnitTypeId.LAIR):
                    await self.do(hq.build(UnitTypeId.LAIR))

        if self.units(UnitTypeId.LAIR).ready.exists:
            if not (self.units(UnitTypeId.HYDRALISKDEN).exists or self.already_pending(UnitTypeId.HYDRALISKDEN)):
                if self.can_afford(UnitTypeId.HYDRALISKDEN):
                    await self.build(UnitTypeId.HYDRALISKDEN, near=hq.position)

        if self.units(UnitTypeId.EXTRACTOR).amount < 2 and not self.already_pending(UnitTypeId.EXTRACTOR):
            if self.can_afford(UnitTypeId.EXTRACTOR):
                drone = self.workers.random
                target = self.state.vespene_geyser.closest_to(drone.position)
                err = await self.do(drone.build(UnitTypeId.EXTRACTOR, target))

        if hq.assigned_harvesters < hq.ideal_harvesters:
            if self.can_afford(UnitTypeId.DRONE) and larvae.exists:
                larva = larvae.random
                await self.do(larva.train(UnitTypeId.DRONE))
                return

        for a in self.units(UnitTypeId.EXTRACTOR):
            if a.assigned_harvesters < a.ideal_harvesters:
                w = self.workers.closer_than(20, a)
                if w.exists:
                    await self.do(w.random.gather(a))

        if self.units(UnitTypeId.SPAWNINGPOOL).ready.exists:
            if not self.units(UnitTypeId.QUEEN).exists and hq.is_ready and hq.noqueue:
                if self.can_afford(UnitTypeId.QUEEN):
                    await self.do(hq.train(UnitTypeId.QUEEN))

        if self.units(UnitTypeId.ZERGLING).amount < 20 and self.minerals > 1000:
            if larvae.exists and self.can_afford(UnitTypeId.ZERGLING):
                await self.do(larvae.random.train(UnitTypeId.ZERGLING))


def main():
    sc2.run_game(sc2.maps.get("(2)CatalystLE"), [
        Bot(Race.Zerg, Hydralisk()),
        Computer(Race.Terran, Difficulty.Medium)
    ], realtime=False, save_replay_as="ZvT.SC2Replay")


if __name__ == '__main__':
    main()
