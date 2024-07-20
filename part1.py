#!/usr/bin/env python3

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








class MyMind(VWActorMindSurrogate):
    def __init__(self) -> None:
        super(MyMind, self).__init__()
        self.__facing_left_wall: bool = False
        self.__bottom_right_corner: bool = False
        self.__startinternalmap: bool = False
        self.__gridsize: int = 0
        self.__internalmap: list = []
        self.__starting_position: bool = False
        self.__turncoordY: int =0
        
        # Add here all the attributes you need/want.
        
        
        
        
        
        
        

    def revise(self) -> None:
        if not self.__facing_left_wall and self.get_own_appearance().is_facing_south() and self.get_latest_observation().is_wall_immediately_ahead():
            print("I am at the southern wall - success!")

            self.__facing_left_wall = True
        elif self.__can_see_corner() and not self.__bottom_right_corner and self.get_own_appearance().is_facing_east() and self.get_latest_observation().is_wall_immediately_ahead():
            coord: PyOptional[VWCoord] = self.__get_visible_corner_coordinates()

            assert coord.is_present()

            print(f"Grid size is {coord.or_else_raise()[0]+1}x{coord.or_else_raise()[1]+1}. I'm staying idle from now on.")
            self.__gridsize = coord.or_else_raise()[0]+1
            print("The grid size n is: ", self.__gridsize)
            self.__create_list()
            
            self.__bottom_right_corner = True
        # One more step.
        elif not self.__facing_left_wall and self.get_own_appearance().is_facing_south() and self.get_latest_observation().is_wall_one_step_ahead():
            print("Almost there! One more step and I'll be at the western wall.")
            
            
            
            
            
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
        
            
            

    def decide(self) -> Iterable[VWAction]:
        if self.__facing_left_wall:
            # If we are heading the right way, move forward (in search of a wall).
            if self.__startinternalmap:
                self.__fill_list()
                
                
                
                
                # If we have reached the start of the grid, then all grid squares have been scanned
                if self.get_latest_observation().get_center().get().get_coord().get_y() == 0 and self.get_latest_observation().get_center().get().get_coord().get_x() == 0:
                    print(self.__internalmap)
                    return [VWIdleAction()]
                     
                
                
                
                # Checks if forward exists
                try:
                    if self.get_latest_observation().get_forward().get():
                            
                            if self.check_if_left_exists() :
                                
                                # if gridsize is greated than 4 in x and y
                                if(self.__gridsize > 4):
                                    if self.get_latest_observation().get_center().get().get_coord().get_y() == self.__turncoordY - 3 and self.get_latest_observation().get_center().get().get_coord().get_x() == self.__gridsize-1 and self.get_own_appearance().is_facing_north():
                                        
                                        return [VWTurnAction(direction=VWDirection.left)] # Turn left if facing north wall and have moved 3 places on side of wall
                                    else:
                                        return [VWMoveAction()]
                                else:
                                    if self.get_latest_observation().get_center().get().get_coord().get_y() == self.__turncoordY - 1 and self.get_latest_observation().get_center().get().get_coord().get_x() == self.__gridsize-1 and self.get_own_appearance().is_facing_north():
                                        
                                        return [VWTurnAction(direction=VWDirection.left)]# Turn left if facing north wall and have moved 3 places on side of wall
                                    else:
                                        return [VWMoveAction()]
                           
                            
                            else:
                                
                                
                                if(self.__gridsize > 4):
                                    
                                    if self.get_latest_observation().get_center().get().get_coord().get_y() == self.__turncoordY - 3 :
                                        
                                        return [VWTurnAction(direction=VWDirection.right)]# Turn right if facing north wall and have moved 3 places on side of wall
                                    else:
                                        
                                        return [VWMoveAction()]
                                else:
                                    if self.get_latest_observation().get_center().get().get_coord().get_y() == self.__turncoordY - 1 :
                                        
                                        return [VWTurnAction(direction=VWDirection.right)]# Turn left if facing north wall and have moved 3 places on side of wall
                                    else:
                                        
                                        return [VWMoveAction()] # Keep moving forward until above conditions have been met
                                    
                            
                            
                        
                      
                            
                            
                             
                                
                                
                 #This code block is only touched when you are facing the wall       
                except:
                    print("cant go forward") # If cannot go forward
                    
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
    
            
        
        
        
    # Fills list by checking obseravble locations for dirt
    def __fill_list(self) -> None:
            try:
                if self.get_latest_observation().get_forward().get().has_dirt():
                    coord_of_dirt = self.get_latest_observation().get_forward().get().get_coord()
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()] = True
                    
                    
            except:
                print("The forward VWLocation is out of bounds")
                
            try: 
                if self.get_latest_observation().get_forwardleft().get().has_dirt():
                    coord_of_dirt = self.get_latest_observation().get_forwardleft().get().get_coord()
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()] = True
                    
                    
            except:
                print("The forward left VWLocation is out of bounds")
        
            try:
                if self.get_latest_observation().get_forwardright().get().has_dirt():
                    coord_of_dirt = self.get_latest_observation().get_forwardright().get().get_coord()
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()] = True
                   
                    
                    
            except:
                print("The forward right VWLocation is out of bounds")     
         
            try: 
                if self.get_latest_observation().get_left().get().has_dirt():
                    coord_of_dirt = self.get_latest_observation().get_left().get().get_coord()
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()] = True
                    
                    
            except:
                    print("The left VWLocation is out of bounds")        
         
            try:
                
                if self.get_latest_observation().get_right().get().has_dirt():
                    coord_of_dirt = self.get_latest_observation().get_right().get().get_coord()
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()] = True
                    
                    
                    
            except:
                    print("The right VWLocation is out of bounds")        
                
            try:
                if self.get_latest_observation().get_center().get().has_dirt():
                    coord_of_dirt = self.get_latest_observation().get_center().get().get_coord()
                    self.__internalmap[coord_of_dirt.get_y()][coord_of_dirt.get_x()] = True
                    
            except:
                
                    print("The centre VWLocation is out of bounds")  
       
        
        
        
    # Creates 2d array. Fills with false for each place in grid.
    def __create_list(self) -> None:
        for i in range(self.__gridsize):
            holder = []
            for x in range(self.__gridsize):
                holder.append(False)
            self.__internalmap.append(holder)
            

        
        
            
    def __can_see_corner(self) -> bool:
        # We can see a corner if we can see a corner `VWLocation` in the current `VWObservation`.
        return any(loc.is_corner() for loc in self.get_latest_observation().get_locations().values())
    
    
    
    
    
    
    
    
    
    def __get_visible_corner_coordinates(self) -> PyOptional[VWCoord]:
        # We return a `PyOptional` wrapping the coordinates of the first corner `VWLocation` we can see.
        # We always check the current `VWObservation` in the same order of `VWPositionNames` (`center`, `forward`, `left`, `right`, `forwardleft`, `forwardright`).
        # We return an empty `PyOptional` if we can't see any corner.
        return PyOptional.of_nullable(next((loc.or_else_raise().get_coord() for loc in self.get_latest_observation().get_locations_in_order() if loc.is_present() and loc.or_else_raise().is_corner()), None))
    
    
    
    
    


if __name__ == "__main__":
    run(default_mind=MyMind(), efforts=VWActionEffort.REASONABLE_EFFORTS)
