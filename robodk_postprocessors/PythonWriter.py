from __future__ import annotations

import functools
import inspect
import reprlib
from dataclasses import dataclass
from pathlib import Path

from numpy import format_float_positional  # We need numpy installed anyway

from .BasePost import BasePost, BaseRoboDKConfig


class FloatRepr(reprlib.Repr):
    """Overrides repr(float) (way harder than it should be), preventing scientific notation and
    limiting decimals"""

    def _repr_iterable(self, x, level, left, right, maxiter, trail=''):
        """
        Calls the base _repr_iterable without a max iteration limit, so that the full list/dict
        will format
        """
        return super()._repr_iterable(x, level, left, right, len(x), trail)

    def repr_float(self, value, level) -> str:
        return format_float_positional(value, precision=5, trim='0')


my_repr_inst = FloatRepr()
my_repr = my_repr_inst.repr


# https://stackoverflow.com/a/73312204
def function_details(f, *, indent=True):
    assert (callable(f))

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        prefix = "\t" if indent else ""

        siggy = inspect.signature(f)
        bound_siggy = siggy.bind(*args, **kwargs)
        bound_siggy.arguments.pop('self')  # Remove self from args for display
        all_sargs = ", ".join(kw + "=" + my_repr(arg) for kw, arg in bound_siggy.arguments.items())
        outstr = f"{prefix}robot.{f.__name__}({all_sargs})"
        print(outstr)
        # Add the line to the RobotPost object
        obj: BasePost = args[0]
        obj.addline(outstr)

        return f(*args, **kwargs)

    return wrapper


@dataclass
class RoboDKConfig(BaseRoboDKConfig):
    robot_post: str = "PythonWriter"
    real_robot_post: str = ""


class RobotPost(BasePost):
    PROG_EXT = "py"

    def __init__(self, robotpost=None, robotname=None, robot_axes=6, **kwargs):
        super().__init__(robotpost, robotname, robot_axes, **kwargs)
        self.PROG = []
        self.top_lines = []
        self.real_robot_post: str = ""
        self.config: dict[str, any] = {}

    @classmethod
    def from_config(cls, config: BaseRoboDKConfig | dict) -> BasePost:
        ret = super().from_config(config)
        ret.config = config
        return ret

    def _add_python_header(self):
        top_lines: list[str] = []

        file_loc = inspect.getfile(type(self))
        file_path = Path(file_loc)
        dir_path = file_path.parent.parent

        top_lines.append("import sys\nimport os")
        top_lines.append(f"sys.path.insert(0, '{dir_path}')")
        top_lines.append(f"from robodk_postprocessors.{self.real_robot_post} import RobotPost\n\n")
        top_lines.append('def run_post():')
        top_lines.append(f"\trobot = RobotPost('{self.real_robot_post}', '{self.ROBOT_NAME}',"
                         f" {self.nAxes})")

        # Add necessary config entries, remove the basic ones
        cfg_to_remove = ['real_robot_post', 'robot_post', 'robot_name', 'robot_axes']
        extra_cfg = {k: v for k, v in self.config.items() if k not in cfg_to_remove}
        for k, v in extra_cfg.items():
            top_lines.append(f"\trobot.{k} = {my_repr(v)}")

        self.top_lines = top_lines

    @function_details
    def ProgStart(self, progname):
        pass

    @function_details
    def ProgFinish(self, progname):
        pass

    def ProgSave(self, folder, progname, ask_user=False, show_result=False):
        outdir = Path(folder)
        outdir.mkdir(exist_ok=True)
        outfile = Path(f'{folder}/{progname}.{self.PROG_EXT}')
        self.PROG_FILES = [str(outfile)]

        self._add_python_header()

        with outfile.open(mode='w') as f:
            for line in self.top_lines:
                f.write(line + "\n")
            for line in self.PROG:
                f.write(line + "\n")

            f.write(f"\trobot.ProgSave('{folder}', '{progname}')\n")

            f.write('if __name__== "__main__":\n')
            f.write('\trun_post()')

        self.PROG = []
        self.top_lines = []

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

    def addline(self, newline: str):
        self.PROG.append(newline)

    @function_details
    def addlog(self, newline):
        pass
