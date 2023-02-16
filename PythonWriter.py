from __future__ import annotations

import functools
from dataclasses import dataclass, field
import inspect
from .robodk import *
from .BasePost import BasePost, BaseRoboDKConfig
from functools import wraps


# https://stackoverflow.com/a/73312204
def function_details(f):
    assert (callable(f))

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        siggy = inspect.signature(f)
        bound_siggy = siggy.bind(*args, **kwargs)
        bound_siggy.arguments.pop('self')
        all_sargs = ", ".join(kw + "=" + repr(arg) for kw, arg in bound_siggy.arguments.items())
        obj: BasePost = args[0]

        outstr = f"robot.{f.__name__}({all_sargs})"
        # print("robot.", f.__name__, "(", all_sargs, ")", sep="")
        print(outstr)
        obj.PROG.append(outstr)
        return f(*args, **kwargs)

    return wrapper


@dataclass
class RoboDKConfig(BaseRoboDKConfig):
    robot_post: str = "PythonWriter"


class RobotPost(BasePost):

    def __init__(self, robotpost=None, robotname=None, robot_axes=6, **kwargs):
        super().__init__(robotpost, robotname, robot_axes, **kwargs)
        self.PROG = []

    @function_details
    def ProgStart(self, progname):
        print('')
        pass

    @function_details
    def ProgFinish(self, progname):
        pass

    @function_details
    def ProgSave(self, folder, progname, ask_user=False, show_result=False):
        # raise Exception('###@todo, must actually save')
        pass

    @function_details
    def MoveJ(self, pose, joints, conf_RLF=None):
        pass

    @function_details
    def MoveL(self, pose, joints, conf_RLF=None):
        pass

    @function_details
    def MoveC(self, pose1, joints1, pose2, joints2, conf_RLF_1=None, conf_RLF_2=None):
        pass

    @function_details
    def setFrame(self, pose, frame_id=None, frame_name=None):
        pass

    @function_details
    def setTool(self, pose, tool_id=None, tool_name=None):
        pass

    @function_details
    def Pause(self, time_ms):
        pass

    @function_details
    def setSpeed(self, speed_mms):
        pass

    @function_details
    def setAcceleration(self, accel_mmss):
        pass

    @function_details
    def setSpeedJoints(self, speed_degs):
        pass

    @function_details
    def setAccelerationJoints(self, accel_degss):
        pass

    @function_details
    def setZoneData(self, zone_mm):
        pass

    @function_details
    def setDO(self, io_var, io_value):
        pass

    @function_details
    def waitDI(self, io_var, io_value, timeout_ms=-1):
        pass

    @function_details
    def RunCode(self, code, is_function_call=False):
        pass

    @function_details
    def RunMessage(self, message, iscomment=False):
        pass

    @function_details
    def addline(self, newline):
        pass

    @function_details
    def addlog(self, newline):
        pass
