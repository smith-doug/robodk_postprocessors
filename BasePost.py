# Copyright 2015-2021 - RoboDK Inc. - https://robodk.com/
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ----------------------------------------------------
# This file is a sample POST PROCESSOR script to generate programs
# for a generic robot with RoboDK
#
# To edit/test this POST PROCESSOR script file:
# Select "Program"->"Add/Edit Post Processor", then select your post or create a new one.
# You can edit this file using any text editor or Python editor. Using a Python editor allows to
# quickly evaluate a sample program at the end of this file.
# Python should be automatically installed with RoboDK
#
# You can also edit the POST PROCESSOR manually:
#    1- Open the *.py file with Python IDLE (right click -> Edit with IDLE)
#    2- Make the necessary changes
#    3- Run the file to open Python Shell: Run -> Run module (F5 by default)
#    4- The "test_post()" function is called automatically
# Alternatively, you can edit this file using a text editor and run it with Python
#
# To use a POST PROCESSOR file you must place the *.py file in "C:/RoboDK/Posts/"
# To select a specific POST PROCESSOR for your robot in RoboDK you must follow these steps:
#    1- Open the robot panel (double click a robot)
#    2- Select "Parameters"
#    3- Select "Unlock advanced options"
#    4- Select your post as the file name in the "Robot brand" box
#
# To delete an existing POST PROCESSOR script, simply delete this file (.py file)
#
# ----------------------------------------------------
# More information about RoboDK Post Processors and Offline Programming here:
#      http://www.robodk.com/help#PostProcessor
#      http://www.robodk.com/doc/PythonAPI/postprocessor.html
# ----------------------------------------------------

# ----------------------------------------------------
# Import RoboDK tools
from robodk.robomath import *
from robodk.robodialogs import *
from robodk.robofileio import *


# ----------------------------------------------------
def pose_2_str(pose):
    """Converts a robot pose target to a string according to the syntax/format of the controller.

    :param pose: 4x4 pose matrix
    :type pose: :meth:`robodk.robomath.Mat`
    :return: postion as a XYZWPR string
    :rtype: str
    """
    [x, y, z, r, p, w] = pose_2_xyzrpw(pose)
    return ('X%.3f Y%.3f Z%.3f R%.3f P%.3f W%.3f' % (x, y, z, r, p, w))


def joints_2_str(joints):
    """Converts a robot joint target to a string according to the syntax/format of the controller.

    :param joints: robot joints as a list
    :type joints: float list
    :return: joint format as a J1-Jn string
    :rtype: str
    """
    str = ''
    data = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    for i in range(len(joints)):
        str = str + ('%s%.6f ' % (data[i], joints[i]))
    str = str[:-1]
    return str


# ----------------------------------------------------
# Object class that handles the robot instructions/syntax
class RobotPost(object):
    """Robot Post Processor object"""

    # Set the program extension
    PROG_EXT = 'txt'

    # --------------------------------------------------------
    # other variables
    ROBOT_POST = ''
    ROBOT_NAME = ''
    PROG_FILES = []

    PROG = []
    LOG = ''
    nAxes = 6

    def __init__(self, robotpost=None, robotname=None, robot_axes=6, **kwargs):
        """Create a new post processor.

        :param robotpost: name of the post processor
        :type robotpost: str
        :param robotname: name of the robot
        :type robotname: str
        :param robot_axes: number of axes of the robot
        :type robot_axes: int
        """
        self.ROBOT_POST = robotpost
        self.ROBOT_NAME = robotname
        self.PROG = []
        self.LOG = ''
        self.nAxes = robot_axes

    def ProgStart(self, progname):
        """Start a new program given a name. Multiple programs can be generated at the same times.

        **Tip**:
        ProgStart is triggered every time a new program must be generated.

        :param progname: name of the program
        :type progname: str
        """
        self.addline('PROC %s()' % progname)

    def ProgFinish(self, progname):
        """This method is executed to define the end of a program or procedure. One module may
        have more than one program. No other instructions will be executed before another
        :meth:`samplepost.RobotPost.ProgStart` is executed.

        **Tip**:
        ProgFinish is triggered after all the instructions of the program.

        :param progname: name of the program
        :type progname: str
        """
        self.addline('ENDPROC')

    def ProgSave(self, folder, progname, ask_user=False, show_result=False):
        """Saves the program. This method is executed after all programs have been processed.

        **Tip**:
        ProgSave is triggered after all the programs and instructions have been executed.

        :param folder: Folder hint to save the program
        :type folder: str
        :param progname: Program name as a hint to save the program
        :type progname: str
        :param ask_user: True if the default settings in RoboDK are set to prompt the user to
        select the folder
        :type ask_user: bool, str
        :param show_result: False if the default settings in RoboDK are set to not show the
        program once it has been saved. Otherwise, a string is provided with the path of the
        preferred text editor
        :type show_result: bool, str
        """
        progname = progname + '.' + self.PROG_EXT
        if ask_user or not DirExists(folder):
            filesave = getSaveFile(folder, progname, 'Save program as...')
            if filesave is not None:
                filesave = filesave.name
            else:
                return
        else:
            filesave = folder + '/' + progname

        # Japanese controllers need the shift_jis codec and replace errors to not throw errors on
        # non supported characters

        # with open(filesave, "w", encoding="shift_jis", errors="replace") as fid:
        with open(filesave, "w", encoding="utf-8") as fid:
            for line in self.PROG:
                fid.write(line)
                fid.write("\n")

        print('SAVED: %s\n' % filesave)
        # ---------------------- show result
        if show_result:
            if type(show_result) is str:
                # Open file with provided application
                import subprocess
                p = subprocess.Popen([show_result, filesave])
            else:
                # open file with default application
                import os
                os.startfile(filesave)

            if len(self.LOG) > 0:
                mbox('Program generation LOG:\n\n' + self.LOG)

    def ProgSendRobot(self, robot_ip, remote_path, ftp_user, ftp_pass):
        """Send a program to the robot using the provided parameters. This method is executed
        right after ProgSave if we selected the option "Send Program to Robot".
        The connection parameters must be provided in the robot connection menu of RoboDK.

        :param robot_ip: IP address of the robot
        :type robot_ip: str
        :param remote_path: Remote path of the robot
        :type remote_path: str
        :param ftp_user: FTP user credential
        :type ftp_user: str
        :param ftp_pass: FTP user password
        :type ftp_pass: str
        """
        UploadFTP(self.PROG_FILES, robot_ip, remote_path, ftp_user, ftp_pass)

    def MoveJ(self, pose, joints, conf_RLF=None):
        """Defines a joint movement.

        **Tip**:
        MoveJ is triggered by the RoboDK instruction Program->Move Joint Instruction.

        :param pose: pose target of the tool with respect to the reference frame. Pose can be
        None if the target is defined as a joint target
        :type pose: :meth:`robodk.robomath.Mat`
        :param joints: robot joints as a list
        :type joints: float list
        :param conf_RLF: robot configuration as a list of 3 ints: [REAR, LOWER-ARM, FLIP]. [0,0,
        0] means [front, upper arm and non-flip] configuration
        :type conf_RLF: int list
        """
        self.addline('MOVJ ' + joints_2_str(joints))

    def MoveL(self, pose, joints, conf_RLF=None):
        """Defines a linear movement.

        **Tip**:
        MoveL is triggered by the RoboDK instruction Program->Move Linear Instruction.

        :param pose: pose target of the tool with respect to the reference frame. Pose can be
        None if the target is defined as a joint target
        :type pose: :meth:`robodk.robomath.Mat`
        :param joints: robot joints as a list
        :type joints: float list
        :param conf_RLF: robot configuration as a list of 3 ints: [REAR, LOWER-ARM, FLIP]. [0,0,
        0] means [front, upper arm and non-flip] configuration
        :type conf_RLF: int list
        """
        self.addline('MOVL ' + pose_2_str(pose))

    def MoveC(self, pose1, joints1, pose2, joints2, conf_RLF_1=None, conf_RLF_2=None):
        """Defines a circular movement.

        **Tip**:
        MoveC is triggered by the RoboDK instruction Program->Move Circular Instruction.

        :param pose1: pose target of a point defining an arc (waypoint)
        :type pose1: :meth:`robodk.robomath.Mat`
        :param pose2: pose target of the end of the arc (final point)
        :type pose2: :meth:`robodk.robomath.Mat`
        :param joints1: robot joints of the waypoint
        :type joints1: float list
        :param joints2: robot joints of the final point
        :type joints2: float list
        :param conf_RLF_1: robot configuration of the waypoint
        :type conf_RLF_1: int list
        :param conf_RLF_2: robot configuration of the final point
        :type conf_RLF_2: int list
        """
        self.addline('MOVC ' + pose_2_str(pose1) + ' ' + pose_2_str(pose2))

    def setFrame(self, pose, frame_id=None, frame_name=None):
        """Defines a new reference frame with respect to the robot base frame. This reference
        frame is used for following pose targets used by movement instructions.

        **Tip**:
        setFrame is triggered by the RoboDK instruction Program->Set Reference Frame Instruction.

        :param pose: pose of the reference frame with respect to the robot base frame
        :type pose: :meth:`robodk.robomath.Mat`
        :param frame_id: number of the reference frame (if available)
        :type frame_id: int, None
        :param frame_name: Name of the reference frame as defined in RoboDK
        :type frame_name: str
        """
        self.addline('BASE_FRAME ' + pose_2_str(pose))

    def setTool(self, pose, tool_id=None, tool_name=None):
        """Change the robot TCP (Tool Center Point) with respect to the robot flange. Any
        movement defined in Cartesian coordinates assumes that it is using the last reference
        frame and tool frame provided.

        **Tip**:
        setTool is triggered by the RoboDK instruction Program->Set Tool Frame Instruction.

        :param pose: pose of the TCP frame with respect to the robot base frame
        :type pose: :meth:`robodk.robomath.Mat`
        :param tool_id: number of the reference frame (if available)
        :type tool_id: int, None
        :param tool_name: Name of the reference frame as defined in RoboDK
        :type tool_name: str
        """
        self.addline('TOOL_FRAME ' + pose_2_str(pose))

    def Pause(self, time_ms):
        """Defines a pause in a program (including movements). time_ms is negative if the pause
        must provoke the robot to stop until the user desires to continue the program.

        **Tip**:
        Pause is triggered by the RoboDK instruction Program->Pause Instruction.

        :param time_ms: time of the pause, in milliseconds
        :type time_ms: float
        """
        if time_ms < 0:
            self.addline('PAUSE')
        else:
            self.addline('WAIT %.3f' % (time_ms * 0.001))

    def setSpeed(self, speed_mms):
        """Changes the robot speed (in mm/s)

        **Tip**:
        setSpeed is triggered by the RoboDK instruction Program->Set Speed Instruction.

        :param speed_mms: speed in :math:`mm/s`
        :type speed_mms: float
        """
        self.addlog('setSpeed not defined (%.2f mms)' % speed_mms)

    def setAcceleration(self, accel_mmss):
        """Changes the robot acceleration (in mm/s2)

        **Tip**:
        setAcceleration is triggered by the RoboDK instruction Program->Set Speed Instruction. An
        acceleration value must be provided.

        :param accel_mmss: speed in :math:`mm/s^2`
        :type accel_mmss: float
        """
        self.addlog('setAcceleration not defined')

    def setSpeedJoints(self, speed_degs):
        """Changes the robot joint speed (in deg/s)

        **Tip**:
        setSpeedJoints is triggered by the RoboDK instruction Program->Set Speed Instruction. A
        joint speed value must be provided.

        :param speed_degs: speed in :math:`deg/s`
        :type speed_degs: float
        """
        self.addlog('setSpeedJoints not defined')

    def setAccelerationJoints(self, accel_degss):
        """Changes the robot joint acceleration (in deg/s2)

        **Tip**:
        setAccelerationJoints is triggered by the RoboDK instruction Program->Set Speed
        Instruction. A joint acceleration value must be provided.

        :param accel_degss: speed in :math:`deg/s^2`
        :type accel_degss: float
        """
        self.addlog('setAccelerationJoints not defined')

    def setZoneData(self, zone_mm):
        """Changes the smoothing radius (also known as rounding, blending radius, CNT,
        APO or zone data). If this parameter is higher it helps making the movement smoother

        **Tip**:
        setZoneData is triggered by the RoboDK instruction Program->Set Rounding Instruction.

        :param zone_mm: rounding radius in mm
        :type zone_mm: float
        """
        self.addlog('setZoneData not defined (%.1f mm)' % zone_mm)

    def setDO(self, io_var, io_value):
        """Sets a variable (usually a digital output) to a given value. This method can also be
        used to set other variables.

        **Tip**:
        setDO is triggered by the RoboDK instruction Program->Set or Wait I/O Instruction.

        :param io_var: variable to set, provided as a str or int
        :type io_var: int, str
        :param io_value: value of the variable, provided as a str, float or int
        :type io_value: int, float, str
        """
        if type(io_var) != str:  # set default variable name if io_var is a number
            io_var = 'OUT[%s]' % str(io_var)
        if type(io_value) != str:  # set default variable value if io_value is a number
            if io_value > 0:
                io_value = 'TRUE'
            else:
                io_value = 'FALSE'

        # at this point, io_var and io_value must be string values
        self.addline('%s=%s' % (io_var, io_value))

    def waitDI(self, io_var, io_value, timeout_ms=-1):
        """Waits for a variable (usually a digital input) to attain a given value io_value. This
        method can also be used to set other variables.Optionally, a timeout can be provided.

        **Tip**:
        waitDI is triggered by the RoboDK instruction Program->Set or Wait I/O Instruction.

        :param io_var: variable to wait for, provided as a str or int
        :type io_var: int, str
        :param io_value: value of the variable, provided as a str, float or int
        :type io_value: int, float, str
        :param timeout_ms: maximum wait time
        :type timeout_ms: float, int
        """
        if type(io_var) != str:  # set default variable name if io_var is a number
            io_var = 'IN[%s]' % str(io_var)
        if type(io_value) != str:  # set default variable value if io_value is a number
            if io_value > 0:
                io_value = 'TRUE'
            else:
                io_value = 'FALSE'

        # at this point, io_var and io_value must be string values
        if timeout_ms < 0:
            self.addline('WAIT FOR %s==%s' % (io_var, io_value))
        else:
            self.addline('WAIT FOR %s==%s TIMEOUT=%.1f' % (io_var, io_value, timeout_ms))

    def RunCode(self, code, is_function_call=False):
        """Adds code or a function call.

        **Tip**:
        RunCode is triggered by the RoboDK instruction Program->Function call Instruction.

        :param code: code or procedure to call
        :param is_function_call: True if the provided code is a specific function to call
        :type code: str
        :type is_function_call: bool
        """
        if is_function_call:
            code.replace(' ', '_')
            if not code.endswith(')'):
                code = code + '()'
            self.addline(code)
        else:
            self.addline(code)

    def RunMessage(self, message, iscomment=False):
        """Display a message in the robot controller screen (teach pendant)

        **Tip**:
        RunMessage is triggered by the RoboDK instruction Program->Show Message Instruction.

        :param message: Message to display on the teach pendant or as a comment on the code
        :type message: str
        :param iscomment: True if the message does not have to be displayed on the teach pendant
        but as a comment on the code
        :type iscomment: bool
        """
        if iscomment:
            self.addline('% ' + message)
        else:
            # self.addlog('Show message on teach pendant not implemented (%s)' % message)
            self.addline('% Show message: ' + message)

    # ------------------ private ----------------------

    def addline(self, newline):
        """Add a new program line. This is a private method used only by the other methods.

        :param newline: new line to add.
        :type newline: str
        """
        self.PROG.append(newline)

    def addlog(self, newline):
        """Add a message to the log. This is a private method used only by the other methods. The
        log is displayed when the program is generated to show any issues when the robot program
        has been generated.

        :param newline: new line
        :type newline: str
        """
        self.LOG = self.LOG + newline + '\n'


# -------------------------------------------------
# ------------ For testing purposes ---------------
def test_post():
    """Test the post processor with a simple program"""

    from robodk.robomath import PosePP as p

    r = RobotPost()

    r.ProgStart("Program")
    r.RunMessage("Program generated by RoboDK using a custom post processor", True)
    r.setFrame(p(807.766544, -963.699898, 41.478944, 0, 0, 0))
    r.setTool(p(62.5, -108.253175, 100, -60, 90, 0))
    r.MoveJ(p(200, 200, 500, 180, 0, 180),
            [-46.18419, -6.77518, -20.54925, 71.38674, 49.58727, -302.54752])
    r.MoveL(p(200, 250, 348.734575, 180, 0, -150),
            [-41.62707, -8.89064, -30.01809, 60.62329, 49.66749, -258.98418])
    r.MoveL(p(200, 200, 262.132034, 180, 0, -150),
            [-43.73892, -3.91728, -35.77935, 58.57566, 54.11615, -253.81122])
    r.RunMessage("Setting air valve 1 on")
    r.RunCode("TCP_On", True)
    r.Pause(1000)
    r.MoveL(p(200, 250, 348.734575, 180, 0, -150),
            [-41.62707, -8.89064, -30.01809, 60.62329, 49.66749, -258.98418])
    r.MoveL(p(250, 300, 278.023897, 180, 0, -150),
            [-37.52588, -6.32628, -34.59693, 53.52525, 49.24426, -251.44677])
    r.MoveL(p(250, 250, 191.421356, 180, 0, -150),
            [-39.75778, -1.04537, -40.37883, 52.09118, 54.15317, -246.94403])
    r.RunMessage("Setting air valve off")
    r.RunCode("TCP_Off", True)
    r.Pause(1000)
    r.MoveL(p(250, 300, 278.023897, 180, 0, -150),
            [-37.52588, -6.32628, -34.59693, 53.52525, 49.24426, -251.44677])
    r.MoveL(p(250, 200, 278.023897, 180, 0, -150),
            [-41.85389, -1.95619, -34.89154, 57.43912, 52.34162, -253.73403])
    r.MoveL(p(250, 150, 191.421356, 180, 0, -150),
            [-43.82111, 3.29703, -40.29493, 56.02402, 56.61169, -249.23532])
    r.MoveJ(None, [-46.18419, -6.77518, -20.54925, 71.38674, 49.58727, -302.54752])
    r.ProgFinish("Program")
    # robot.ProgSave(".","Program",True)

    for line in r.PROG:
        print(line)

    if len(r.LOG) > 0:
        mbox('Program generation LOG:\n\n' + r.LOG)

    input("Press Enter to close...")


if __name__ == "__main__":
    """Procedure to call when the module is executed by itself: test_post()"""
    test_post()
