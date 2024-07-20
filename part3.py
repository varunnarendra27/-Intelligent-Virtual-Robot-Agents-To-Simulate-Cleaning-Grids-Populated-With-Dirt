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
        
        self.__initialsetup = False
        
        self.__orange_to_clean: list = []
        self.__orange_coord = []
        self.__orange_ready: bool = True
        self.__green_to_clean: list = []
        self.__green_coord:list = []
        self.__green_ready: bool = True
        self.closest_dirt = []
        self.move: bool = False
        
        
        # Add here all the attributes you need/want.
         
        

    def revise(self) -> None:
        
        
        self.holder = self.get_latest_received_messages()
        print(self.holder)
        for message in self.holder:
            # Checking if White needs to move
            if message.get_content() == "Move!":
                self.move = True
            # list to set up commuunication between robots
            elif isinstance(message.get_content(), list):
                if message.get_content()[0] == "Green_Setup":
                    
                    self.__green_coord = message.get_content()[1]
                    print("Coord of Green: ", self.__green_coord)
                    
                if message.get_content()[0] == "Orange_Setup":
                    self.__orange_coord = message.get_content()[1]
                    print("Coord of Orange: ", self.__orange_coord)
                # If green finds dirt, set boolean to notify that green robot is ready for next dirt
                if message.get_content()[0] == "Green_Mind: Dirt Found":
                    if self.__green_to_clean != []:
                        self.__green_to_clean.remove(message.get_content()[1])
                        self.__green_ready = True
                    
                    self.__green_coord == message.get_content()[1]
                # If orange finds dirt, set boolean to notify that orange robot is ready for next dirt    
                if message.get_content()[0] == "Orange_Mind: Dirt Found":
                    if self.__orange_to_clean != []:
                        
                        self.__orange_to_clean.remove(message.get_content()[1])
                        self.__orange_ready = True
                    
                
                
        
        # Moves white robot to bottom right to find the gridsize
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
            
            
            
            
    # Function to move robot out of the way        
    def move_out_of_the_way(self) ->Iterable[VWAction]:
        print("test 2")
        if(self.check_if_forward_exists() and not self.get_latest_observation().get_forward().get().has_actor()):
            print("test 3")
            self.move = False 
            return[VWMoveAction()]
        elif(self.check_if_left_exists()):
            return[VWTurnAction(VWDirection.left)]
        elif(self.check_if_right_exists()):
            return[VWTurnAction(VWDirection.right)]
        
    # Functions to check if certain squares exist
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
    
    
    
    
    
    
    
    # Caclulates closest green dirt by using pythagoras to find a vector
    def calculate_closest_green_dirt(self) ->None:
        shortest_distance = [0.0,0.0]
        shortest_vector = 0.0
        current_position_y = self.__green_coord[0]
        current_position_x = self.__green_coord[1]
        
        for loc_of_dirt in self.__green_to_clean:
            vector_to_dirt = ((loc_of_dirt[0] - current_position_y)**2) + ((loc_of_dirt[1] - current_position_x)**2)
            vector_to_dirt = math.sqrt(vector_to_dirt)
            
            print("white mind: the vector of dirt is: ", vector_to_dirt) 
            
            if shortest_vector ==0:
                shortest_distance = [loc_of_dirt[0], loc_of_dirt[1]]
                
            elif shortest_vector > vector_to_dirt:
                shortest_distance = [loc_of_dirt[0], loc_of_dirt[1]]
            
        print(shortest_distance)
        self.closest_dirt = shortest_distance
        
        print("white_mind: The closest_dirt is :", self.closest_dirt)
        
        
    # Caclulates closest orange dirt by using pythagoras to find a vector    
    def calculate_closest_orange_dirt(self) ->None:
        shortest_distance = [0.0,0.0]
        shortest_vector = 0.0
        current_position_y = self.__orange_coord[0]
        current_position_x = self.__orange_coord[1]
        
        for loc_of_dirt in self.__orange_to_clean:
            vector_to_dirt = ((loc_of_dirt[0] - current_position_y)**2) + ((loc_of_dirt[1] - current_position_x)**2)
            vector_to_dirt = math.sqrt(vector_to_dirt)
            
            print("white mind: the vector of dirt is: ", vector_to_dirt) 
            
            if shortest_vector ==0:
                shortest_distance = [loc_of_dirt[0], loc_of_dirt[1]]
                
            elif shortest_vector > vector_to_dirt:
                shortest_distance = [loc_of_dirt[0], loc_of_dirt[1]]
            
        print(shortest_distance)
        self.closest_dirt = shortest_distance
        
        print("white_mind: The closest_dirt is :", self.closest_dirt)
    

    def decide(self) -> Iterable[VWAction]:
        
        if self.move == True:
            return self.move_out_of_the_way()
        # Checks if there is a robot in the way. Sennds appropriate broadcast message if this is the case
        if self.check_if_forward_exists():
            if self.get_latest_observation().get_forward().get().has_actor() :
                if self.get_latest_observation().get_forward().get().get_actor_appearance().get().get_colour().name == "green":
                    return [VWBroadcastAction(message="Move Green!", sender_id= self.get_own_id())]
                elif self.get_latest_observation().get_forward().get().get_actor_appearance().get().get_colour().name == "orange":
                    return [VWBroadcastAction(message="Move Orange!", sender_id= self.get_own_id())]
                
        if self.__start_cleaning == True:
            print("white_mind: I am going to start cleaning!")
            self.list_of_dirt = []
            
            
            if self.__initialsetup == False:
                self.__initialsetup = True
                # Intialises internal map of dirt
                for y in range (len(self.__internalmap)):
                    for x in range (len(self.__internalmap)):
                        if self.__internalmap[y][x] == [True, "green"]:
                            self.__green_to_clean.append([y, x])
                        elif self.__internalmap[y][x] == [True, "orange"]:
                            self.__orange_to_clean.append([y, x])
            
            
            print("white_mind: The green dirt to clean is ", self.__green_to_clean)
            print("white_mind: The orange dirt to clean is ", self.__orange_to_clean)
            
            # Broadcasts next to dirt to travel to for both orange and green
            if self.__green_ready == True:
                self.__green_ready = False
                if self.__green_to_clean != []:
                    self.calculate_closest_green_dirt()
                    print("white_mind: I am about to send a new a go_to. The next dirt will be ", self.closest_dirt)
                    return [VWBroadcastAction(message=["green_go_to", [self.closest_dirt]], sender_id= self.get_own_id())]
            if self.__orange_ready == True:
                print("orange_ready is ", self.__orange_ready)
                self.__orange_ready = False
                if self.__orange_to_clean != []:
                    self.calculate_closest_orange_dirt()
                    print("white_mind: I am about to send a new a go_to. The next dirt will be ", self.closest_dirt)
                    return [VWBroadcastAction(message=["orange_go_to", [self.closest_dirt]], sender_id= self.get_own_id())]
            else: return [VWIdleAction()]
            
                    
                    
            
        
        if self.__facing_left_wall:
            # If we are heading the right way, move forward (in search of a wall).
            if self.__startinternalmap:
                
                self.__fill_list()
                # If we have reached the start ofo the grid, then all grid squares have been scanned
                
                if self.get_latest_observation().get_center().get().get_coord().get_y() == 0 and self.get_latest_observation().get_center().get().get_coord().get_x() == 0:
                     
                     
                    
                    self.__start_cleaning = True
                    return [VWBroadcastAction(message=self.__internalmap, sender_id= self.get_own_id())]
                     
                     
                
                
                
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
    
            
        
        
        
    # Function to scan observable vwlocations for dirt and store inside internal map
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
       
            
       
        
        
    # Initialising internal map using 3d array. It also stores the colour type
    
    def __create_list(self) -> None:
        for i in range(self.__gridsize):
            holder = []
            for x in range(self.__gridsize):
                holder.append([False, "blank"])
            self.__internalmap.append(holder)
            
        print(self.__internalmap)
        
        
    # Checks to see if corner is visible        
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
        self.__active_message: list = []
        self.__start_cleaning: bool = False
        self.__initialsetup: bool = False
        self.closest_dirt: list = []
        
        
    
    def revise(self) -> None:
        
        
        self.holder = self.get_latest_received_messages()
        print(self.holder)
        for message in self.holder:
            print("Green_Mind: ", message.get_content())
            # Checkes if robot is in the way
            if message.get_content() == "Move Green!":
                self.move = True
                
            elif isinstance(message.get_content(), list):
                # Checks if green go to notification has been sent. Oulines where the next dirt is
                if message.get_content()[0] == "green_go_to":
                    self.__active_message = message.get_content()[1]
                    self.__start_cleaning = True
            
            
    def decide(self) -> Iterable[VWAction]:
        if self.move == True:
            return self.move_out_of_the_way()
        
        if self.check_if_forward_exists():
            if self.get_latest_observation().get_forward().get().has_actor() :
                if self.get_latest_observation().get_forward().get().get_actor_appearance().get().get_colour().name == "white":
                    return [VWBroadcastAction(message="Move!", sender_id= self.get_own_id())]
                elif self.get_latest_observation().get_forward().get().get_actor_appearance().get().get_colour().name == "orange":
                    return [VWBroadcastAction(message="Move Orange!", sender_id= self.get_own_id())]
        
        if self.__initialsetup == False:
            
            self.__initialsetup = True
            message_to_send = ["Green_Setup", [self.get_latest_observation().get_center().get().get_coord().get_y(), self.get_latest_observation().get_center().get().get_coord().get_x()]]
            return [VWBroadcastAction(message=message_to_send, sender_id= self.get_own_id())]
                # Initial broadcast so white robot knows what green robot's starting location is
        
        
        print("start_cleaning: ", self.__start_cleaning)
        print("green_mind: Active message is ", self.__active_message)
        
        ''' Green Robot will start cleaning'''
        
        if self.__active_message == []:
            print("Green_Mind: I am going to stay idle") # If no messsages, stay idle
            return[VWIdleAction()]
        
        if self.__start_cleaning == True:
            print("Green_Mind: I am going to start cleaning!")
           
            return self.move_to_dirt()
                    
                    
        else:
            return[VWIdleAction()]
            
    # Function to move robot to specific dirt. Moves in the Y axis and then the x axis.
    def move_to_dirt(self)->Iterable[VWAction]:
        list_of_dirt = self.__active_message[0]
        print("The closest_dirt is: ", self.__active_message) 
        

        current_position_y = self.get_latest_observation().get_center().get().get_coord().get_y() # finds current coordinates
        current_position_x = self.get_latest_observation().get_center().get().get_coord().get_x()
        
        
        if(self.get_latest_observation().get_center().get().has_dirt() and self.get_latest_observation().get_center().get().get_dirt_appearance().get().get_colour().name == "green"):
            print("Green_Mind: I found the dirt!")
            
            loc = tuple(self.get_own_position())
            self.__active_message = []
            message_to_send = ["Green_Mind: Dirt Found", [current_position_y, current_position_x]]
            
            return [VWCleanAction(), VWBroadcastAction(message=message_to_send, sender_id= self.get_own_id())]
        else:
            
            if(current_position_y > list_of_dirt[0]):
                if(not self.get_own_appearance().is_facing_north()):
                    
                    return[VWTurnAction(VWDirection.left)]
                elif(current_position_y != list_of_dirt[0]):
                        
                        return[VWMoveAction()]
            
            elif(current_position_y < list_of_dirt[0]):
                if(not self.get_own_appearance().is_facing_south()):
                    
                    return[VWTurnAction(VWDirection.right)]
                elif(current_position_y != list_of_dirt[0]):
                    
                    return[VWMoveAction()]
                    
            elif(current_position_y == list_of_dirt[0]):
                if(current_position_x > list_of_dirt[1]):
                    if(not self.get_own_appearance().is_facing_west()):
                        
                        return[VWTurnAction(VWDirection.left)]
                    elif(current_position_x != list_of_dirt[1]):
                            return[VWMoveAction()]
                elif(current_position_x < list_of_dirt[1]):
                    
                    if(not self.get_own_appearance().is_facing_east()):
                        
                        return[VWTurnAction(VWDirection.right)]
                    elif(current_position_x != list_of_dirt[1]):
                        
                        return[VWMoveAction()]
                else:
                    return [VWIdleAction()]
                
    # Function to move robot out of another robots way            
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
        self.__active_message: list = []
        self.__start_cleaning: bool = False
        self.__initialsetup: bool = False
        self.closest_dirt: list = []
        
        
    
    def revise(self) -> None:
        
        self.holder = self.get_latest_received_messages()
        print(self.holder)
        for message in self.holder:
            print("Orange_Mind: ", message.get_content())
            
            if message.get_content() == "Move Orange!":# checks if orange needs to move
                self.move = True
            # Checks for orange_go_to broadcast, sending next dirt to go to.    
            elif isinstance(message.get_content(), list):
                if message.get_content()[0] == "orange_go_to":
                    print("orange_mind: I have recieved a go to!")
                    self.__active_message = message.get_content()[1]
                    self.__start_cleaning = True
            
            
    def decide(self) -> Iterable[VWAction]:
        if self.move == True:
            return self.move_out_of_the_way()
        # Checking if anything is in the way
        if self.check_if_forward_exists():
            if self.get_latest_observation().get_forward().get().has_actor() :# Checks if there is an actor in front
                if self.get_latest_observation().get_forward().get().get_actor_appearance().get().get_colour().name == "white":
                    return [VWBroadcastAction(message="Move!", sender_id= self.get_own_id())]
                elif self.get_latest_observation().get_forward().get().get_actor_appearance().get().get_colour().name == "green":
                    return [VWBroadcastAction(message="Move Orange!", sender_id= self.get_own_id())]
        
        if self.__initialsetup == False:
            
            self.__initialsetup = True
            message_to_send = ["Orange_Setup", [self.get_latest_observation().get_center().get().get_coord().get_y(), self.get_latest_observation().get_center().get().get_coord().get_x()]]
            return [VWBroadcastAction(message=message_to_send, sender_id= self.get_own_id())]
            
        
        
        print("start_cleaning: ", self.__start_cleaning)
        print("orange_mind: Active message is ", self.__active_message)
        
        ''' Orange Robot will start cleaning'''
        
        if self.__active_message == []:
            print("orange_Mind: I am going to stay idle") # Stays idle if there are no messages from white robot
            return[VWIdleAction()]
        
        if self.__start_cleaning == True:
            print("Orange_Mind: I am going to start cleaning!")
           
            return self.move_to_dirt()
                    
                    
        else:
            return[VWIdleAction()]
            
    # Moves robot to dirt using active message from white robot
    def move_to_dirt(self)->Iterable[VWAction]:
        list_of_dirt = self.__active_message[0]
        print("The closest_dirt is: ", self.__active_message)
        

        current_position_y = self.get_latest_observation().get_center().get().get_coord().get_y() 
        current_position_x = self.get_latest_observation().get_center().get().get_coord().get_x()
        
        
        if(self.get_latest_observation().get_center().get().has_dirt() and self.get_latest_observation().get_center().get().get_dirt_appearance().get().get_colour().name == "orange"):
            print("Orange_Mind: I found the dirt!")
            '''self.__internalmap[current_position_y -1][current_position_x-1] = [False, "blank"]'''
            
            '''print(self.list_of_dirt)'''
            loc = tuple(self.get_own_position())
            self.__active_message = []
            message_to_send = ["Orange_Mind: Dirt Found", [current_position_y, current_position_x]]
            
            return [VWCleanAction(), VWBroadcastAction(message=message_to_send, sender_id= self.get_own_id())]
        else:
            
            if(current_position_y > list_of_dirt[0]):
                if(not self.get_own_appearance().is_facing_north()):
                    
                    return[VWTurnAction(VWDirection.left)]
                elif(current_position_y != list_of_dirt[0]):
                        
                        return[VWMoveAction()]
            
            elif(current_position_y < list_of_dirt[0]):
                if(not self.get_own_appearance().is_facing_south()):
                    
                    return[VWTurnAction(VWDirection.right)]
                elif(current_position_y != list_of_dirt[0]):
                    
                    return[VWMoveAction()]
                    
            elif(current_position_y == list_of_dirt[0]):
                if(current_position_x > list_of_dirt[1]):
                    if(not self.get_own_appearance().is_facing_west()):
                        
                        return[VWTurnAction(VWDirection.left)]
                    elif(current_position_x != list_of_dirt[1]):
                            return[VWMoveAction()]
                elif(current_position_x < list_of_dirt[1]):
                    
                    if(not self.get_own_appearance().is_facing_east()):
                        
                        return[VWTurnAction(VWDirection.right)]
                    elif(current_position_x != list_of_dirt[1]):
                        
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
            
        
    # Functiona to check if vwlocations in observable space exist
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
