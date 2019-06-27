"""
    This is Pycao, a modeler and raytracer interpreter for 3D drawings
    Copyright (C) 2015  Laurent Evain

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


from uservariables import *
from generic import *
from mathutils import *
from aliases import *
from genericwithmaths import *
from elaborate import *
from compound import *
import povrayshoot 
from cameras import *


        
class Light(ObjectInWorld):
    """
    A light with a hook, added by default to the cameras already created.
    """
    def __init__(self,location=origin,shadow=True,lightType=defaultLightType,cameraList=camerasInScene):
        if not hasattr(self,"info"):
            self.info=Object()
        self.location=location
        self.add_hook("location",location)
        if not shadow:
            self.info.rgbIntensity=defaultShadowlesslightRgbIntensity
        else:
            self.info.rgbIntensity=defaultShadowlightRgbIntensity
        if not shadow:
            self.info.rgb=shadowlesslightDefaultRgb
        else:
            self.info.rgb=shadowlightDefaultRgb
        self.lightType=lightType
        self.shadow=shadow
        for camera in cameraList:
            camera.lights.append(self)
    def move_alone(self,M):
        self.location=M*self.location
        return self
    def location_string(self):
        return "<"+str(self.location[0])+","+str(self.location[1])+","+str(self.location[2])+">"
    def shadow_string(self):
        if not self.shadow:
            return "shadowless "
        else:
            return ""
    def color_string(self):
        if hasattr(self.info,"color")and self.info.color is not None:
            string=self.info.color
        elif hasattr(self.info,"rgb") and self.info.rgb is not None:
            i=self.info.rgbIntensity
            r=self.info.rgb
            string="rgb <"+str(i*r[0])+","+str(i*r[1])+","+str(i*r[2])+"> "
        else: return " "
        return "color "+string
    def povray_string(self):
        string="light_source {"+self.location_string()+ self.color_string()+ self.lightType +" "+ self.shadow_string()+"}\n"
        return string

    
class PhysicalLamp(Compound):
    """" returns an object with 2 hooks, one for the light, one for hanging on the wall/ceiling """
    def __init__(self):#an empty lamp,often useful
            self.add_hook("ceiling",origin)
            self.add_hook("light",origin)

    @staticmethod
    def conical():
        self=PhysicalLamp()
        cone=Cone(origin-.05*Z,origin+.2*Z,.4,.20,booleanOpen=True)
        cone.rgbed([.55,.5,.5])
        cone.name="Lampe"
        cylinder1=Cylinder(origin+.2*Z,origin+.3*Z,0.005).colored("Black")
        cylinder2=Cylinder(origin+.3*Z,origin+.32*Z,.05).colored("Black")
        self.add_list_to_compound([cone,cylinder2,cylinder1])
        self.add_hook("ceiling",origin+.32*Z)
        self.add_hook("light",origin-.2*Z)
        return self


        
class Lamp(Compound):
    """ a union of a light and a physicallamp, it comes with a hook. The light is by default added to the list of existing cameras when it 
    is created """ 
    def __init__(self,physicalLamp=None,shadowfull=None,shadowless=None,cameraList=None):
        if physicalLamp is None:
            physicalLamp=PhysicalLamp.conical()
        elif physicalLamp == False:
            physicalLamp=PhysicalLamp() #an empty compound with 2 hooks for consistency
        if shadowfull is None:
            shadowfull=Light() # a light
        if shadowless is None:
            shadowless=Light(shadow=False)
        self.add_list_to_compound([["object",physicalLamp]])
        if not shadowfull==False:
            self.add_to_compound(["shadowfull",shadowfull])
            shadowfull.hooked_on(physicalLamp)
        if not shadowless==False:
            self.add_to_compound(["shadowless",shadowless])
            shadowless.hooked_on(physicalLamp)
        physicalLamp.select_hook("light") # since the lamp has an other hook to the ceiling
        self.add_hook("ceiling",physicalLamp.hook("ceiling"))
        
