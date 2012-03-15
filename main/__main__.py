#! /usr/bin/env python2
# -*- coding: utf-8 -*-

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^#
# META GOES ABOVE              #
################################

##
# Things I still don't understand tagged as [why].
# Feel free to enlighten me by email or on #rgrd @ quakenet :]
##

#All changes to the code deviating from original tutorial by Michal Walczak are considered noticeware:
#You can use this code as is without any warranty, reuse it and sell it, but
#please send me a message that you did - mw@michalwalczak.eu. Thank you!

#Copyright (c) 2011, Joao Henriques
#All rights reserved.

#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * The names of its contributors may not be used to endorse or promote
#      products derived from this software without specific prior written
#      permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL JOAO HENRIQUES BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


#############################################################
#                                                           #
#   2011                                                    #
#                                                           #
#   All changes and final form by MICHAL WALCZAK            #
#                                                           #
#                                                           #
#   using                                                   #
#   Complete roguelike tutorial using python+libtcod        #
#   This program uses libtcod - doryen.eptalys.net/libtcod/ #
#   [More info and links in README file]                    #
#                                                           #
#   You can use the code at will as long as you give the    #
#    tutorial creator a credit.                             #
#                                                           #
#   If you want to make a fork, or use this game as a base  #
#    for your game - feel free to do so, just let me know.  #
#                                                           #
#   Contact me by email:                                    #
#                                                           #
#   mw.michalwalczak@eu [exchange positions of @ and .]     #
#                                                           #
#   Visit my blog: http://michalwalczak.eu/                 #
#                                                           #
#############################################################

################################
# BODY GOES BELOW              #


################################
# FILE IMPORT                  #
################################

import thirdparty.libtcodpy as libtcod #libtcod import, and rename
import math #for math, duh
import textwrap #for messages

################################
# CONSTANTS                    #
################################

#tile
GAME_TITLE = 'Warden'
VERSION = '0.0.1'

#DEBUG
DEBUG_NO_FOG = False

#FPS maximum
LIMIT_FPS = 100

#console size
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#on-screen map size within above
MAP_WIDTH = 80
MAP_HEIGHT = 40

#min/max room dimensions (both horizontal and vertical)
ROOM_MAX_SIZE = 9
ROOM_MIN_SIZE = 5
MAX_ROOMS = 100 #max rooms number per map

#FOV settings
FOV_ALGO = 0 #default libtcod FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10 #fov range

#walls/floor colours
#those are a bit misleading, check 'render_all()'
color_dark_wall = libtcod.Color(15,12,7)
color_light_wall = libtcod.darkest_grey
color_dark_ground = libtcod.Color(15,12,7)
color_light_ground = libtcod.darkest_grey

HIGHLIGHT_COLOR = libtcod.dark_grey

#max number of monsters per room
MAX_ROOM_MONSTERS = 10

#max number of items spawned per room
MAX_ROOM_ITEMS = 2

#GUI sizes and coordinates
BAR_WIDTH = 20 #standard HP/MANA/whatever bar width
PANEL_HEIGHT = 10 #bottom panel height
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT #bottom panel placement

#message log constants
MSG_X = BAR_WIDTH + 2 #where message log starts (x)
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2 #max msg lenght (from hp bar)
MSG_HEIGHT = PANEL_HEIGHT - 2 #top message placement (y)

#menu constants
INVENTORY_WIDTH = 50

CONFUSE_NUM_TURNS = 5

#tab-look variable declaration
interest_names = '0'
interest_pos = '0'
interest_cycle = 0
highlight = 0
old_highlight_tab = None
old_mouse_x = 0
old_mouse_y = 0

high = ord('a')

PLAYER_NAME = "player"

################################
# CLASSES                      #
################################

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None, highlight=None):
        self.blocked = blocked
        self.explored = False
        self.highlight = highlight

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Rect:
    #a rectangle on a map used to make rooms
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    #calculate the center of a room
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
    #returns true if this rectangle intersects with one another
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)

class Object:
    #any entity represented by a character
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None):
        self.name = name
        self.blocks = blocks
        self.always_visible = always_visible
        self.x = x
        self.y = y
        self.char = char
        self.color = color

        self.fighter = fighter
        if self.fighter: #let's the fighter component 'know who owns it'
            self.fighter.owner = self

        self.ai = ai
        if self.ai: #let AI component know who owns it
            self.ai.owner = self

        self.item = item
        if self.item: #let the Item component know who owns it
            self.item.owner = self

    def move(self, dx, dy):
        #moving by given amount
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y):
        #return a vector and distance to target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize the vector to lenght 1 (preserving directors)
        #round and convert to integer
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def is_cardinal(self, target_x, target_y):
        #check if the target tile is in cardinal direction from self
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        target = (dx,dy)

        if target == (1,1):
            return False
        elif target == (-1,1):
            return False
        elif target == (-1,-1):
            return False
        elif target == (1,-1):
            return False
        else:
            return True

    def distance_to(self, other):
        #return the distance to another object (euclidean, and float!)
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        return dist

    def draw(self):
        #if visible to the player, or explored and always visible
        if libtcod.map_is_in_fov(fov_map, self.x, self.y) or (self.always_visible and map[self.x][self.y].explored):
            libtcod.console_set_default_foreground(con, self.color)
            if map[self.x][self.y].highlight == None:
                libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
            else:
                libtcod.console_put_char(con, self.x, self.y, self.char, HIGHLIGHT_COLOR)

    def clear(self):
        #clear the sign
        if libtcod.map_is_in_fov(fov_map, self.x, self.y) and map[self.x][self.y].highlight == None:
            libtcod.console_put_char_ex(con, self.x, self.y, '.', libtcod.grey, color_light_ground)
        elif libtcod.map_is_in_fov(fov_map, self.x, self.y) and map[self.x][self.y].highlight == True:
            libtcod.console_put_char_ex(con, self.x, self.y, '.', libtcod.grey, HIGHLIGHT_COLOR)

    def send_to_back(self):
        #make this obcject drawn first so it appears beneath everything else
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def distance(self, x, y):
        #return the distance to given coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

################################
# COMPONENT CLASSES            #
################################

#fighting abilities class
class Fighter:
    def __init__(self, hp, stamina, power, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.stamina = stamina
        self.max_stamina = stamina
        self.power = power
        self.max_power = power
        self.death_function = death_function

    def take_damage(self, damage):
        #apply damage if possible
        if damage > 0:
            self.hp -= damage

            #check for death, if there's death function call it
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)

    #cauchy distribution attack formula, should work neatly
    def attack(self, target):
        victim = target.fighter #lets give the target an easier callname
        damage = 0

        tohit = math.atan((float(self.power) - float(victim.power)/(5.0)))/math.pi + 0.5
        #main system function + crit bonus below
        if self.power > victim.power:
            diff = self.power - victim.power
            crit_table = [2,3,5,8,13,21,34,55,89,95,100]
            crit_chance = crit_table[diff-1]
            if libtcod.random_get_int(0,0,100) < crit_chance:
                tohit = tohit + float(crit_table[diff-1] * 0.01)

        rand = libtcod.random_get_float(0, 0.0, 1.0) #get a random number to calculate the hit

        if rand <= tohit: #set damage
            if self.owner.char == '@':
                damage = 3
            else:
                message(target.name.capitalize() + ' blocks the ' + self.owner.name + "'s attack!", libtcod.light_blue)
                target.fighter.tire_down()

        else:
            message(self.owner.name.capitalize() + ' misses!', libtcod.light_blue)
            if self.owner.char == '@':
                self.tire_down()

        #apply damage
        if damage == 3:
            message(self.owner.name.capitalize() + ' slashes ' + target.name + '!')
            victim.take_damage(damage)


    def heal(self, amount):
        #heal by given amount without going over max
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def rest(self, amount):
        #rest a given amount without going over max
        if game_state == "playing":
            self.stamina += amount
            if self.stamina > self.max_stamina:
                self.stamina = self.max_stamina

    def tire_down(self):
        if self.stamina - 5 < 0:
            self.stamina = 0
            message(self.owner.name.capitalize() + " is exhausted by the attacks!", libtcod.red)
        else:
            self.stamina -= 5

        if self.stamina == 0:
            if self.power - 1 < 0:
                self.power = 0
            else:
                self.power -= 1

            if self.power <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)
            else:
                message(self.owner.name.capitalize() + " is severly wounded by the attack, but fights on with new strength!", libtcod.dark_purple)
                self.stamina += 10

#basic pathfinding AI for monsters
class Pathfinder:
    def __init__(self, alerted = 0, last_x=None, last_y=None):
        self.alerted = alerted
        self.last_x = last_x
        self.last_y = last_y

    def take_turn(self):
        monster = self.owner
        libtcod.map_set_properties(fov_map, monster.x, monster.y, not map[monster.x][monster.y].block_sight, True) #unlock own tile before move

        if not monster.fighter.stamina + 0.1 >= monster.fighter.max_stamina:
            monster.fighter.stamina += 0.1
        else: monster.fighter.stamina = monster.fighter.max_stamina

        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            #player in view
            self.alerted = 5 #stay alert for 5 turns
            self.last_x = player.x #remember player's last position
            self.last_y = player.y
            libtcod.dijkstra_compute(path_map, monster.x, monster.y)
            libtcod.dijkstra_path_set(path_map, self.last_x, self.last_y)
            #compute and set path to the player
            if path_map is not False: #if there is a possible path
                x,y = libtcod.dijkstra_get(path_map, 0) #get next tile from path
                if monster.distance_to(player) > 1: #if player is away
                    if not is_blocked(x,y): #if next tile is not blocked
                        monster.move_towards(x,y) #move to next tile
                    else: #if it is blocked, move in random direction
                        dir = random_step()
                        monster.move(dir[0],dir[1])
                elif player.fighter.power > 0 and monster.is_cardinal(player.x, player.y) == True:
                #if player is alive and in cardinal direction - attack
                    monster.fighter.attack(player)
        elif self.alerted >= 1 and not libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
        #if lost sight of the player and alerted
            self.alerted = self.alerted - 1 #decrease the alert level
            libtcod.dijkstra_compute(path_map, monster.x, monster.y)
            libtcod.dijkstra_path_set(path_map, self.last_x, self.last_y)
            #move towards the player's last known position or stumble around if impossible
            if path_map is not False:
                x,y = libtcod.dijkstra_get(path_map, 0)
                if not is_blocked(x,y):
                    monster.move_towards(x,y)
                else:
                    dir = random_step()
                    monster.move(dir[0],dir[1])

        else: #move in random direction if left all alone
            dir = random_step()
            monster.move(dir[0],dir[1])

        #finally, block the tile so other monsters can path around it
        libtcod.map_set_properties(fov_map, monster.x, monster.y, not map[monster.x][monster.y].block_sight, False)

#AI for any temporarily confused monster
class ConfusedMonster:
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        libtcod.map_set_properties(fov_map, self.owner.x, self.owner.y, not map[self.owner.x][self.owner.y].block_sight, True)

        if self.num_turns > 0: #if still confused
            #move in random direction, decrease the number of confusion turns left
            dir = random_step()
            self.owner.move(dir[0],dir[1])
            self.num_turns -= 1

        else: #restore to previous AI
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' does not look confused anymore!', libtcod.red)
        libtcod.map_set_properties(fov_map, self.owner.x, self.owner.y, not map[self.owner.x][self.owner.y].block_sight, False)

#an item that can be picked up and used
class Item:
    def __init__(self, use_function=None, wear_function=None, remove_function=None, value=0):
        self.use_function = use_function
        self.wear_function = wear_function
        self.remove_function = remove_function
        self.value = value

    def pick_up(self):
        #add to the inventory, remove from the map
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.' + 'Drop something to be able to pick it up.', libtcod.red)
        else:
            if not self.owner.name == 'hole':
                inventory.append(self.owner)
                objects.remove(self.owner)
                message('You picked up a ' + self.owner.name + '!', libtcod.green)
            else:
                message('You cannot pick up the hole, who gave you that idea?', libtcod.white)

    def drop(self):
        #add to the map and remove from the player's inventory, placing item at the players coordinates
        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

    def use(self):
        #call 'use_function' if defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                if not self.owner.name == 'hole':
                    inventory.remove(self.owner) #destroy after use, unless the action has been cancelled

    def wear(self):
        #call 'wear_function' if defined
        if self.wear_function is None:
            message('The ' + self.owner.name + ' cannot be worn.')
        else:
            if self.wear_function(self.value) != 'cancelled':
                inventory.remove(self.owner)
                equipment.append(self.owner)
                message('You are now wearing/wielding ' + self.owner.name + '.')
            else:
                message('Remove item of that type first.', libtcod.red)

    def remove(self):
        #remove (unworn/unwield)
        if self.remove_function is None:
            message('The ' + self.owner.name + ' cannot be removed.')
        else:
            if self.remove_function(self.value) != 'cancelled':
                equipment.remove(self.owner)
                inventory.append(self.owner)
                message('You are no longer wearing/wielding ' + self.owner.name + '.')

################################
# FUNCTIONS                    #
################################

#room creation function
def create_room(room):
    global map
    for x in range(room.x1 + 1, room.x2):
       for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

#horizontal tunnel creation between rooms
def create_h_tunnel(x1, x2, y):
    global map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

#vertical tunnel creation between rooms
def create_v_tunnel(y1, y2, x):
    global map
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

#map generation function
def make_map():
    global map, objects, num_rooms, hole

    #the list of objects with just the player
    objects = [player]

    #fill map with "blocked" tiles
    map = [[ Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    rooms = []
    num_rooms = 0

    #room carving
    for r in range(MAX_ROOMS):
        #random width and height of the room
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        #"Rect" class makes rectangles easier to work with
        #[why] Check what Rect does, and how it handles rectangles.
        new_room = Rect(x, y, w, h)

        #run through the other rooms and see if they intersect with this one
        intersection = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                intersection = True
                break

        if not intersection:
            #this means there are no intersections, so this room is valid

            #"paint" it to the map's tiles
            create_room(new_room)

            #fill the room with monsters
            place_objects(new_room)

            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                #this is the first room, where the player starts at
                #places the @ here
                player.x = new_x
                player.y = new_y
            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel

                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms-1].center()

                #draw a coin (random number that is either 0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #coin=1
                    #first move horizontally, than vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #coin=0
                    #first move vertically, than horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    #place the hole in the last room
    item_component = Item(use_function=new_level)

    hole = Object(new_x, new_y, 'O', 'hole', libtcod.yellow, item=item_component, always_visible=True)

    objects.append(hole)
    hole.send_to_back()

#object generator function
def place_objects(room):
    global num_rooms
    #choose a random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    if not num_rooms == 0:
        for i in range(num_monsters):
            #choose a random spot in the room for a spawn
            x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
            y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

            #only place anything if tile is not blocked
            if not is_blocked(x, y):
                #gen a random number
                roll_monster=libtcod.random_get_int(0, 0, 100)

                if roll_monster < 10:
                    #create an ogre
                    fighter_component = Fighter(hp=4, stamina=10, power=12, death_function=monster_death)
                    ai_component = Pathfinder()

                    monster = Object(x, y, 'O', 'ogre', libtcod.darker_red, blocks=True, fighter=fighter_component, ai=ai_component)
                elif roll_monster < 10+55:
                    #create a hurlock
                    fighter_component = Fighter(hp=3, stamina=10, power=8, death_function=monster_death)
                    ai_component = Pathfinder()

                    monster = Object(x, y, 'H', 'hurlock', libtcod.dark_orange * libtcod.light_grey, blocks=True, fighter=fighter_component, ai=ai_component)
                else:
                    #create a genlock
                    fighter_component = Fighter(hp=3, stamina=10, power=6, death_function=monster_death)
                    ai_component = Pathfinder()

                    monster = Object(x, y, 'g', 'genlock', libtcod.dark_green, blocks=True,
                        fighter=fighter_component, ai=ai_component)

                objects.append(monster)

"""
    #choose a random number of items
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

    for i in range(num_items):
        #choose a random spot for an item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        #only place if the tile is not blocked already
        if not is_blocked(x, y):
            roll_item = libtcod.random_get_int(0, 0, 100)
            if roll_item < 30:
                #70% chance to create a healing potion
                item_component = Item(use_function=cast_heal)
                item = Object(x, y, '!', 'healing potion', libtcod.light_red, item=item_component)

            elif roll_item < 30+10:
                #create a lightning bolt scroll (10% chance)
                item_component = Item(use_function=cast_lightning)

                item = Object(x, y, '#', 'scroll of lightning', libtcod.light_yellow, item=item_component)

            elif roll_item < 30+10+10:
                #create a fireball scroll (10% chance)
                item_component = Item(use_function=cast_fireball)

                item = Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)

            elif roll_item < 30+10+10+10:
                #create a confuse scroll (10% chance)
                item_component = Item(use_function=cast_confuse)

                item = Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)

            elif roll_item < 30+10+10+10+20:
                #create a leather armor
                item_component = Item(wear_function=wear_armor, remove_function=remove_armor, value=1)

                item = Object(x, y, '{', 'leather armor', libtcod.light_orange, item=item_component)

            else:
                #create an iron armor
                item_component = Item(wear_function=wield_weapon, remove_function=remove_weapon, value=1)

                item = Object(x, y, '/', 'short sword', libtcod.white, item=item_component)
            objects.append(item)
            item.send_to_back() #items appear below monsters/player/corpses
            item.always_visible = True #items are visible even out of FOV
"""

#rendering function
def render_all():
    global fov_map
    global color_dark_wall
    global color_dark_ground
    global color_light_wall
    global color_light_ground
    global fov_recompute
    global highlight

    if fov_recompute:
       for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                map[x][y].highlight = None

    if fov_recompute:
        #recompute FOV if needed (player moved, etc.)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        #go through all tiles, and set their background color and char according to FOV
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    if map[x][y].explored:
                        #out of FOV
                        if wall:
                            libtcod.console_put_char_ex(con, x, y, '#', color_dark_wall, libtcod.darkest_sepia)
                        else:
                            libtcod.console_put_char_ex(con, x, y, '.', libtcod.dark_sepia, color_dark_ground)
                else:
                    #it's visible
                    #[TODO] create FOV fall-off
                    if not map[x][y].highlight == True:
                        if wall:
                            libtcod.console_put_char_ex(con, x, y, '#', color_light_wall, libtcod.grey * 0.75)
                        else:
                            libtcod.console_put_char_ex(con, x, y, '.', libtcod.grey, color_light_ground)
                    else:
                        libtcod.console_put_char_ex(con, x, y, '.', libtcod.grey, HIGHLIGHT_COLOR)
                    #since visible, explore
                    map[x][y].explored = True

    #draw all objects in the list, except the player that is drawn AFTER everything else
    for object in objects:
        if object != player:
            object.draw()
    player.draw()

    #blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    ###############################
    # BOTTOM PANEL
    ###############################

    #prepare the bottom panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    libtcod.console_hline(panel, 0, 0, SCREEN_WIDTH)

    libtcod.console_print_ex(panel, 1, 1, libtcod.BKGND_NONE, libtcod.LEFT, player.name.capitalize())

    render_bar(1, 3, BAR_WIDTH, 'STAMINA', player.fighter.stamina, player.fighter.max_stamina, libtcod.dark_red, libtcod.darkest_red, panel)
    render_bar(1, 4, BAR_WIDTH, 'POWER', player.fighter.power, player.fighter.max_power, libtcod.silver, libtcod.darkest_grey * 0.5, panel)

    libtcod.console_print_ex(panel, 1, 6, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level: ' + str(d_level))
    libtcod.console_print_ex(panel, 1, 7, libtcod.BKGND_NONE, libtcod.LEFT, 'Turns passed: ' + str(turns_passed))
    libtcod.console_print_ex(panel, 1, 8, libtcod.BKGND_NONE, libtcod.LEFT, 'Killing spree: ' + str(monsters_killed))

    #print the game messages, one line at a time
    y = 2
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    mouselook = get_names_under_mouse()
    if len(mouselook) >= 1:
        libtcod.console_print_ex(panel, MSG_X, 1, libtcod.BKGND_NONE, libtcod.LEFT, 'You are looking at: ' + mouselook)

    #blit panel's contents to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

#keystrokes function
def handle_keys():
    global fov_recompute, pick_list, high

    key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
    key_char = chr(key.c)

    #toggle fullscreen
    if key.vk == libtcod.KEY_F11:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    #exit game
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'

    #if the game is playing
    if game_state == 'playing':
        #movement keys
        #numpad, arrows, vim
        if key.vk == libtcod.KEY_KP8 or key.vk == libtcod.KEY_UP or key_char == 'j':
            player_move_or_attack(0, -1)

        elif key.vk == libtcod.KEY_KP2 or key.vk == libtcod.KEY_DOWN or key_char == 'k':
            player_move_or_attack(0, 1)

        elif key.vk == libtcod.KEY_KP4 or key.vk == libtcod.KEY_LEFT or key_char == 'h':
            player_move_or_attack(-1, 0)

        elif key.vk == libtcod.KEY_KP6 or key.vk == libtcod.KEY_RIGHT or key_char == 'l':
            player_move_or_attack(1, 0)

        elif key.vk == libtcod.KEY_KP5 or key.vk == libtcod.KEY_SPACE: #KP_5, SPACE - wait a turn
            player.move(0, 0)
            message('You wait a turn.', libtcod.white)
            player.fighter.rest(5)
            fov_recompute = True

        else:
            #test for other keys
            """
            if key_char == 'g':
                pick_list = []
                #pick up an item
                for object in objects: #look for an item in player's tile
                    if object.x == player.x and object.y == player.y and object.item:
                        pick_list.append(object)

                #if there's only one item, pick it up instantly
                if len(pick_list) == 1:
                    pick_list[0].item.pick_up()
                    return True

                #if there's more, display a menu to chose one
                elif len(pick_list) > 1:
                    high = ord('a')
                    chosen_item = pickup_menu('Choose an item to pick up.\n')
                    if chosen_item is not None:
                        chosen_item.item.pick_up()
                        return True

            if key_char == 'a':
                #show the inventory, if an item is selected, use it
                high = ord('a')
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()
                    return True

            if key_char == 'w':
                #show the inventory, let player wear the items
                high = ord('a')
                chosen_item = inventory_menu('Press the key next to an item to wear it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.wear()
                    return True

            if key_char == 'r':
                #show the equipment screen, let the player remove the one he chose
                high = ord('a')
                chosen_item = equipment_menu('Press the key next to an item to remove it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.remove()
                    return True

            if key_char == 'd':
                #show the inventory, if an item is selected, drop it
                high = ord('a')
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()
                    return True

            """

            if key_char == 'o':
                #find hole, and jump!
                for object in objects:
                    if object.x == player.x and object.y == player.y and object.name == 'hole':
                        object.item.use()
                        break

            if key_char == 'P':
                #screenshot, because I can
                libtcod.sys_save_screenshot()
                msgbox('\n Screenshot saved in game directory.\n', 37)

            if key.vk == libtcod.KEY_TAB:
                if not len(interest_names) < 1:
                    interest_tab(interest_pos[interest_cycle], interest_names[interest_cycle])
                else:
                    message('There is nothing of interest around you.', libtcod.white)

            if key.vk == libtcod.KEY_F1:
                #[TODO] HELP SCREEN
                pass

            if key_char == 'q':
                message(str(dice_roll(1,6)))

            return 'didnt-take-turn' #This makes sure that monsters don't take turn if player did not.

#movement and attacking
def player_move_or_attack(dx, dy):
    global fov_recompute, interest_cycle, didnttaketurn

    didnttaketurn = 0

    #the coordinates the player is moving to/attacking
    x = player.x + dx
    y = player.y + dy

    #check for attackable objects
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    #attack if target found
    if target is not None:
        player.fighter.attack(target)
    elif target is None and is_blocked(x,y):
        didnttaketurn = 1
    else:
        player.move(dx, dy)
        items = get_names_player_tile()
        if len(items) >= 1:
            message('On the floor here: ' + str(items))

        fov_recompute = True

#function that checks if the tile is blocked
def is_blocked(x, y):
    #check map tile first
    if map[x][y].blocked:
        return True

    #than check for blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

#GAME OVER MAN, GAME OVER
def player_death(player):
    global game_state
    message('You are dead! Press ESC to exit to main menu.', libtcod.red)
    game_state = 'dead'

    #visual corpse change
    player.char = '%'
    player.color = libtcod.darker_red

#monster death function
def monster_death(monster):
    global monsters_killed
    #transforms a dead mob into a non-blocking corpse that can't be attacked and doesn't move (yet)
    message(monster.name.capitalize() + ' is dead!', libtcod.orange)
    monster.char = '%'
    monster.color = libtcod.darker_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.always_visible = True
    monsters_killed += 1
    #make sure the spot where body lies is cleared for other monsters to move on
    libtcod.map_set_properties(fov_map, monster.x, monster.y, not map[monster.x][monster.y].block_sight, True)

    monster.send_to_back()

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color, console):
    #bar rendering function (hp/xp/mana, whatever)
    bar_width = int(float(value) / maximum * total_width)

    #render the background
    libtcod.console_set_default_background(console, back_color)
    libtcod.console_rect(console, x, y, total_width, 1, False, libtcod.BKGND_SET)

    #render the bar on top of that
    libtcod.console_set_default_background(console, bar_color)
    if bar_width > 0:
        libtcod.console_rect(console, x, y, bar_width, 1, False, libtcod.BKGND_SET)

    #text with values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(console, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER, name + ': ' + str(value))

#msgs handling function
def message(new_msg, color = libtcod.white):
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if buffer is full, remove the oldest line to make room for a new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #add the new line as a tuple, with the text and colour
        game_msgs.append( (line, color) )

#return a string with objects names that are under the mouse
def get_names_under_mouse():
    global highlight, old_highlight, old_mouse_x, old_mouse_y

    mouse = libtcod.Mouse()
    libtcod.sys_check_for_event(libtcod.EVENT_MOUSE_MOVE, libtcod.Key(), mouse)
    (x, y) = (mouse.cx, mouse.cy)


    if old_highlight != None:
        map[old_highlight[0]][old_highlight[1]].highlight = None

    highlight = 0
    if x <= 79 and y <= 39 and x >= 0 and y >= 0:
        map[x][y].highlight = True
        highlight = 1
        old_highlight = (x,y)

    #create a list of names of all objects at mouse's coordinates and in FOV
    names = [obj.name for obj in objects if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]

    names = ', ' .join(names) #join the names separated by commas
    return names.capitalize()

#return a string with objects names that are on the same tile as player
def get_names_player_tile():
    (x, y) = (player.x, player.y)

    names = [obj.name for obj in objects if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and not obj.char == '@']

    names = ', ' .join(names)
    return names.capitalize()

def interest_list():
    global interest_names, interest_pos

    interest_names = [obj.name for obj in objects if libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and not obj.char == '@']

    interest_pos = [(obj.x, obj.y) for obj in objects if libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and not obj.char == '@']

def interest_tab(position, name):
    global interest_cycle, highlight, old_highlight_tab

    if old_highlight != None:
        map[old_highlight_tab[0]][old_highlight_tab[1]].highlight = None
        map[old_highlight[0]][old_highlight[1]].highlight = None

    highlight = 0

    if not len(interest_names) - 1 < interest_cycle:

        message('You see ' + name + ' here.', libtcod.white)
        for object in objects:
            if object.x == position[0] and object.y == position[1]:
                map[position[0]][position[1]].highlight = True
                highlight = 1
                old_highlight_tab = (position[0],position[1])
        if len(interest_names) - 1 == interest_cycle:
            interest_cycle = 0
        else:
            interest_cycle += 1

#menu function - initially for the inventory screen
def menu(header, options, width):
    global high
    #debug exception is you try to make a menu with more than 26 options
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    #calculate total height for the header (auto-wraped), and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #creates an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
    libtcod.console_set_default_background(window, HIGHLIGHT_COLOR)
    #print the menu's options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        if not high == letter_index:
            libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        else:
            libtcod.console_print_ex(window, 0, y, libtcod.BKGND_SET, libtcod.LEFT, text)
        y += 1
        letter_index +=1

    #blit "window" contents to the root console
    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the console, and wait for a key-press
    libtcod.console_flush()

    mouse = libtcod.Mouse()
    key = libtcod.Key()
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_RELEASE | libtcod.EVENT_MOUSE, key, mouse)

    mouse_move = abs(mouse.dy) + abs(mouse.dx)

    if mouse_move > 2:
        if header_height != 0 and mouse.cy > y and mouse.cy < y+height:
            high = ord('a') + mouse.cy - y - header_height
            return 99
        else:
            high = ord('a') + mouse.cy - y
            return 99

    if mouse.lbutton_pressed:
        index = high - ord('a')
        if index >= 0 and index < len(options): return index

    if key.vk == libtcod.KEY_F11:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    if key.vk == libtcod.KEY_ESCAPE:
        return None

    if key.vk == libtcod.KEY_ENTER or key.vk == libtcod.KEY_KPENTER or key.vk == libtcod.KEY_SPACE:
        index = high - ord('a')
        if index >= 0 and index < len(options): return index

    if key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2 or chr(key.c) == 'k':
        if not high == letter_index -1:
            high += 1
            return 99
        else:
            return 99
    elif key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8 or chr(key.c) == 'j':
        if not high == ord('a'):
            high -= 1
            return 99
        else:
            return 99

    #convert ASCII code to an index; if it corresponds to an option - return that
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return 99

#inventory menu function (utilizes above)
def inventory_menu(header):
     while True:
        if len(inventory) ==  0:
            options = ['Inventory is empty.']

        else:
            options = [item.name for item in inventory]

        index = menu(header, options, INVENTORY_WIDTH)

        #if an item was chosen, return it
        if index is None or len(inventory) == 0: return None
        elif index == 99: continue
        else: return inventory[index].item

def pickup_menu(header):
    while True:
        options = [item.name for item in  pick_list]

        index = menu(header, options, INVENTORY_WIDTH)

        if index is None or len(pick_list) == 0: return None
        elif index == 99: continue
        else: return pick_list[index]

def equipment_menu(header):
    while True:
        if len(equipment) == 0:
            options = ['You are not wearing or wielding anything.']

        else:
            options = [item.name for item in equipment]

        index = menu(header, options, INVENTORY_WIDTH)

        #if an item was chosen, return it
        if index is None or len(equipment) == 0: return None
        elif index == 99: continue
        else: return equipment[index].item

#find the closest enemy, up to a maximum range in the player's FOV
def closest_monster(max_range):
    closest_enemy = None
    closest_dist = max_range + 1 #start with slightly more then maximum range

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
        #calculate the distance between the object and the player
            dist = player.distance_to(object)
            if dist < closest_dist: #it's closest, remember
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

#return the position of left-clicked tile in player's FOV/set range, None,None if right-clicked
def target_tile(max_range=None):
    while True:
        #render the screen erasing the inventory and showing the objects name under the mouse
        render_all()
        libtcod.console_flush()

        key = libtcod.console_check_for_keypress()
        mouse = libtcod.mouse_get_status() #get ouse position and click status
        (x, y) = (mouse.cx, mouse.cy)

        #accept the target if the player clicked in FOV and check for optional range
        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and
            (max_range is None or player.distance(x, y) <= max_range)):
            return(x, y)

        #cancel if player right-clicked or pressed Escape
        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            message('Cancelled.', libtcod.white)
            return (None, None)

#returns a clicked monster inside FOV or range, or None if right-clicked
def target_monster (max_range=None):
    while True:
        (x, y) = target_tile(max_range)
        if x is None: #player cancelled
            message('Cancelled.', libtcod.white)
            return None

        #return the first clicked monster, loop until you do
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj

def msgbox(text, width=50):
    menu(text, [], width) #uses menu() as a message box
    libtcod.sys_sleep_milli(1000)

#a simple win condition - kill enough monsters to win
def win_condition():
    if monsters_killed >= MONSTERS_TO_WIN:
        return True

#create a pathing map from the fov_map
def make_path_map():
    global path_map
    path_map = libtcod.dijkstra_new(fov_map, 0)

def random_step():
    #valid move directions (including waiting)
    wait = [0, 0]
    e = [0, 1]
    w = [0, -1]
    n = [1, 0]
    s = [-1, 0]
    valid = [wait, e, w, n, s]

    #get random index number
    index = libtcod.random_get_int(0,0,4)

    #extract the value from direction list
    dir = valid[index]

    return dir

def dice_roll(dices, sides):
    result = 0
    while not dices == 0:
        roll = libtcod.random_get_int(0, 1, sides)
        result = result + roll
        dices -= 1

    return result
################################
# Wearable Items               #
################################

def wield_weapon(rating):
    global weapon_wield
    if weapon_wield == False:
        player.fighter.power = player.fighter.power + rating
        weapon_wield = True
    else:
        return 'cancelled'

def remove_weapon(rating):
    global weapon_wield
    player.fighter.power = player.fighter.power - rating
    weapon_wield = False

def wear_armor(rating):
    global armor_worn
    if armor_worn == False:
        player.fighter.defense = player.fighter.defense + rating
        armor_worn = True
    else:
        return 'cancelled'

def remove_armor(rating):
    global armor_worn
    player.fighter.defense = player.fighter.defense - rating
    armor_worn = False

################################
# Magic Effects                #
################################

#player healing (by set amount)
#[why] should be easy enough to convert this to RNG value
def cast_heal():
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'

    heal = dice_roll(2,5) + 2

    message('Your wounds start to feel better!', libtcod.light_violet)
    player.fighter.heal(heal)

#lightning spell that finds closest enemy within a maximum range and deals damage
#[why] as with above, should be easy to tweak this to semi-random
def cast_lightning():
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None: #if no enemy is found within max range - cancel
        message('No enemy is close enough to strike with vengeance.', libtcod.red)
        return 'cancelled'

    #target found? light'em up!
    message('A lightning bolt strikes the ' + monster.name + ' with a loud thunder! The damage is ' + str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)

def cast_confuse():
    #ask the player to select a target for confuse spell
    message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(CONFUSE_RANGE)
    if monster is None: return 'cancelled'

    #replace the monster's AI with "confused"
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster #tell the new component who owns it
    message('The eyes of the ' + monster.name + ' look vacant, as it starts to stumble around!', libtcod.light_green)

def cast_fireball():
    #ask the player for a target tile to throw a fireball at
    message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', libtcod.orange)

    for obj in objects: #damage every fighter in range, including the player
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
            message('The ' + obj.name + ' gets burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
            obj.fighter.take_damage(FIREBALL_DAMAGE)


################################
# META-GAME FUNCTIONS          #
################################

def main_menu():
    img = libtcod.image_load('main/data/menu.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and credits
        libtcod.console_set_default_foreground(0, libtcod.light_grey)
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT-7, libtcod.BKGND_NONE, libtcod.CENTER, 'By Michal Walczak')

        #show options and wait for the player's choice
        choice = menu('   Choose an option:', ['Play a new game.', 'Highscores', 'Credits', 'Quit.'], 24)

        if choice == 0: #new game
            new_game()
            play_game()
        if choice == 1:
            msgbox('\n Not yet implemented. \n', 22)
        if choice == 2:
            msgbox('\n Not yet implemented. \n', 22)
        if choice == 3: #quit
            break

        libtcod.console_flush() #clear the console before redraw (fixes blacking out issue?

#new game initialisation
def new_game():
    global player, inventory, game_msgs, game_state, d_level, monsters_killed, win_print, equipment, weapon_wield, armor_worn, player_gold, highlight, old_highlight_tab, old_highlight, turns_passed, explheal, didnttaketurn

    PLAYER_NAME = input_box("Enter your name:", 30)
    if PLAYER_NAME == "":
        PLAYER_NAME = "player"

    #create a fighter component for the player, add a player @, state objects list
    fighter_component = Fighter(hp=20, stamina=100, power=10, death_function=player_death)
    player = Object(0, 0, "@", PLAYER_NAME, libtcod.silver * 1.5, blocks=True, fighter=fighter_component)

    #list for storing the game messages
    game_msgs = []

    #win variables
    monsters_killed = 0
    win_print = 0

    #gen the map
    make_map()

    #set the dungeon level to 1
    d_level = 1

    turns_passed = 0

    #gen fov map
    initialize_fov()

    #gen path map
    make_path_map()

    #game state variables
    game_state = 'playing'

    #inventory list
    inventory = []
    equipment = []
    weapon_wield = False
    armor_worn = False

    highlight = 0
    old_highlight = (0,0)
    old_highlight_tab = (0,0)
    old_mouse_x = 0
    old_mouse_y = 0

    didnttaketurn = 0

    #welcoming message
    message('Welcome, wanderer! Try not to die too early.', libtcod.red)

def new_level():
    global player, game_msgs, game_state, d_level

    make_map()
    d_level += 1 #add one to the dungeon level
    initialize_fov()
    make_path_map()
    game_state='playing'
    message('You jump into the hole to another level, and land with a *thump* on the floor below.', libtcod.red)

#as name says
def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True

    #create the FOV map, according to the generated map
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)
    libtcod.console_clear(con) #unexplored areas start black


    if DEBUG_NO_FOG:  #debug mode, reveal everything
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                map[x][y].explored = True
        for object in objects:
            object.always_visible = True

#main game function
def play_game():
    global game_state, win_print, highlight, interest_cycle, didnttaketurn, turns_passed
    player_action = None

    #Start main loop
    while not libtcod.console_is_window_closed():

        render_all() #render stuff

        interest_list()

        libtcod.console_flush() #refresh the console

        #erase before move
        for object in objects:
                object.clear()

        if interest_names == '0':
            interest_list()

        #import keys handling
        player_action = handle_keys()
        if player_action == None and didnttaketurn == 1:
            player_action = 'didnt-take-turn'
            didnttaketurn = 0
        if player_action == 'exit': #if pressing a key returns 'exit' - close the window
            break

        #let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            highlight = 0
            turns_passed += 1
            for object in objects:
                if object.ai:
                    object.ai.take_turn()

            interest_list()
            interest_cycle = 0

def input_box(header, width=50):
    timer = 0
    command = ""
    x = 1

    #calculate total height for the header (auto-wraped), and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = header_height + 3
    print(height)

    #creates an off-screen console that represents the menu's window
    in_box = libtcod.console_new(width, height)

    #print the header with auto-wrap
    libtcod.console_set_default_foreground(in_box, libtcod.white)
    libtcod.console_print_rect_ex(in_box, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)
    libtcod.console_set_default_background(in_box, HIGHLIGHT_COLOR)

    while True:
        libtcod.console_set_default_foreground(in_box, libtcod.white)
        libtcod.console_set_default_background(in_box, HIGHLIGHT_COLOR)

        timer += 1
        if timer % (LIMIT_FPS / 4) == 0:
            if timer % (LIMIT_FPS / 2) == 0:
                timer = 0
                libtcod.console_put_char(in_box, x, 2, "_")
            else:
                libtcod.console_put_char(in_box, x, 2, " ")

        key = libtcod.Key()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse())

        if key.vk == libtcod.KEY_BACKSPACE and x > 1:
            libtcod.console_put_char(in_box, x, 2, " ")
            command = command[:-1]
            x -= 1
        elif key.vk == libtcod.KEY_ENTER:
            if len(command) > 10:
                #msgbox("\n Chosen name is too long. \n", 28)
                libtcod.console_set_default_foreground(in_box, libtcod.lighter_red)
                libtcod.console_print_rect(in_box, 1, 1, width, 1, "Name too long. (max. 10)")
                libtcod.console_set_default_foreground(in_box, libtcod.white)
            else:
                break
        elif key.vk == libtcod.KEY_ESCAPE:
            command = ""
            break
        elif key.c > 0:
            letter = chr(key.c)
            libtcod.console_put_char(in_box, x, 2, letter)
            command += letter
            x += 1

        #blit "window" contents to the root console
        x_con = SCREEN_WIDTH/2 - width/2
        y_con = SCREEN_HEIGHT/2 - height/2
        libtcod.console_blit(in_box, 0, 0, width, height, 0, x_con, y_con, 1.0, 0.7)

        #present the console, and wait for a key-press
        libtcod.console_flush()

    print(command)
    return command

################################
# Initialization               #
################################

#font import, spawn window, window name, FPS (if real-time)
libtcod.console_set_custom_font('main/data/terminal16x16_gs_ro.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE)
#libtcod.console_set_custom_font('cont/arial12x12.png', libtcod.FONT_LAYOUT_TCOD | libtcod.FONT_TYPE_GRAYSCALE)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE + ' v.' + VERSION, False, renderer = libtcod.RENDERER_SDL)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT) #new console, used ALOT[why]
#bottom panel console
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

high = ord('a')
main_menu()

#End of the line.
