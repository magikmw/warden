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

# Pretty stuff
# [TODO] Flash on hit
# [TODO] Add blood decals.

# WAT
# [FIX] SEGFAULTS
# [FIX] Segfault while entering next lv (8->9, cratuki, windows)
# [FIX] Segfaults (put print everywhere) - in progress
# [TODO] Balance tweaks
#       * change distribution of monster kind per lv
#       * reduce the size of levels
# [XXX] Side panel for stats, reduce size of screen altogether?
# [FIX] Keys not regged [Chaged to sys_check_for_event, added a debug message]
# [FIX?] srd| reported interface bork
# [XXX] Remove mouselook

################################
# BODY GOES BELOW              #


################################
# LOGGER INITIALIZATION        #
################################

import logging

# create a logger
logg = logging.getLogger('Main')
logg.setLevel(logging.DEBUG)

# create a handler and set level
logg_ch = logging.StreamHandler()
logg_fh = logging.FileHandler('warden.log', mode='a', encoding=None, delay=False)
logg_ch.setLevel(logging.INFO)
logg_fh.setLevel(logging.DEBUG)

# crate a formatter and add it to the handler
# [HH:MM:SS AM][LEVEL] Message string
logg_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%I:%M:%S')
logg_ch.setFormatter(logg_formatter)
logg_fh.setFormatter(logg_formatter)

# add ch to logger
logg.addHandler(logg_ch) #console handler at level INFO
logg.addHandler(logg_fh) #file handler at level DEBUG for more detail

# ready to go!
# logging convention:
# logg.debug('') for variable passing
# logg.info('') for standard initialization messages
# logg.warn('') for known errors and caught exceptions
# logg.error('') for something that shouldn't happen
# logg.critical('') for breakage errors

logg.info('Logging initialized.')

################################
# MODULE IMPORT                #
################################

logg.info('Module import initialized.')

import thirdparty.libtcodpy as libtcod #libtcod import, and rename
logg.debug('libTCOD initialized')
from math import pi, atan, sqrt #for math, duh
logg.debug('math initialized')
import textwrap #for messages
logg.debug('textwrap initialized')
import datetime
logg.debug('datetime initialized')

logg.info('All modules imported succesfully.')

################################
# CONSTANTS                    #
################################

logg.info('Constants initialization.')

#tile
GAME_TITLE = 'Warden'
VERSION = '1.1.1'

#DEBUG
DEBUG_NO_FOG = False
DEBUG_GOD_MODE = False

#FPS maximum
LIMIT_FPS = 20

#console size
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

#on-screen map size within above
MAP_WIDTH = 80
MAP_HEIGHT = 40

#min/max room dimensions (both horizontal and vertical)
ROOM_MAX_SIZE = 8
ROOM_MIN_SIZE = 5
MAX_ROOMS = 40 #max rooms number per map

#FOV settings
FOV_ALGO = 0 #default libtcod FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 8 #fov range

#walls/floor colours
#those are a bit misleading, check 'render_all()'
color_dark_wall = libtcod.Color(15,12,7)
color_light_wall = libtcod.darkest_grey
color_dark_ground = libtcod.Color(15,12,7)
color_light_ground = libtcod.darkest_grey

HIGHLIGHT_COLOR = libtcod.dark_grey

#max number of monsters per room
MAX_ROOM_MONSTERS = 5

#max number of items spawned per room
MAX_ROOM_ITEMS = 1

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
NUM_SHARDS = 4
NUM_POTIONS = 5
NUM_ARCH = 2
lv_feeling = 'none'

d_level = 1
got_key = True

fov_map = None
path_map = None

logg.info('Constants initialization finished.')

################################
# CLASSES                      #
################################

logg.info('Class initialization.')

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None, highlight=None):
        self.blocked = blocked
        self.explored = False
        self.highlight = highlight

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

logg.debug('Tile initialized.')

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

logg.debug('Rect initialized.')

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
        #logg.debug('move() called, %s, %s', dx, dy)
        #moving by given amount
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y):
        #logg.debug('move_towards() called, %s, %s', target_x, target_y)
        #return a vector and distance to target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = sqrt(dx ** 2 + dy ** 2)

        #normalize the vector to lenght 1 (preserving directors)
        #round and convert to integer
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def is_cardinal(self, target_x, target_y):
        #logg.debug('is_cardinal() called, %s, %s', target_x, target_y)
        #check if the target tile is in cardinal direction from self
        dx = target_x - self.x
        dy = target_y - self.y
        distance = sqrt(dx ** 2 + dy ** 2)

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
        #logg.debug('distance_to() called %s, %s', other.x, other.y)
        #return the distance to another object (euclidean, and float!)
        dx = other.x - self.x
        dy = other.y - self.y
        dist = sqrt(dx ** 2 + dy ** 2)
        return dist

    def draw(self):
        #logg.debug('draw() called')
        #if visible to the player, or explored and always visible
        #logg.debug('Method draw() called by %s, pos x: %s, y: %s', self.name, str(self.x), str(self.y))
        if libtcod.map_is_in_fov(fov_map, self.x, self.y) or (self.always_visible and map[self.x][self.y].explored):
            libtcod.console_set_default_foreground(con, self.color)
            if map[self.x][self.y].highlight == None:
                libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
            else:
                libtcod.console_put_char(con, self.x, self.y, self.char, HIGHLIGHT_COLOR)

    def clear(self):
        #logg.debug('clear() called')
        #clear the sign
        #logg.debug('Method clear() called by %s, pos x: %s, y: %s', self.name, str(self.x), str(self.y))
        if libtcod.map_is_in_fov(fov_map, self.x, self.y) and map[self.x][self.y].highlight == None:
            libtcod.console_put_char_ex(con, self.x, self.y, '.', libtcod.grey, color_light_ground)
        elif libtcod.map_is_in_fov(fov_map, self.x, self.y) and map[self.x][self.y].highlight == True:
            libtcod.console_put_char_ex(con, self.x, self.y, '.', libtcod.grey, HIGHLIGHT_COLOR)
        elif self.name == 'Archdemon':
            if map[self.x][self.y].explored == True:
                libtcod.console_put_char_ex(con, self.x, self.y, '.', libtcod.dark_sepia, color_dark_ground)
            else:
                libtcod.console_put_char_ex(con, self.x, self.y, ' ', libtcod.black, libtcod.black)

    def send_to_back(self):
        #logg.debug('send_to_back() called')
        #make this obcject drawn first so it appears beneath everything else
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def distance(self, x, y):
        #logg.debug('distance() called, %s, %s', x, y)
        #return the distance to given coordinates
        return sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

logg.debug('Object initialized.')

################################
# COMPONENT CLASSES            #
################################

logg.info('Component classes initialization.')

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
        #logg.debug('take_damage() called, %s', damage)
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
        #logg.debug('attack() called, %s', target.name)
        victim = target.fighter #lets give the target an easier callname
        damage = 0

        tohit = atan((float(self.power) - float(victim.power)/(5.0)))/pi + 0.5
        #main system function + crit bonus below
        if self.power > victim.power:
            diff = self.power - victim.power
            if diff > 11:
                tohit = 1.1
            else:
                crit_table = [2,3,5,8,13,21,34,55,89,95,100]
                crit_chance = crit_table[diff-1]
                if libtcod.random_get_int(0,0,100) < crit_chance:
                    tohit = tohit + float(crit_table[diff-1] * 0.01)

        rand = libtcod.random_get_float(0, 0.0, 1.0) #get a random number to calculate the hit

        if rand <= tohit: #set damage
            if self.owner.char == '@':
                damage = 3
            elif self.owner.char == 'A' and d_level < 10:
                message("Archdemon drains your lifeforce!", libtcod.light_blue)
                target.fighter.tire_down(100)
            elif self.owner.char == 'A' and d_level == 10:
                message("The Archdemon cripples you!", libtcod.light_blue)
                target.fighter.tire_down(25)
            else:
                message(target.name.capitalize() + ' blocks the ' + self.owner.name + "'s attack!", libtcod.light_blue)
                target.fighter.tire_down(5)

        else:
            message(self.owner.name.capitalize() + ' misses!', libtcod.light_blue)

        #apply damage
        if damage == 3:
            message(self.owner.name.capitalize() + ' slashes ' + target.name + '!', libtcod.light_blue)
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

    def tire_down(self, amount):
        if self.stamina - amount < 0:
            self.stamina = 0
        else:
            self.stamina -= amount

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
                message("The corruption and your wounds take their toll.", libtcod.dark_purple)
                self.stamina += 70

logg.debug('Fighter initialized.')

#basic pathfinding AI for monsters
class Pathfinder:
    def __init__(self, alerted = 0, last_x=None, last_y=None):
        self.alerted = alerted
        self.last_x = last_x
        self.last_y = last_y

    def take_turn(self):
        #logg.debug('Take turn called.')
        monster = self.owner
        libtcod.map_set_properties(fov_map, monster.x, monster.y, not map[monster.x][monster.y].block_sight, True) #unlock own tile before move

        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            #player in view
            self.alerted = 15 #stay alert for 5 turns
            self.last_x = player.x #remember player's last position
            self.last_y = player.y
            logg.debug('libtcod.path_compute() called by %s, pos x: %s, y: %s to x: %s, y: %s', monster.name, str(monster.x), str(monster.y), self.last_x, self.last_y)
            libtcod.path_compute(path_map, monster.x, monster.y, self.last_x, self.last_y)
            #compute and set path to the player
            x,y = libtcod.path_walk(path_map, True)
            logg.debug('x,y set to x: %s, y: %s', x, y)
            if x is not None and y is not None: #if there is a possible path
                if monster.distance_to(player) > 1: #if player is away
                    if not is_blocked(x,y): #if next tile is not blocked
                        monster.move_towards(x,y) #move to next tile
                    else: #if it is blocked, move in random direction
                        dir = random_step()
                        monster.move(dir[0],dir[1])
                    logg.debug('Monster moved to x: %s, y: %s', monster.x, monster.y)
                elif player.fighter.power > 0 and monster.is_cardinal(player.x, player.y) == True:
                #if player is alive and in cardinal direction - attack
                    logg.debug('Monster attacks x: %s, y: %s', player.x, player.y)
                    monster.fighter.attack(player)
        elif self.alerted >= 1 and not libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
        #if lost sight of the player and alerted
            self.alerted = self.alerted - 1 #decrease the alert level
            logg.debug('libtcod.path_compute() called by %s, pos x: %s, y: %s to x: %s, y: %s', monster.name, str(monster.x), str(monster.y), self.last_x, self.last_y)
            x,y = libtcod.path_walk(path_map, True)
            logg.debug('x,y set to x: %s, y: %s', x, y)
            #move towards the player's last known position or stumble around if impossible
            if x is not None and y is not None:
                if not is_blocked(x,y):
                    monster.move_towards(x,y)
                else:
                    dir = random_step()
                    monster.move(dir[0],dir[1])
            logg.debug('Monster moved to x: %s, y: %s', monster.x, monster.y)

        else: #move in random direction if left all alone
            dir = random_step()
            monster.move(dir[0],dir[1])

        #finally, block the tile so other monsters can path around it
        libtcod.map_set_properties(fov_map, monster.x, monster.y, not map[monster.x][monster.y].block_sight, False)

logg.debug('Pathfinder initialized.')

class Pathfinder_arch:
    def __init__(self, alerted = 1, last_x=None, last_y=None):
        self.alerted = alerted
        self.last_x = last_x
        self.last_y = last_y

    def take_turn(self):
        monster = self.owner
        libtcod.map_set_properties(fov_map, monster.x, monster.y, not map[monster.x][monster.y].block_sight, True) #unlock own tile before move
        self.owner.clear()

        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y) or self.alerted > 0:
            #player in view
            self.last_x = player.x #remember player's last position
            self.last_y = player.y
            logg.debug('libtcod.path_compute() called by %s, pos x: %s, y: %s to x: %s, y: %s', monster.name, str(monster.x), str(monster.y), self.last_x, self_last_y)
            libtcod.path_compute(path_map, monster.x, monster.y, self.last_x, self.last_y)
            #compute and set path to the player
            x,y = libtcod.path_walk(path_map, True)
            logg.debug('x,y set to x: %s, y: %s', x, y)
            if x is not None and y is not None: #if there is a possible path
                if monster.distance_to(player) > 1: #if player is away
                    if not is_blocked(x,y): #if next tile is not blocked
                        monster.move_towards(x,y) #move to next tile
                    else: #if it is blocked, move in random direction
                        dir = random_step()
                        monster.move(dir[0],dir[1])
                    logg.debug('Monster moved to x: %s, y: %s', monster.x, monster.y)
                elif player.fighter.power > 0 and monster.is_cardinal(player.x, player.y) == True:
                    #if player is alive and in cardinal direction - attack
                    logg.debug('Monster attacks x: %s, y: %s', player.x, player.y)
                    monster.fighter.attack(player)
        elif self.alerted >= 1 and not libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
        #if lost sight of the player and alerted
            logg.debug('libtcod.path_compute() called by %s, pos x: %s, y: %s to x: %s, y: %s', monster.name, str(monster.x), str(monster.y), self.last_x, self_last_y)
            libtcod.path_compute(path_map, monster.x, monster.y, self.last_x, self.last_y)
            #compute and set path to the player
            x,y = libtcod.path_walk(path_map, True)
            logg.debug('x,y set to x: %s, y: %s', x, y)
            #move towards the player's last known position or stumble around if impossible
            if x is not None and y is not None: #if there is a possible path
                if not is_blocked(x,y):
                    monster.move_towards(x,y)
                else:
                    dir = random_step()
                    monster.move(dir[0],dir[1])
            logg.debug('Monster moved to x: %s, y: %s', monster.x, monster.y)
        else: #move in random direction if left all alone
            dir = random_step()
            monster.move(dir[0],dir[1])

        #finally, block the tile so other monsters can path around it
        libtcod.map_set_properties(fov_map, monster.x, monster.y, not map[monster.x][monster.y].block_sight, False)

logg.debug('Pathfinder_arch initialized')

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
            if not self.owner.name == 'passage':
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
            self.use_function()
            if self.owner.name is not 'passage':
                objects.remove(self.owner)

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

logg.debug('Item initialized.')
logg.info('Class initialization finished.')

################################
# FUNCTIONS                    #
################################

logg.info('Functions initialization.')

#room creation function
def create_room(room):
    #logg.debug('create_room() called')
    global map
    for x in range(room.x1 + 1, room.x2):
       for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

logg.debug('create_room()')

#horizontal tunnel creation between rooms
def create_h_tunnel(x1, x2, y):
    #logg.debug('create_h_tunnel() called')
    global map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

logg.debug('create_h_tunnel()')

#vertical tunnel creation between rooms
def create_v_tunnel(y1, y2, x):
    #logg.debug('create_v_tunnel')
    global map
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

logg.debug('create_v_tunnel')

#map generation function
def make_map():
    #logg.debug('make_map() called')
    global map, objects, num_rooms, hole, drop, lv_feeling

    #the list of objects with just the player
    objects = [player]

    #fill map with "blocked" tiles
    map = [[ Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    rooms = []
    num_rooms = 0

    drop = False

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

                    if libtcod.random_get_int(0, 0, 1) == 1:
                        create_h_tunnel(prev_x, new_x, prev_y+1)
                        create_v_tunnel(prev_y, new_y, new_x+1)
                else:
                    #coin=0
                    #first move vertically, than horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

                    if libtcod.random_get_int(0, 0, 1) == 1:
                        create_v_tunnel(prev_y, new_y, prev_x+1)
                        create_h_tunnel(prev_x, new_x, new_y+1)

            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    if d_level is not 10:

        #place the hole in the last room
        item_component = Item(use_function=new_level)

        hole = Object(new_x, new_y, 'O', 'passage', libtcod.yellow, item=item_component, always_visible=True)

        objects.append(hole)
        hole.send_to_back()
    else:
        fighter_component = Fighter(hp=30, stamina=10, power=10, death_function=archdemon_death)
        ai_component = Pathfinder_arch()

        monster = Object(new_x, new_y, 'A', 'Archdemon', libtcod.cyan, blocks=True, fighter=fighter_component, ai=ai_component, always_visible=True)
        objects.append(monster)
        lv_feeling = 'finale'

    #logg.debug('make_map() finished with %s rooms, player at %s, %s, lv_feeling = %s, exit at %s, %s', num_rooms, player.x, player.y, lv_feeling, new_x, new_y)

logg.debug('make_map()')

#object generator function
def place_objects(room):
    global num_rooms, drop, got_key, NUM_POTIONS, NUM_SHARDS, NUM_ARCH, lv_feeling
    #logg.debug('place_objects called in room %s', num_rooms)
    #choose a random number of monsters
    num_monsters = libtcod.random_get_int(0, 2, MAX_ROOM_MONSTERS + d_level)

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
                    fighter_component = Fighter(hp=7, stamina=10, power=8, death_function=monster_death)
                    ai_component = Pathfinder()

                    monster = Object(x, y, 'O', 'ogre', libtcod.darker_red, blocks=True, fighter=fighter_component, ai=ai_component)
                elif roll_monster < 10+55:
                    #create a hurlock
                    fighter_component = Fighter(hp=4, stamina=10, power=5, death_function=monster_death)
                    ai_component = Pathfinder()

                    monster = Object(x, y, 'H', 'hurlock', libtcod.dark_orange * libtcod.light_grey, blocks=True, fighter=fighter_component, ai=ai_component)
                else:
                    #create a genlock
                    fighter_component = Fighter(hp=3, stamina=10, power=3, death_function=monster_death)
                    ai_component = Pathfinder()

                    monster = Object(x, y, 'g', 'genlock', libtcod.dark_green, blocks=True,
                        fighter=fighter_component, ai=ai_component)

                objects.append(monster)

    if d_level > 1 and drop == False and NUM_POTIONS > 0:
        #choose a random number of items
        num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

        for i in range(num_items):
            #choose a random spot for an item
            x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
            y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

            #only place if the tile is not blocked already
            if not is_blocked(x, y):
                roll_item = libtcod.random_get_int(0, 0, 100)
                if roll_item < 100:
                    #50% chance to create a healing potion
                    item_component = Item(use_function=cast_power)
                    item = Object(x, y, '!', 'healing potion', libtcod.light_red, item=item_component)

                    objects.append(item)
                    item.send_to_back() #items appear below monsters/player/corpses
                    item.always_visible = True #items are visible even out of FOV
                    NUM_POTIONS -= 1
                    drop = True

    if NUM_ARCH > 0:
        shard_chance = libtcod.random_get_int(0, 1, 100)
    else:
        shard_chance = 100
    if d_level < 10 and d_level > 1 and num_rooms == 5 and NUM_SHARDS > 0 and shard_chance >= 50:
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        characters = ("`", "|", "-", "_", "'")
        char = characters[libtcod.random_get_int(0, 0, len(characters) - 1)]

        item_component = Item(use_function=get_shard)
        item = Object(x, y, char, 'shard', libtcod.gold * libtcod.lightest_blue * 2, item=item_component)

        objects.append(item)
        item.send_to_back()
        item.always_visible = True
        got_key = False
        NUM_SHARDS -= 1
        lv_feeling = 'shard'

    elif d_level < 10 and d_level > 1 and num_rooms == 5 and NUM_ARCH > 0 and NUM_SHARDS > 0:
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        fighter_component = Fighter(hp=9001, stamina=10, power=15, death_function=archdemon_death)
        ai_component = Pathfinder_arch()

        monster = Object(x, y, 'A', 'Archdemon', libtcod.cyan, blocks=True, fighter=fighter_component, ai=ai_component, always_visible=True)
        objects.append(monster)
        got_key = True
        NUM_ARCH -= 1
        lv_feeling = 'arch'

        #logg.debug('place_objects done', num_rooms)

logg.debug('place_objects()')

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

    libtcod.console_set_default_foreground(panel, libtcod.lightest_gray)

    render_bar(1, 3, BAR_WIDTH, 'STAMINA', player.fighter.stamina, player.fighter.max_stamina, libtcod.dark_red, libtcod.darkest_red, panel)
    render_bar(1, 4, BAR_WIDTH, 'POWER', player.fighter.power, player.fighter.power, libtcod.darkest_gray, libtcod.darkest_grey * 0.5, panel)


    libtcod.console_set_default_foreground(panel, libtcod.lightest_gray)
    libtcod.console_print_ex(panel, 1, 6, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level: ' + str(d_level))
    libtcod.console_print_ex(panel, 1, 7, libtcod.BKGND_NONE, libtcod.LEFT, 'Darkspawn killed: ' + str(monsters_killed))
    libtcod.console_print_ex(panel, 1, 8, libtcod.BKGND_NONE, libtcod.LEFT, 'Score: ' + str(monsters_killed * d_level))

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
logg.debug('render_all()')

#keystrokes function
def handle_keys():
    global fov_recompute, pick_list, high, init_font

    key = libtcod.Key()

    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, libtcod.Mouse())
    key_char = chr(key.c)

    if key.vk is not 0:
        logg.debug('Key pressed: key_char[%s], key.vk[%s].', key_char, key.vk)

    #toggle fullscreen
    if key.vk == libtcod.KEY_F11:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    #exit game
    elif key.vk == libtcod.KEY_ESCAPE:

        while(True):
            leave = False
            choice = menu('\n Do you really want to return to main menu? \n', ['No.', 'Restart', 'Yes, quit.'], 44)

            if choice == 0: #Don't quit
                break
            if choice == 1:
                new_game()
                play_game()
            elif choice == 2: #quit and save the score
                now = datetime.datetime.now()
                date_time = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + " " + str(now.hour) + ":" + str(now.minute)
                score = str(monsters_killed * d_level)

                string = (score + " - " + player.name + " - " + date_time + "\n")
                fileObj = open("main/data/highscores.dat", "a")
                fileObj.write(string)
                fileObj.close()
                leave = True
                break
        if leave == True:
            return 'exit'

    #use pgup and pgdown to change font size on the fly
    elif key.vk == libtcod.KEY_PAGEUP:
        if init_font == 16:
            pass
        elif init_font == 12:
            init_font = 16
            libtcod.console_set_custom_font('main/data/terminal16x16_gs_ro.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE)
            libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE + ' v.' + VERSION, False, renderer = libtcod.RENDERER_SDL)
            libtcod.sys_set_fps(LIMIT_FPS)
            con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT) #new console, used ALOT[why]
            #bottom panel console
            panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
        elif init_font == 10:
            init_font = 12
            libtcod.console_set_custom_font('main/data/terminal12x12_gs_ro.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE)
            libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE + ' v.' + VERSION, False, renderer = libtcod.RENDERER_SDL)
            libtcod.sys_set_fps(LIMIT_FPS)
            con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT) #new console, used ALOT[why]
            #bottom panel console
            panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
        elif init_font == 8:
            init_font = 10
            libtcod.console_set_custom_font('main/data/terminal10x10_gs_ro.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE)
            libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE + ' v.' + VERSION, False, renderer = libtcod.RENDERER_SDL)
            libtcod.sys_set_fps(LIMIT_FPS)
            con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT) #new console, used ALOT[why]
            #bottom panel console
            panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
        else:
            print("Well, obviously there is an error in handle_keys")

    elif key.vk == libtcod.KEY_PAGEDOWN:
        if init_font == 8:
            pass
        elif init_font == 10:
            init_font = 8
            libtcod.console_set_custom_font('main/data/terminal8x8_gs_ro.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE)
            libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE + ' v.' + VERSION, False, renderer = libtcod.RENDERER_SDL)
            libtcod.sys_set_fps(LIMIT_FPS)
            con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT) #new console, used ALOT[why]
            #bottom panel console
            panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
        elif init_font == 12:
            init_font = 10
            libtcod.console_set_custom_font('main/data/terminal10x10_gs_ro.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE)
            libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE + ' v.' + VERSION, False, renderer = libtcod.RENDERER_SDL)
            libtcod.sys_set_fps(LIMIT_FPS)
            con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT) #new console, used ALOT[why]
            #bottom panel console
            panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
        elif init_font == 16:
            init_font = 12
            libtcod.console_set_custom_font('main/data/terminal12x12_gs_ro.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE)
            libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE + ' v.' + VERSION, False, renderer = libtcod.RENDERER_SDL)
            libtcod.sys_set_fps(LIMIT_FPS)
            con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT) #new console, used ALOT[why]
            #bottom panel console
            panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
        else:
            print("Well, obviously there is an error in handle_keys")

    #if the game is playing
    if game_state == 'playing':
        #movement keys
        #numpad, arrows, vim
        if key.vk == libtcod.KEY_KP8 or key.vk == libtcod.KEY_UP or key_char == 'k':
            player_move_or_attack(0, -1)

        elif key.vk == libtcod.KEY_KP2 or key.vk == libtcod.KEY_DOWN or key_char == 'j':
            player_move_or_attack(0, 1)

        elif key.vk == libtcod.KEY_KP4 or key.vk == libtcod.KEY_LEFT or key_char == 'h':
            player_move_or_attack(-1, 0)

        elif key.vk == libtcod.KEY_KP6 or key.vk == libtcod.KEY_RIGHT or key_char == 'l':
            player_move_or_attack(1, 0)

        elif key.vk == libtcod.KEY_KP5 or key.vk == libtcod.KEY_SPACE: #KP_5, SPACE - wait a turn
            player.move(0, 0)
            message('You wait a turn.', libtcod.white)
            player.fighter.rest(1)
            fov_recompute = True

        else:
            #test for other keys

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
                help_screen()

            return 'didnt-take-turn' #This makes sure that monsters don't take turn if player did not.

logg.debug('handle_keys()')

#movement and attacking
def player_move_or_attack(dx, dy):
    global fov_recompute, interest_cycle, didnttaketurn

    didnttaketurn = 0

    #the coordinates the player is moving to/attacking
    x = player.x + dx
    y = player.y + dy

    #check for attackable objects
    target = None
    item = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    for object in objects:
        if object.item and object.x == x and object.y == y:
            item = object
            break

    #attack if target found
    if target is not None:
        player.fighter.attack(target)
    elif target is None and is_blocked(x,y):
        didnttaketurn = 1
    else:
        player.move(dx, dy)
        if item is not None and item.name is not 'passage':
            item.item.use()
        elif item is not None and item.name == 'passage' and got_key == False:
            message("You feel the presence of a great artifact nearby.", libtcod.dark_purple)
            message("You cannot leave here without it.", libtcod.dark_purple)
        elif item is not None and item.name == 'passage' and got_key == True:
            item.item.use()
        items = get_names_player_tile()
        if len(items) >= 1:
            message('On the floor here: ' + str(items))

        fov_recompute = True

logg.debug('player_move_or_attack()')

#function that checks if the tile is blocked
def is_blocked(x, y):
    #check map tile first
    try:
        #[XXX] Hack for windows, seems the libtcod.dll is broken and throws up y in range of couple million
        if map[x][y].blocked:
            return True
    except IndexError:
        logg.warn('is_blocked() catched an IndexError with values x: %s and y: %s', str(x), str(y))
        return True

    #than check for blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

logg.debug('is_blocked()')

#GAME OVER MAN, GAME OVER
def player_death(player):
    global game_state

    message('You are dead! Press ESCAPE to exit to main menu.', libtcod.red)
    message('Check highscores if you have beaten the best yet!', libtcod.red)
    game_state = 'dead'

    #visual corpse change
    player.char = '%'
    player.color = libtcod.darker_red

logg.debug('player_death()')

#monster death function
def monster_death(monster):
    global monsters_killed
    #transforms a dead mob into a non-blocking corpse that can't be attacked and doesn't move (yet)
    message(monster.name.capitalize() + ' is dead!', libtcod.light_blue)
    monster.char = '%'
    monster.color = libtcod.darker_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.always_visible = True
    monsters_killed += 1
    player.fighter.rest(15)
    #make sure the spot where body lies is cleared for other monsters to move on
    libtcod.map_set_properties(fov_map, monster.x, monster.y, not map[monster.x][monster.y].block_sight, True)

    monster.send_to_back()

logg.debug('monster_death()')

def archdemon_death(monster):

    global game_state, monsters_killed

    monsters_killed += 100

    message(monster.name.capitalize() + ' is dead!', libtcod.light_blue)
    message("As you lay down your sword, the horde howls in dispair!", libtcod.light_purple)
    message("Congratulations Warden!", libtcod.light_purple)
    message("With your death you bought some time for the living.", libtcod.light_purple)
    message("Press ESCAPE to quit and check your score.")
    message("")
    monster.char = 'A'
    monster.color = libtcod.darker_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.always_visible = True

    game_state = "win"

logg.debug('archdemon_death()')

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color, console):
    #bar rendering function (hp/xp/mana, whatever)
    if maximum == 0:
        bar_width = value
    else:
        bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_foreground(panel, libtcod.lightest_gray)

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

logg.debug('render_bar()')

#msgs handling function
def message(new_msg, color = libtcod.white):
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if buffer is full, remove the oldest line to make room for a new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #add the new line as a tuple, with the text and colour
        game_msgs.append( (line, color) )

logg.debug('message()')

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

logg.debug('get_names_under_mouse()')

#return a string with objects names that are on the same tile as player
def get_names_player_tile():
    (x, y) = (player.x, player.y)

    names = [obj.name for obj in objects if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and not obj.char == '@']

    names = ', ' .join(names)
    return names.capitalize()

logg.debug('get_names_player_tile()')

def interest_list():
    global interest_names, interest_pos

    interest_names = [obj.name for obj in objects if libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and not obj.char == '@']

    interest_pos = [(obj.x, obj.y) for obj in objects if libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and not obj.char == '@']

logg.debug('interest_list()')

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

logg.debug('interest_tab()')

#menu function - initially for the inventory screen
def menu(header, options, width, offset=0):
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
    y = SCREEN_HEIGHT/2 - height/2 + offset
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the console, and wait for a key-press
    libtcod.console_flush()

    mouse = libtcod.Mouse()
    key = libtcod.Key()
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

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

logg.debug('menu()')

def msgbox(text, width=50):
    menu(text, [], width) #uses menu() as a message box
    libtcod.sys_sleep_milli(1000)

logg.debug('msgbox()')

#create a pathing map from the fov_map
def make_path_map():
    logg.debug('make_path_map() called')
    global path_map
    path_map = libtcod.path_new_using_map(fov_map, 0)

logg.debug('make_path_map()')

def destroy_path_map():
    logg.debug('destroy_path_map() called')
    global path_map
    libtcod.path_delete(path_map)

logg.debug('make_path_map()')

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

logg.debug('random_step()')

################################
# Magic Effects                #
################################

def cast_power():
    message('You drink the potion and feel the power in your veins!', libtcod.light_violet)
    player.fighter.stamina = 100
    player.fighter.power += 1

logg.debug('cast_power()')

def get_shard():
    global got_key
    if NUM_SHARDS is not 0:
        message('You have found a fragment of an ancient weapon.', libtcod.light_violet)
    else:
        message('The sword shards magically reforge, and a powerful sword lays in your hands.', libtcod.light_violet)
        message('This sword will allow you to kill the Archdemon!', libtcod.light_blue)
        player.fighter.power += 3
    got_key = True

logg.debug('get_shard()')

################################
# META-GAME FUNCTIONS          #
################################

def main_menu():
    img = libtcod.image_load('main/data/warden.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and credits
        libtcod.console_set_default_foreground(0, libtcod.light_grey)
        libtcod.console_print_ex(0, SCREEN_WIDTH/2, SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER, 'By Michal Walczak')

        #show options and wait for the player's choice
        choice = menu('   Choose an option:', ['Play a new game.', 'Highscores', 'Help', 'Quit.'], 24, 5)

        if choice == 0: #new game
            new_game()
            play_game()
        if choice == 1:
            highscores()
        if choice == 2:
            help_screen()
        if choice == 3: #quit
            break

        libtcod.console_flush() #clear the console before redraw (fixes blacking out issue?

logg.debug('main_menu()')

#new game initialisation
def new_game():
    global player, inventory, game_msgs, game_state, d_level, monsters_killed, win_print, equipment, weapon_wield, armor_worn, player_gold, highlight, old_highlight_tab, old_highlight, turns_passed, explheal, didnttaketurn, path_map

    PLAYER_NAME = input_box("Enter your name:", 30)
    if PLAYER_NAME == "":
        PLAYER_NAME = "Warden"

    #create a fighter component for the player, add a player @, state objects list
    fighter_component = Fighter(hp=20, stamina=100, power=8, death_function=player_death)
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
    if path_map is not None:
        destroy_path_map()

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

    NUM_SHARDS = 4
    NUM_POTIONS = 5
    NUM_ARCH = 2
    lv_feeling = 'none'
    got_key = True

    didnttaketurn = 0

    #welcoming message
    message('Dwarven guards close the gates to Deep Roads behind you...', libtcod.red)
    message('Use arrows, numpad or vi-keys to move.', libtcod.lightest_gray)
    message('Press F1 to display the help screen.', libtcod.lightest_gray)

logg.debug('new_game()')

def new_level():
    global player, game_msgs, game_state, d_level, lv_feeling

    #logg.debug('new_level() called, d_lv is %s', d_level + 1)

    lv_feeling = 'none'
    d_level += 1 #add one to the dungeon level
    make_map()
    got_key = False
    initialize_fov()
    destroy_path_map()
    make_path_map()
    game_state='playing'
    if lv_feeling == 'none':
        message('You follow some narrow tunnels deeper down. You hear earth rumbling behind you.', libtcod.lightest_grey)
    elif lv_feeling == 'arch':
        message('With every step you take, you can feel the evil presence of an Archdemon. Run!', libtcod.light_red)
    elif lv_feeling == 'shard':
        message('You feel there is a powerful item around this area.', libtcod.gold)
    elif lv_feeling == 'finale':
        message('Here it is! Kill the Archdemon!', libtcod.light_red)

logg.debug('new_level()')

#as name says
def initialize_fov():
    #logg.debug('initialize_fov() called')
    global fov_recompute, fov_map
    fov_recompute = True

    #clear old map if present
    if fov_map is not None:
        libtcod.map_clear(fov_map, transparent = False, walkable = False)

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

logg.debug('initialize_fov()')

#main game function
def play_game():
    #logg.debug('play_game() called')
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
            if DEBUG_GOD_MODE == True:
                player.fighter.stamina = 100
            player.fighter.tire_down(1)
            highlight = 0
            turns_passed += 1
            logg.debug('Turn %s, AI is taking turn.', turns_passed)
            for object in objects:
                if object.ai:
                    object.ai.take_turn()

            interest_list()
            interest_cycle = 0

logg.debug('play_game()')

def input_box(header, width=50):
    timer = 0
    command = ""
    x = 1

    #calculate total height for the header (auto-wraped), and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = header_height + 3

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
        elif key.vk == libtcod.KEY_ENTER or key.vk == libtcod.KEY_KPENTER:
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

    return command

logg.debug('input_box()')

def highscores():
    scores = []
    try:
        for line in open("main/data/highscores.dat", "r"):
            scores.append(line)
    except IOError:
        msgbox("\n No highscore to display. \n", 26)
        libtcod.sys_sleep_milli(1000)
        return None

    scores.sort(key=lambda x: int(x.split(' - ', 1)[0]), reverse = True)

    #creates an off-screen console that represents the menu's window
    hiscr = libtcod.console_new(40, 14)

    header = "HIGHSCORES"

    #print the header with auto-wrap
    libtcod.console_set_default_foreground(hiscr, libtcod.lightest_gray)
    libtcod.console_print_rect_ex(hiscr, 14, 1, 40, 1, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print the menu's options
    y = 3
    index = 1

    for line in scores:
        if index != 10:
            index_p = "0"+str(index)
        else:
            index_p = index
        text = '(' + str(index_p) + ') ' + line
        libtcod.console_print_ex(hiscr, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        index +=1
        if index == 11:
            break

    #blit "window" contents to the root console
    x = SCREEN_WIDTH/2 - 40/2
    y = SCREEN_HEIGHT/2 - 14/2
    libtcod.console_blit(hiscr, 0, 0, 40, 14, 0, x, y, 1.0, 1.0)

    #present the console, and wait for a key-press
    libtcod.console_flush()

    libtcod.sys_sleep_milli(1000)

    libtcod.sys_wait_for_event(libtcod.EVENT_KEY_RELEASE | libtcod.EVENT_MOUSE_PRESS, libtcod.Key(), libtcod.Mouse(), True)

logg.debug('highscores()')

def help_screen():
    halp = libtcod.console_new(70, 35)
    header = "Warden Help Screen"

    while True:

        libtcod.console_set_default_foreground(halp, libtcod.lightest_gray)
        libtcod.console_print_rect_ex(halp, 26, 1, 70, 1, libtcod.BKGND_NONE, libtcod.LEFT, header)

        walloftext ="""
                        More info in README.txt
  ----------
  Keybindings:

  Arrows / numpad / vi-keys   -   Arrows / numpad arrows / vi-keys
  SPACE / .                   -   Wait a turn
  TAB                         -   Cycle interesting things on screen
  Point with mouse            -   Display names of objects
  PAGE UP / PAGE DOWN         -   Change screen size
  F1                          -   Display help screen (this)
  F11                         -   Toggle fullscreen
  ESCAPE                      -   Quit to main menu (confirm)
  SHIFT + P                   -   Take a screenshot

  ----------
  The objectives:
  - Seek out blade shards to gain access to the lower levels!
  - Reforge an ancient sword!
  - Kill the Archdemon on level 10!
  - Beat the highscore!

  Some tips:
  - Walk into things to attack
  - Your stamina drains quickly in combat and while waiting,
      only killing monsters can replenish it with your rage
  - If you run out of power, you are dead
  - You can't kill the Archdemon without a powerful sword
  - Find health potions to regain some lost strength
  - Only cardinal directions are valid for movement
  \n
  """

        libtcod.console_print_rect_ex(halp, 0, 3, 0, 0, libtcod.BKGND_NONE, libtcod.LEFT, walloftext)

        x = SCREEN_WIDTH/2 - 70/2
        y = SCREEN_HEIGHT/2 - 30/2
        libtcod.console_blit(halp, 0, 0, 70, 35, 0, x, y, 1.0, 1)


        libtcod.console_flush()

        if libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE_PRESS, libtcod.Key(), libtcod.Mouse(), False) != 0:
            return False

logg.debug('help_screen()')
logg.info('Functions initialization finished.')
################################
# Initialization               #
################################

logg.info('Main loop initialization.')
logg.info('Auto detect screen resolution and set font size.')
#font import, spawn window, window name, FPS (if real-time)
res_height = libtcod.sys_get_current_resolution()[1]
logg.debug('Screen height detected: %s', str(res_height))
if res_height <= 550:
    logg.debug('Font size set to 8')
    init_font = 8
    libtcod.console_set_custom_font('main/data/terminal8x8_gs_ro.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE)
elif res_height <= 600:
    logg.debug('Font size set to 10')
    init_font = 10
    libtcod.console_set_custom_font('main/data/terminal10x10_gs_ro.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE)
elif res_height <= 900:
    logg.debug('Font size set to 12')
    init_font = 12
    libtcod.console_set_custom_font('main/data/terminal12x12_gs_ro.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE)
else:
    logg.debug('Font size set to 16')
    init_font = 16
    libtcod.console_set_custom_font('main/data/terminal16x16_gs_ro.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GRAYSCALE)
logg.debug('Main console initialization.')
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE + ' v.' + VERSION, False, renderer = libtcod.RENDERER_SDL)
logg.debug('Setting the FPS limit.')
libtcod.sys_set_fps(LIMIT_FPS)
logg.debug('Drawing console initialization.')
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT) #new console, used ALOT[why]
#bottom panel console
logg.debug('Bottom panel console initialization.')
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

high = ord('a')
logg.info('Invoking main_menu()')
main_menu()

logg.info('Program terminated properly. Have a nice day.')
#End of the line.
