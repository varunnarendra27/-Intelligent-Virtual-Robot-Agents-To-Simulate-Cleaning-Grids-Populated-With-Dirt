#!/usr/bin/env python3
import math
from typing import Iterable
from pyoptional.pyoptional import PyOptional
from vacuumworld import run
from vacuumworld.model.actions.vwactions import VWAction
from vacuumworld.model.actions.vwidle_action import VWIdleAction
from vacuumworld.model.actions.vwbroadcast_action import VWBroadcastAction
from vacuumworld.model.actions.vweffort import VWActionEffort
from vacuumworld.model.actor.mind.surrogate.vwactor_mind_surrogate import VWActorMindSurrogate
from vacuumworld.common.vwdirection import VWDirection
from vacuumworld.common.vwcoordinates import VWCoord
from vacuumworld.model.actions.vwidle_action import VWIdleAction
from vacuumworld.model.actions.vwmove_action import VWMoveAction
from vacuumworld.model.actions.vwturn_action import VWTurnAction
from vacuumworld.model.actions.vwclean_action import VWCleanAction


class MyMind(VWActorMindSurrogate):
    def __init__(self) -> None:
        super(MyMind, self).__init__()
        self.__facing_left_wall: bool = False
        self.__bottom_right_corner: bool = False
        self.__startinternalmap: bool = False
        self.__gridsize: int = 0
        self.__internalmap: list = []
        self.__dirt_found: bool = False
        self.__starting_position: bool = False
        self.__turncoordY: int =0
        self.__map_sent: bool = False
        self.__start_cleaning = False
        self.list_of_dirt = []
        self.broadcast_chosen_dirt: bool = False
        

        

    def revise(self) -> None:
        
        
        
        self.holder = self.get_latest_received_messages()
        print(self.holder)
        for message in self.holder:
            print(message.get_content())
            if message.get_content() == "Move!":
                self.move = True
            elif isinstance(message.get_content(), list):
                self.__internalmap = message.get_content()
                print("white_mind: Recieved internal map") # Everytime a robot cleans up dirt, a new internal map is shared between robots with updates dirt on grid
                print(self.__internalmap)
                self.__start_cleaning = True
        
        # At start of program, white robot travels to bottom right fo find grid size.
        if not self.__facing_left_wall and self.get_own_appearance().is_facing_south() and self.get_latest_observation().is_wall_immediately_ahead():
            self.__facing_left_wall = True
        elif self.__can_see_corner() and not self.__bottom_right_corner and self.get_own_appearance().is_facing_east() and self.get_latest_observation().is_wall_immediately_ahead():
            coord: PyOptional[VWCoord] = self.__get_visible_corner_coordinates()

            assert coord.is_present()

            print(f"Grid size is {coord.or_else_raise()[0]+1}x{coord.or_else_raise()[1]+1}. I'm staying idle from now on.")
            self.__gridsize = coord.or_else_raise()[0]+1
            self.__create_list()
            self.__bottom_right_corner = True
        # One more step.
        elif not self.__facing_left_wall and self.get_own_appearance().is_facing_south() and self.get_latest_observation().is_wall_one_step_ahead():
            print("Almost there! One more step and I'll be at the western wall.")
            
            
            
            
    # Functions to check if vwlocations are acessable        
    def check_if_left_exists(self) -> bool:
        try:
            self.get_latest_observation().get_left().get()
            return True
        except:
            return False
        
    def check_if_right_exists(self) -> bool:
        try:
            self.get_latest_observation().get_right().get()
            return True
        except:
            return False
        
    def check_if_facing_wall(self) -> bool:
        try:
            self.get_latest_observation().get_forward().get()
            return True
        except:
            return False
        

    def check_if_forward_exists(self) -> bool:
        try:
            self.get_latest_observation().get_forward().get()
            return True
        except:
            return False
        
        
    def send_updated_map(self) -> bool:
        try:
            self.get_latest_observation().get_forward().get()
            return True
        except:
            return False
    
    
    # Calculates closest dirt by using pythagoras to find vector. The dirt of the shortest distance is then traveled to first
    def calculate_closest_dirt(self) ->None:
        shortest_distance = [0.0,0.0,0.0]
        current_position_y = self.get_latest_observation().get_center().get().get_coord().get_y()
        current_position_x = self.get_latest_observation().get_center().get().get_coord().get_x()
        
        for loc_of_dirt in self.list_of_dirt:
            vector_to_dirt = ((loc_of_dirt[0] - current_position_y)**2) + ((loc_of_dirt[1] - current_position_x)**2)
            vector_to_dirt = math.sqrt(vector_to_dirt)
            
            print("white mind: the vector of dirt is: ", vector_to_dirt) 
            
            if shortest_distance[0] ==0:
                shortest_distance = [vector_to_dirt, loc_of_dirt[0], loc_of_dirt[1]]
                
            elif shortest_distance[0] > vector_to_dirt:
                shortest_distance = [vector_to_dirt, loc_of_dirt[0], loc_of_dirt[1]]
            
        print(shortest_distance)
        self.closest_dirt = shortest_distance
        print("white_mind: The closest_dirt is :", self.closest_dirt)
    
    # FUnction to move robot to specific location specified by the closest dirt. Moves in y axis thten x axis
    def move_to_dirt(self)->Iterable[VWAction]:
        sending_message = {"going_to" : self.closest_dirt}
        if self.broadcast_chosen_dirt == False:
            self.broadcast_chosen_dirt = True
            print("white_mind: broadcasting chosen dirt")
            return [VWBroadcastAction(message=sending_message, sender_id= self.get_own_id())]
            
        list_of_dirt = self.closest_dirt
        print("list of dirt is:", list_of_dirt)
        current_position_y = self.get_latest_observation().get_center().get().get_coord().get_y() 
        current_position_x = self.get_latest_observation().get_center().get().get_coord().get_x()
        
        print("my x coord is:", current_position_x)
        print("my y coord is:", current_position_y)
        
        if(self.get_latest_observation().get_center().get().has_dirt()):
            self.broadcast_chosen_dirt = False
            print("white_mind: I FOUND THE DIRT!!")
            
            
            
            loc = tuple(self.get_own_position())
            self.list_of_dirt.remove([loc[1],loc[0]])
            self.__internalmap[current_position_y][current_position_x] = [False, "blank"]
            print(self.__internalmap)
            return [VWCleanAction(), VWBroadcastAction(message=self.__internalmap, sender_id= self.get_own_id())] # Cleans dirt and sends updated map
        else:
            
            if(current_position_y > list_of_dirt[1]):
                if(not self.get_own_appearance().is_facing_north()):
                    
                    return[VWTurnAction(VWDirection.left)]
                elif(current_position_y != list_of_dirt[1]):
                        
                        return[VWMoveAction()]
            
            elif(current_position_y < list_of_dirt[1]):
                if(not self.get_own_appearance().is_facing_south()):
                    
                    return[VWTurnAction(VWDirection.right)]
                elif(current_position_y != list_of_dirt[1]):
                    
                    return[VWMoveAction()]
                    
            elif(current_position_y == list_of_dirt[1]):
                if(current_position_x > list_of_dirt[2]):
                    if(not self.get_own_appearance().is_facing_west()):
                        
                        return[VWTurnAction(VWDirection.left)]
                    elif(current_position_x != list_of_dirt[2]):
                            return[VWMoveAction()]
                elif(current_position_x < list_of_dirt[2]):
                  
                    
                    if(not self.get_own_appearance().is_facing_east()):
                        
                        return[VWTurnAction(VWDirection.right)]
                    elif(current_position_x != list_of_dirt[2]):
                        
                        return[VWMoveAction()]
                else:
                    return [VWIdleAction()]
    
            

    def decide(self) -> Iterable[VWAction]:
        
                
        # Checks if there are any robots in the way. Broadcasts message to move if there is.
        if self.check_if_forward_exists():
            if self.get_latest_observation().get_forward().get().has_actor() :
                if self.get_latest_observation().get_forward().get().get_actor_appearance().get().get_colour().name == "green":
                    return [VWBroadcastAction(message="Move Green!", sender_id= self.get_own_id())]
                elif self.get_latest_observation().get_forward().get().get_actor_appearance().get().get_colour().name == "orange":
                    return [VWBroadcastAction(message="Move Orange!", sender_id= self.get_own_id())]
                
        if self.__start_cleaning == True:
            print("white_mind: I am going to start cleaning!")
            self.list_of_dirt = []
            # creates list of dirt to be cleaned
            for y in range (len(self.__internalmap)):
                for x in range (len(self.__internalmap)):
                    if self.__internalmap[y][x] == [True, "green"] or self.__internalmap[y][x] == [True, "orange"]:
                        self.list_of_dirt.append([y, x])
            '''self.__start_cleaning = False'''
            if self.list_of_dirt == []:
                return [VWIdleAction()]# if there is no more dirt, remain idle
            print("white_mind: ", self.list_of_dirt)
            
            
            print("white_mind: Calculating closest dirt")
            
            self.calculate_closest_dirt()
            return self.move_to_dirt()
                    
                    
            
        
        if self.__facing_left_wall:
            # If we are heading the right way, move forward (in search of a wall).
            if self.__startinternalmap:
                
                self.__fill_list()
                # If we have reached the start ofo the grid, then all grid squares have been scanned
                
                if self.get_latest_observation().get_center().get().get_coord().get_y() == 0 and self.get_latest_observation().get_center().get().get_coord().get_x() == 0:
                     
                     
                     if self.__map_sent == False:
                        self.__map_sent = True
                        self.__start_cleaning = True
                        return [VWBroadcastAction(message=self.__internalmap, sender_id= self.get_own_id())]
                     
                     else:
                        
                        return [VWIdleAction()]
                
                
                
                # Program for initial path that white takes to scan grid
                try:
                    if self.get_latest_observation().get_forward().get():
                            
                            if self.check_if_left_exists() :
                                
                                # side jumps differe based on the size of the grid
                                if(self.__gridsize > 4):
                                    if self.get_latest_observation().get_center().get().get_coord().get_y() == self.__turncoordY - 3 and self.get_latest_observation().get_center().get().get_coord().get_x() == self.__gridsize-1 and self.get_own_appearance().is_facing_north():
                                        
                                        return [VWTurnAction(direction=VWDirection.left)]
                                    else:
                                        return [VWMoveAction()]
                                else:
                                    if self.get_latest_observation().get_center().get().get_coord().get_y() == self.__turncoordY - 1 and self.get_latest_observation().get_center().get().get_coord().get_x() == self.__gridsize-1 and self.get_own_appearance().is_facing_north():
                                        
                                        return [VWTurnAction(direction=VWDirection.left)]
                                    else:
                                        
                                        return [VWMoveAction()]
                           
                            
                            else:
                                
                                
                                if(self.__gridsize > 4):
                                    
                                    if self.get_latest_observation().get_center().get().get_coord().get_y() == self.__turncoordY - 3 :
                                       
                                        return [VWTurnAction(direction=VWDirection.right)]
                                    else:
                                        
                                        return [VWMoveAction()]
                                else:
                                    if self.get_latest_observation().get_center().get().get_coord().get_y() == self.__turncoordY - 1 :
                                        
                                        return [VWTurnAction(direction=VWDirection.right)]
                                    else:
                                        
                                        return [VWMoveAction()]
                 #This code block is only touched when you are facing the wall       
                except:
                    print("white_mind: cant go forward")
                    
                    if(not self.check_if_forward_exists() and not self.check_if_right_exists()):
                        return [VWTurnAction(direction=VWDirection.left)]
                    elif self.get_own_appearance().is_facing_west():
                        self.__turncoordY = self.get_latest_observation().get_center().get().get_coord().get_y()
                        
                        return [VWTurnAction(direction=VWDirection.right)]
                    elif self.get_own_appearance().is_facing_east():
                        self.__turncoordY = self.get_latest_observation().get_center().get().get_coord().get_y()
                        return [VWTurnAction(direction=VWDirection.left)]
                    
                    
                    
                    
                    
                
               
            # Once we have found the western wall, we remain idle.
            
            
            
            
            
            
            
            
            elif self.__bottom_right_corner:
                while not self.get_own_appearance().is_facing_west():
                    return [VWTurnAction(direction=VWDirection.left)]
                self.__startinternalmap = True
                return [VWIdleAction()]
            elif self.get_own_appearance().is_facing_east():
                return [VWMoveAction()]
            # If we are facing north, turn left.
            elif self.get_own_appearance().is_facing_south():
                return [VWTurnAction(VWDirection.left)]
            # Otherwise (i.e., facing east or south), turn right.
            else:
                return [VWTurnAction(VWDirection.right)]
        else:
            # If we are heading the right way, move forward (in search of a wall).
            if self.get_own_appearance().is_facing_south():
                return [VWMoveAction()]
            # If we are facing north, turn left.
            elif self.get_own_appearance().is_facing_north():
                return [VWTurnAction(VWDirection.left)]
            # Otherwise (i.e., facing east or south), turn right.
            else:
                return [VWTurnAction(VWDirection.left)]
    
            
        
        
        
    # Checks if there is any dirt in observable locations.
    def __fill_list(self) -> None:
        
            
            
   
        
            try:
                if self.get_latest_observation().get_forward().get().has_dirt():
                    print("THERE IS DIRT HERE")
                    coord_of_dirt = self.get_latest_observation().get_forward().get().get_coord()
                    type_of_dirt = self.get_latest_observation().get_forward().get().get_dirt_appearance().get().get_colour()
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()][0] = True 
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()][1] = type_of_dirt.name
                    self.__dirt_found = True
                    
            except:
                print("The forward VWLocation is out of bounds")
                
            try: 
                if self.get_latest_observation().get_forwardleft().get().has_dirt():
                    coord_of_dirt = self.get_latest_observation().get_forwardleft().get().get_coord()
                    type_of_dirt = self.get_latest_observation().get_forwardleft().get().get_dirt_appearance().get().get_colour()
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()][0] = True
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()][1] = type_of_dirt.name
                    self.__dirt_found = True
                    
            except:
                print("The forward left VWLocation is out of bounds")
        
            try:
                if self.get_latest_observation().get_forwardright().get().has_dirt():
                    coord_of_dirt = self.get_latest_observation().get_forwardright().get().get_coord()
                    type_of_dirt = self.get_latest_observation().get_forwardright().get().get_dirt_appearance().get().get_colour()
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()][0] = True
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()][1] = type_of_dirt.name
                    self.__dirt_found = True
                    
                    
                    
            except:
                print("The forward right VWLocation is out of bounds")     
         
            try: 
                if self.get_latest_observation().get_left().get().has_dirt():
                    coord_of_dirt = self.get_latest_observation().get_left().get().get_coord()
                    type_of_dirt = self.get_latest_observation().get_left().get().get_dirt_appearance().get().get_colour()
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()][0] = True
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()][1] = type_of_dirt.name
                    self.__dirt_found = True
                    
                    
            except:
                    print("The left VWLocation is out of bounds")        
         
            try:
                
                if self.get_latest_observation().get_right().get().has_dirt():
                    coord_of_dirt = self.get_latest_observation().get_right().get().get_coord()
                    type_of_dirt = self.get_latest_observation().get_right().get().get_dirt_appearance().get().get_colour()
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()][0] = True
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()][1] = type_of_dirt.name
                    self.__dirt_found = True
                    
                    
                    
            except:
                    print("The right VWLocation is out of bounds")        
                
            try:
                if self.get_latest_observation().get_center().get().has_dirt():
                    coord_of_dirt = self.get_latest_observation().get_center().get().get_coord()
                    type_of_dirt = self.get_latest_observation().get_center().get().get_dirt_appearance().get().get_colour()
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()][0] = True
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()][1] = type_of_dirt.name
                    self.__dirt_found = True
                   
            except:
                
                    print("The centre VWLocation is out of bounds")  
       
            
            
        
 
            
            
            
    
       
       
       
        
        
    # Use 3D array to store items in grid. First value indicates true for dirt, and false for no dirt. Second value indicates colour of dirt
    
    def __create_list(self) -> None:
        for i in range(self.__gridsize):
            holder = []
            for x in range(self.__gridsize):
                holder.append([False, "blank"])
            self.__internalmap.append(holder)
            
        print(self.__internalmap)
        
        
            
    def __can_see_corner(self) -> bool:
        # We can see a corner if we can see a corner `VWLocation` in the current `VWObservation`.
        return any(loc.is_corner() for loc in self.get_latest_observation().get_locations().values())
    
    
    def __get_visible_corner_coordinates(self) -> PyOptional[VWCoord]:
        # We return a `PyOptional` wrapping the coordinates of the first corner `VWLocation` we can see.
        # We always check the current `VWObservation` in the same order of `VWPositionNames` (`center`, `forward`, `left`, `right`, `forwardleft`, `forwardright`).
        # We return an empty `PyOptional` if we can't see any corner.
        return PyOptional.of_nullable(next((loc.or_else_raise().get_coord() for loc in self.get_latest_observation().get_locations_in_order() if loc.is_present() and loc.or_else_raise().is_corner()), None))
    
    
    
class GreenMind(VWActorMindSurrogate):
    
    def __init__(self) -> None:
        super(GreenMind, self).__init__()
        self.move = False
        self.__internalmap: list = []
        self.__start_cleaning: bool = False
        self.list_of_dirt: list = []
        self.closest_dirt: list = []
        self.white_mind_choice:list = [-1,-1]
        
    
    def revise(self) -> None:
        # Do something.
        print("Testing revision")
        # Checking for any incoming messages regarding movement
        self.holder = self.get_latest_received_messages()
        print(self.holder)
        for message in self.holder:
            print("Testing recieving of message")
            print(message.get_content())
            if message.get_content() == "Move Green!":
                self.move = True
            elif isinstance(message.get_content(), list):
                self.__internalmap = message.get_content()
                print("Recieved internal map")
                print(self.__internalmap)
                self.__start_cleaning = True
            elif isinstance(message.get_content(), dict):
                print("Recieved dictionary: ", message.get_content())
                self.white_mind_choice = message.get_content()["going_to"]
            
    def decide(self) -> Iterable[VWAction]:
        
        if self.move == True:
            return self.move_out_of_the_way()
        
        
        print("start_cleaning: ", self.__start_cleaning)
        
        ''' Green Robot will start cleaning'''
        if self.__start_cleaning == True:
            print("I am going to start cleaning!")
            self.list_of_dirt = []
            # Creates list of dirt to be cleaned
            for y in range (len(self.__internalmap)):
                for x in range (len(self.__internalmap)):
                    if self.__internalmap[y][x] == [True, "green"]:
                        self.list_of_dirt.append([y, x])
            
            print("green mind: ", self.list_of_dirt)
            if self.list_of_dirt == []:
                return [VWIdleAction()]  # if there is no more dirt, remain idle
            
            print("Calculating closest dirt")
            
            self.calculate_closest_dirt()
            return self.move_to_dirt()
                    
                    
        else:
            return[VWIdleAction()]
            
            
    
    
   
        
        
    
    # Finds closest dirt using pythagoras and vectors.
    def calculate_closest_dirt(self) ->None:
        shortest_distance = [0.0,0.0,0.0]
        current_position_y = self.get_latest_observation().get_center().get().get_coord().get_y()
        current_position_x = self.get_latest_observation().get_center().get().get_coord().get_x()
        
        for loc_of_dirt in self.list_of_dirt:
            vector_to_dirt = ((loc_of_dirt[0] - current_position_y)**2) + ((loc_of_dirt[1] - current_position_x)**2)
            vector_to_dirt = math.sqrt(vector_to_dirt)
            
            print("the vector of dirt is: ", vector_to_dirt) 
            
            if shortest_distance[0] ==0:
                shortest_distance = [vector_to_dirt, loc_of_dirt[0], loc_of_dirt[1]]
                
            elif shortest_distance[0] > vector_to_dirt:
                shortest_distance = [vector_to_dirt, loc_of_dirt[0], loc_of_dirt[1]]
            
        print(shortest_distance)
        self.closest_dirt = shortest_distance
        print("The closest_dirt is :", self.closest_dirt)
            
            
        print(shortest_distance)
        self.closest_dirt = shortest_distance
        print("The closest_dirt is :", self.closest_dirt)
    # Function to move robot to specific dirt
    def move_to_dirt(self)->Iterable[VWAction]:
        list_of_dirt = self.closest_dirt
        print(" green list of dirt is:", list_of_dirt)
        current_position_y = self.get_latest_observation().get_center().get().get_coord().get_y() 
        current_position_x = self.get_latest_observation().get_center().get().get_coord().get_x()
        
        print("my x coord is:", current_position_x)
        print("my y coord is:", current_position_y)
        
        if(self.get_latest_observation().get_center().get().has_dirt() and self.get_latest_observation().get_center().get().get_dirt_appearance().get().get_colour().name == "green"):
            print("I FOUND THE DIRT!!")
            '''self.__internalmap[current_position_y -1][current_position_x-1] = [False, "blank"]'''
            
            '''print(self.list_of_dirt)'''
            loc = tuple(self.get_own_position())
            self.list_of_dirt.remove([loc[1],loc[0]])
            self.__internalmap[current_position_y][current_position_x] = [False, "blank"]
            print(self.__internalmap)
            return [VWCleanAction(), VWBroadcastAction(message=self.__internalmap, sender_id= self.get_own_id())] # Cleans dirt and sends updated map
        else:
            
            if(current_position_y > list_of_dirt[1]):
                if(not self.get_own_appearance().is_facing_north()):
                    
                    return[VWTurnAction(VWDirection.left)]
                elif(current_position_y != list_of_dirt[1]):
                        
                        return[VWMoveAction()]
            
            elif(current_position_y < list_of_dirt[1]):
                if(not self.get_own_appearance().is_facing_south()):
                    
                    return[VWTurnAction(VWDirection.right)]
                elif(current_position_y != list_of_dirt[1]):
                    
                    return[VWMoveAction()]
                    
            elif(current_position_y == list_of_dirt[1]):
                if(current_position_x > list_of_dirt[2]):
                    if(not self.get_own_appearance().is_facing_west()):
                        
                        return[VWTurnAction(VWDirection.left)]
                    elif(current_position_x != list_of_dirt[2]):
                            return[VWMoveAction()]
                elif(current_position_x < list_of_dirt[2]):
                    
                    
                    if(not self.get_own_appearance().is_facing_east()):
                        
                        return[VWTurnAction(VWDirection.right)]
                    elif(current_position_x != list_of_dirt[2]):
                        return[VWMoveAction()]
                else:
                    return [VWIdleAction()]
                
    # Function to move robot out of way            
    def move_out_of_the_way(self) ->Iterable[VWAction]:
        
        if(self.check_if_forward_exists() and not self.get_latest_observation().get_forward().get().has_actor()):
            
            self.move = False 
            return[VWMoveAction()]
        elif(self.check_if_left_exists()):
            return[VWTurnAction(VWDirection.left)]
        elif(self.check_if_right_exists()):
            return[VWTurnAction(VWDirection.right)]
            
        
    
    def check_if_left_exists(self) -> bool:
        try:
            self.get_latest_observation().get_left().get()
            return True
        except:
            return False
        
    def check_if_right_exists(self) -> bool:
        try:
            self.get_latest_observation().get_right().get()
            return True
        except:
            return False
        
    def check_if_facing_wall(self) -> bool:
        try:
            self.get_latest_observation().get_forward().get()
            return True
        except:
            return False
        

    def check_if_forward_exists(self) -> bool:
        try:
            self.get_latest_observation().get_forward().get()
            return True
        except:
            return False
        
        
        
class OrangeMind(VWActorMindSurrogate):
    
    def __init__(self) -> None:
        super(OrangeMind, self).__init__()
        self.move = False
        self.__internalmap: list = []
        self.__start_cleaning: bool = False
        self.list_of_dirt: list = []
        self.closest_dirt: list = []
        
    
    def revise(self) -> None:
        # Do something.
        print("Testing revision")
        
        self.holder = self.get_latest_received_messages()
        print(self.holder)
        for message in self.holder:
            print("Testing recieving of message")
            print(message.get_content())
            if message.get_content() == "Move Orange!":
                self.move = True
            elif isinstance(message.get_content(), list):
                self.__internalmap = message.get_content()
                print("Recieved internal map") # new internal map sent everytime a robot cleans a dirt
                print(self.__internalmap)
                self.__start_cleaning = True
    def decide(self) -> Iterable[VWAction]:
        print("TESTING DECISIONNN")
        
        
        ''' Orange Robot will start cleaning'''
        if self.__start_cleaning == True:
            print("orange: I am going to start cleaning!")
            self.list_of_dirt = []
            for y in range (len(self.__internalmap)):
                for x in range (len(self.__internalmap)):
                    if self.__internalmap[y][x] == [True, "orange"]: # intialises list of dirt
                        self.list_of_dirt.append([y, x])
            
            print("orange: ", self.list_of_dirt)
            if self.list_of_dirt == []:
                return [VWIdleAction()] # if there is no more dirt, remain idle
            
            print("Calculating closest dirt")
            
            self.calculate_closest_dirt()
            return self.move_to_dirt()
                    
                    
        else:
            return[VWIdleAction()]
        if self.move == True:
            return self.move_out_of_the_way()
        
        
        print("start_cleaning: ", self.__start_cleaning)
            
            
    
    # Finds closest dirt using pythagoras. the vector is saved
    def calculate_closest_dirt(self) ->None:
        shortest_distance = [0.0,0.0,0.0]
        current_position_y = self.get_latest_observation().get_center().get().get_coord().get_y()
        current_position_x = self.get_latest_observation().get_center().get().get_coord().get_x()
        
        for loc_of_dirt in self.list_of_dirt:
            vector_to_dirt = ((loc_of_dirt[0] - current_position_y)**2) + ((loc_of_dirt[1] - current_position_x)**2)
            vector_to_dirt = math.sqrt(vector_to_dirt)
            
            print("the vector of dirt is: ", vector_to_dirt) 
            
            if shortest_distance[0] ==0:
                shortest_distance = [vector_to_dirt, loc_of_dirt[0], loc_of_dirt[1]]
                
            elif shortest_distance[0] > vector_to_dirt:
                shortest_distance = [vector_to_dirt, loc_of_dirt[0], loc_of_dirt[1]]
            
        print(shortest_distance)
        self.closest_dirt = shortest_distance
        print("The closest_dirt is :", self.closest_dirt)
    
    # Function to move robot to closest dirt
    def move_to_dirt(self)->Iterable[VWAction]:
        list_of_dirt = self.closest_dirt
        print("orange list of dirt is:", list_of_dirt)
        
        current_position_y = self.get_latest_observation().get_center().get().get_coord().get_y() 
        current_position_x = self.get_latest_observation().get_center().get().get_coord().get_x()
        
        print("my x coord is:", current_position_x)
        print("my y coord is:", current_position_y)
        
        if(self.get_latest_observation().get_center().get().has_dirt() and self.get_latest_observation().get_center().get().get_dirt_appearance().get().get_colour().name == "orange"):
            print("I FOUND THE DIRT!!")
            '''self.__internalmap[current_position_y -1][current_position_x-1] = [False, "blank"]'''
            
            '''print(self.list_of_dirt)'''
            loc = tuple(self.get_own_position())
            self.list_of_dirt.remove([loc[1],loc[0]])
            self.__internalmap[current_position_y][current_position_x] = [False, "blank"]
            print(self.__internalmap)
            return [VWCleanAction(), VWBroadcastAction(message=self.__internalmap, sender_id= self.get_own_id())] # Cleans dirt and sends updated map
        else:
            
            if(current_position_y > list_of_dirt[1]):
                if(not self.get_own_appearance().is_facing_north()):
                    
                    return[VWTurnAction(VWDirection.left)]
                elif(current_position_y != list_of_dirt[1]):
                        
                        return[VWMoveAction()]
            
            elif(current_position_y < list_of_dirt[1]):
                if(not self.get_own_appearance().is_facing_south()):
                    
                    return[VWTurnAction(VWDirection.right)]
                elif(current_position_y != list_of_dirt[1]):
                    
                    return[VWMoveAction()]
                    
            elif(current_position_y == list_of_dirt[1]):
                if(current_position_x > list_of_dirt[2]):
                    if(not self.get_own_appearance().is_facing_west()):
                        
                        return[VWTurnAction(VWDirection.left)]
                    elif(current_position_x != list_of_dirt[2]):
                            return[VWMoveAction()]
                elif(current_position_x < list_of_dirt[2]):
                    
                    
                    if(not self.get_own_appearance().is_facing_east()):
                        
                        return[VWTurnAction(VWDirection.right)]
                    elif(current_position_x != list_of_dirt[2]):
                        
                        return[VWMoveAction()]
                else:
                    return [VWIdleAction()]
            
        
            
                
        
           
    # Moves robot out of the way    
    def move_out_of_the_way(self) ->Iterable[VWAction]:
        
        if(self.check_if_forward_exists() and not self.get_latest_observation().get_forward().get().has_actor()):
            
            self.move = False 
            return[VWMoveAction()]
        elif(self.check_if_left_exists()):
            return[VWTurnAction(VWDirection.left)]
        elif(self.check_if_right_exists()):
            return[VWTurnAction(VWDirection.right)]
        
    def check_if_left_exists(self) -> bool:
        try:
            self.get_latest_observation().get_left().get()
            return True
        except:
            return False
        
    def check_if_right_exists(self) -> bool:
        try:
            self.get_latest_observation().get_right().get()
            return True
        except:
            return False
        
    def check_if_facing_wall(self) -> bool:
        try:
            self.get_latest_observation().get_forward().get()
            return True
        except:
            return False
        

    def check_if_forward_exists(self) -> bool:
        try:
            self.get_latest_observation().get_forward().get()
            return True
        except:
            return False





if __name__ == "__main__":
    run(white_mind=MyMind(), orange_mind=OrangeMind(), green_mind=GreenMind(), efforts=VWActionEffort.REASONABLE_EFFORTS)
