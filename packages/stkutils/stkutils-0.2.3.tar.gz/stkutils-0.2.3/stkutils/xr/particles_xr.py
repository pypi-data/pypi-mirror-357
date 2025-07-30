# S.T.A.L.K.E.R. particles.xr handling module
# 11/08/2013	- added firstgen chunk unpacking
# 09/08/2013	- fixed bug with unpacking build files
# 22/08/2012	- initial release
##############################################
from stkutils.binary_data import pack, unpack
from stkutils.chunked import chunked
from stkutils.data_packet import data_packet
from stkutils.ini_file import ini_file
from stkutils.perl_utils import (
    chdir,
    fail,
    join,
    length,
    mkpath,
    split,
    substr,
    universal_dict_object,
)
from stkutils.utils import get_filelist


class particles_xr:
    # use strict;
    # use data_packet;
    # use ini_file;
    # use debug qw(fail warn);
    # use utils qw(get_filelist);
    # use File::Path;

    PS_CHUNK_VERSION = 1
    PS_CHUNK_FIRSTGEN = 2
    PS_CHUNK_PARTICLES_EFFECTS = 3
    PS_CHUNK_PARTICLES_GROUPS = 4

    # def __init__():
    # 	my $class = shift;
    # 	my $self = universal_dict_object();
    # 	bless $self, $class;
    # 	return $self;
    # }
    def read(self, CDH, mode):
        # my $self = shift;
        # my () = @_;
        print("reading...\n")
        if not ((mode == "ltx") or (mode == "bin")):
            fail("unsuported mode " + mode)
        while 1:
            (index, size) = CDH.r_chunk_open()
            if not (index is not None):
                break
            # SWITCH: {
            if index == self.PS_CHUNK_VERSION:
                self.read_version(CDH)
            elif index == self.PS_CHUNK_FIRSTGEN:
                self.read_firstgen(CDH, mode)
            elif index == self.PS_CHUNK_PARTICLES_EFFECTS:
                self.read_peffects(CDH, mode)
            elif index == self.PS_CHUNK_PARTICLES_GROUPS:
                self.read_pgroups(CDH, mode)
            else:
                fail("unknown chunk index " + index)
            # }
            CDH.r_chunk_close()

        CDH.close()

    def read_version(self, CDH):

        # 	print "	version = ";
        (self.version,) = unpack("v", CDH.r_chunk_data())
        # 	print "$self.version\n";
        if self.version != 1:
            fail("unsupported version " + self.version)

    def read_firstgen(self, CDH, mode):

        rData = CDH.r_chunk_data()
        (count,) = unpack("V", substr(rData, 0, 4))
        for i in range(count):
            p = firstgen(substr(rData, 4 + 0x248 * i, 0x248))
            p.read("bin")
            self.firstgen.append(p)

    def read_peffects(self, CDH, mode):
        print("	particle effects\n")
        while 1:
            (index, size) = CDH.r_chunk_open()
            if not (index is not None):
                break
            CPEDef = particles_effect(CDH.r_chunk_data())
            CPEDef.read("bin")
            self.particles_effects.append(CPEDef)
            CDH.r_chunk_close()

    def read_pgroups(self, CDH, mode):
        print("	particle groups\n")
        while 1:
            (index, size) = CDH.r_chunk_open()
            if not (index is not None):
                break
            CPGDef = particles_group(CDH.r_chunk_data())
            CPGDef.read(mode)
            self.particles_groups.append(CPGDef)
            CDH.r_chunk_close()

    def write(self, CDH, mode):
        print("writing...\n")
        if not ((mode == "ltx") or (mode == "bin")):
            fail("unsuported mode " + mode)

        self.write_version(CDH)
        self.write_firstgen(CDH, mode)
        self.write_peffects(CDH, mode)
        self.write_pgroups(CDH, mode)

    def write_version(self, CDH):
        print("	version\n")
        CDH.w_chunk(self.PS_CHUNK_VERSION, pack("v", self.version))

    def write_firstgen(self, CDH, mode):
        if not (self.firstgen is not None):
            return
        print("	firstgen\n")
        CDH.w_chunk_open(self.PS_CHUNK_FIRSTGEN)
        CDH.w_chunk_data(pack("V", len(self.firstgen)))
        for effect in self.firstgen:
            effect.write(CDH, "bin")

        CDH.w_chunk_close()

    def write_peffects(self, CDH, mode):
        print("	particle effects\n")
        CDH.w_chunk_open(self.PS_CHUNK_PARTICLES_EFFECTS)

        for i, effect in enumerate(self.particles_effects):
            effect.write(CDH, "bin", i)

        CDH.w_chunk_close()

    def write_pgroups(self, CDH, mode):
        print("	particle groups\n")
        CDH.w_chunk_open(self.PS_CHUNK_PARTICLES_GROUPS)

        for i, group in enumerate(self.particles_groups):
            group.write(CDH, mode, i)

        CDH.w_chunk_close()

    def export(self, folder, mode):
        print("exporting...\n")
        mkpath(folder, 0)
        chdir(folder)  # or fail('cannot change dir to '+folder);

        ini = open("particles.ltx", "w", encoding="cp1251")
        ini.write("[general]\n")
        ini.write(f"version = {self.version}\n")
        ini.write("effects_count = " + ((len(self.particles_effects) - 1) + 1) + "\n")
        ini.write("groups_count = " + ((len(self.particles_groups) - 1) + 1) + "\n")
        ini.close()
        self.export_firstgen(mode)
        self.export_effects(mode)
        self.export_groups(mode)

    def export_firstgen(self, mode):

        if (len(self.firstgen) - 1) == -1:
            return
        print("	firstgen\n")
        for effect in self.firstgen:
            effect.export("bin")

    def export_effects(self, mode):

        print("	particle effects\n")
        for effect in self.particles_effects:
            effect.export("bin")

    def export_groups(self, mode):

        print("	particle groups\n")
        for group in self.particles_groups:
            group.export(mode)

    def my_import(self, folder, mode):
        print("importing...\n")
        ini = ini_file(folder + "particles.ltx", "r")
        self.version = ini.value("general", "version")
        ini.close()

        self.import_firstgen(folder, mode)
        self.import_effects(folder, mode)
        self.import_groups(folder, mode)

    def import_firstgen(self, folder, mode):
        ext = ".fg"
        if mode == "ltx":
            ext = "_firstgen.ltx"
        effects = get_filelist(folder, ext)

        if (len(effects) - 1) == -1:
            return
        print("	firstgen\n")
        for path in effects:
            effect = firstgen()
            effect._import(path, "bin")
            self.firstgen.append(effect)

    def import_effects(self, folder, mode):
        print("	particle effects\n")
        ext = ".pe"
        if mode == "ltx":
            ext = "_effect.ltx"
        effects = get_filelist(folder, ext)

        for path in effects:
            effect = particles_effect()
            effect._import(path, "bin")
            self.particles_effects.append(effect)

    def import_groups(self, folder, mode):
        print("	particle groups\n")
        ext = ".pg"
        if mode == "ltx":
            ext = "_group.ltx"
        groups = get_filelist(folder, ext)

        for path in groups:
            group = particles_group()
            group._import(path, mode)
            self.particles_groups.append(group)


#######################################################################
class firstgen:
    # use strict;
    # use debug 'fail';

    def __init__(self, data=""):
        self.service_flags = 0
        self.data = data

    def read(self, mode):
        self.read_name()

    def read_name(self):
        packet = data_packet(self.data)
        (self.m_name) = packet.unpack("Z*")

    def write(self, CDH, mode):
        # 	if (mode == 'bin'):
        CDH.w_chunk_data(self.data)

    def write_name(self, CDH):
        CDH.w_chunk_data(pack("Z*", self.m_name))

    def export(self, mode):
        path = split("\\", self.m_name)
        name = path.pop()
        path = join("\\", "firstgen", path)
        # File::Path::mkpath(path, 0);

        # 	if ($mode == 'bin') {
        fh = open(path + "\\" + name + ".fg", "wb")

        fh.write(self.data, length(self.data))
        fh.close()

    def export_name(self, ini):
        ini.write(f"name = {self.m_name}\n")

    def _import(self, path, mode):
        # 	if ($mode == 'bin') {
        self.m_name = substr(path, 0, -3)
        # self.m_name =~ s/firstgen\\//;
        fh = open(path, "rb")
        data = ""
        fh.read(data)
        self.data = data
        fh.close()

    # 	}

    def import_name(self, ini):
        self.m_name = ini.value("general", "name")


#######################################################################
class particles_effect:
    # use strict;
    # use debug 'fail';
    PED_CHUNK_VERSION = 1
    PED_CHUNK_NAME = 2
    PED_CHUNK_EFFECTDATA = 3
    PED_CHUNK_ACTIONS = 4
    PED_CHUNK_FLAGS = 5
    PED_CHUNK_FRAME = 6
    PED_CHUNK_SPRITE = 7
    PED_CHUNK_TIMELIMIT = 8
    PED_CHUNK_COLLISION = 33
    PED_CHUNK_VEL_SCALE = 34
    PED_CHUNK_DESC = 35

    PED_CHUNK_UNK = 36

    PED_CHUNK_DEF_ROTATION = 37

    PAAvoidID = 0
    PABounceID = 1
    PACallActionListID_obsolette = 2
    PACopyVertexBID = 3
    PADampingID = 4
    PAExplosionID = 5
    PAFollowID = 6
    PAGravitateID = 7
    PAGravityID = 8
    PAJetID = 9
    PAKillOldID = 0x0A
    PAMatchVelocityID = 0x0B
    PAMoveID = 0x0C
    PAOrbitLineID = 0x0D
    PAOrbitPointID = 0x0E
    PARandomAccelID = 0x0F
    PARandomDisplaceID = 0x10
    PARandomVelocityID = 0x11
    PARestoreID = 0x12
    PASinkID = 0x13
    PASinkVelocityID = 0x14
    PASourceID = 0x15
    PASpeedLimitID = 0x16
    PATargetColorID = 0x17
    PATargetSizeID = 0x18
    PATargetRotateID = 0x19
    PATargetRotateDID = 0x1A
    PATargetVelocityID = 0x1B
    PATargetVelocityDID = 0x1C
    PAVortexID = 0x1D
    PATurbulenceID = 0x1E
    PAScatterID = 0x1F
    action_enum_force_dword = 0xFFFFFFFF

    FL_SOC = 0x2

    def __init__(self, data=""):
        self.service_flags = 0
        self.data = data

    def read(self, mode):
        CDH = chunked(self.data, "data")
        while 1:
            (index, size) = CDH.r_chunk_open()
            if not (index is not None):
                break
            if (mode == "bin") and index > self.PED_CHUNK_NAME:  # break

                if index == self.PED_CHUNK_VERSION:
                    self.read_version(CDH)
                elif index == self.PED_CHUNK_NAME:
                    self.read_name(CDH)
                elif (mode == "ltx") and index == self.PED_CHUNK_EFFECTDATA:
                    self.read_effectdata(CDH)
                elif (mode == "ltx") and index == self.PED_CHUNK_ACTIONS:
                    self.read_actions(CDH)
                elif (mode == "ltx") and index == self.PED_CHUNK_FLAGS:
                    self.read_flags(CDH)
                elif (mode == "ltx") and index == self.PED_CHUNK_FRAME:
                    self.read_frame(CDH)
                elif index == self.PED_CHUNK_SPRITE:
                    self.read_sprite(CDH)
                elif (mode == "ltx") and index == self.PED_CHUNK_TIMELIMIT:
                    self.read_timelimit(CDH)
                elif (mode == "ltx") and index == self.PED_CHUNK_COLLISION:
                    self.read_collision(CDH)
                elif (mode == "ltx") and index == self.PED_CHUNK_VEL_SCALE:
                    self.read_vel_scale(CDH)
                elif (mode == "ltx") and index == self.PED_CHUNK_DESC:
                    self.read_description(CDH)
                elif (mode == "ltx") and index == self.PED_CHUNK_DEF_ROTATION:
                    self.read_def_rotation(CDH)
                elif mode == "ltx":
                    fail("unknown chunk index " + index)

            CDH.r_chunk_close()

        CDH.close()

    def read_version(self, CDH):

        (self.version,) = unpack("v", CDH.r_chunk_data())
        if self.version != 1:
            fail("unsupported version " + self.version)

    def read_name(self, CDH):

        packet = data_packet(CDH.r_chunk_data())
        (self.m_name) = packet.unpack("Z*")
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_effectdata(self, CDH):
        packet = data_packet(CDH.r_chunk_data())
        (self.m_MaxParticles) = packet.unpack("V")
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_actions(self, CDH):
        packet = data_packet(CDH.r_chunk_data())
        (count) = packet.unpack("V", 4)
        for i in range(count):
            (type) = packet.unpack("V", 4)
            action = universal_dict_object()
            # SWITCH: {
            # 			$type == PAAvoidID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PABounceID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PACallActionListID_obsolette : $action = pa_avoid(); $action.load($packet);
            # 			$type == PACopyVertexBID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PADampingID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PAExplosionID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PAFollowID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PAGravitateID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PAGravityID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PAJetID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PAKillOldID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PAMatchVelocityID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PAMoveID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PAOrbitLineID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PAOrbitPointID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PARandomAccelID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PARandomDisplaceID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PARandomVelocityID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PARestoreID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PASinkID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PASinkVelocityID : $action = pa_avoid(); $action.load($packet);
            if type == self.PASourceID:
                action = pa_source()
                action.read(packet)
            # 			$type == PASpeedLimitID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PATargetColorID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PATargetSizeID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PATargetRotateID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PATargetRotateDID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PATargetVelocityID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PATargetVelocityDID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PAVortexID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PATurbulenceID : $action = pa_avoid(); $action.load($packet);
            # 			$type == PAScatterID : $action = pa_avoid(); $action.load($packet);
            else:
                fail("unknown type " + type)
            # }
            self.m_Actions.append(action)

        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_flags(self, CDH):
        packet = data_packet(CDH.r_chunk_data())
        (self.m_Flags) = packet.unpack("V")
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_frame(self, CDH):
        packet = data_packet(CDH.r_chunk_data())
        self.m_fTexSize = packet.unpack("f2", 8)
        self.reserved = packet.unpack("f2", 8)
        (self.m_iFrameDimX, self.m_iFrameCount, self.m_fSpeed) = packet.unpack(
            "VVf",
            12,
        )
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_sprite(self, CDH):
        packet = data_packet(CDH.r_chunk_data())
        (self.m_ShaderName, self.m_TextureName) = packet.unpack("Z*Z*")
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_timelimit(self, CDH):
        packet = data_packet(CDH.r_chunk_data())
        (self.m_fTimeLimit) = packet.unpack("f")
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_collision(self, CDH):
        packet = data_packet(CDH.r_chunk_data())
        (
            self.m_fCollideOneMinusFriction,
            self.m_fCollideResilience,
            self.m_fCollideSqrCutoff,
        ) = packet.unpack("fff")
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_vel_scale(self, CDH):
        packet = data_packet(CDH.r_chunk_data())
        self.m_VelocityScale = packet.unpack("f3")
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_description(self, CDH):
        self.service_flags |= self.FL_SOC
        packet = data_packet(CDH.r_chunk_data())
        (self.m_Creator, self.m_Editor, self.m_CreateTime, self.m_EditTime) = (
            packet.unpack("Z*Z*VV")
        )
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_def_rotation(self, CDH):
        packet = data_packet(CDH.r_chunk_data())
        self.m_APDefaultRotation = packet.unpack("f3")
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def write(self, CDH, mode, index):
        if mode == "bin":
            CDH.w_chunk(index, self.data)
        elif mode == "ltx":
            CDH.w_chunk_open(index)
            self.write_version(CDH)
            self.write_name(CDH)
            self.write_effectdata(CDH)
            self.write_actions(CDH)
            self.write_flags(CDH)
            if (self.m_Flags & 0x1) == 0x1:
                self.write_sprite(CDH)
            if (self.m_Flags & 0x400) == 0x400:
                self.write_frame(CDH)
            if (self.m_Flags & 0x4000) == 0x4000:
                self.write_timelimit(CDH)
            if (self.m_Flags & 0x10000) == 0x10000:
                self.write_collision(CDH)
            if (self.m_Flags & 0x40000) == 0x40000:
                self.write_vel_scale(CDH)
            if (self.m_Flags & 0x8000) == 0x8000:
                self.write_def_rotation(CDH)
            if (self.service_flags & self.FL_SOC) == self.FL_SOC:
                self.write_description(CDH)
            CDH.w_chunk_close()

    def export(self, mode):

        path = split("\\", self.m_name)
        path.pop()
        path = join("\\", path)
        mkpath(path, 0)

        if mode == "bin":
            # 		print "$self.m_name\n";
            fh = open(self.m_name + ".pe", "wb")
            if not (fh is not None):
                return

            fh.write(self.data, length(self.data))
            fh.close()
        elif mode == "ltx":
            fh = open(self.m_name + "_effect.ltx", "w", encoding="cp1251")
            fh.write("[general]\n")
            self.export_version(fh)
            self.export_name(fh)
            self.export_effectdata(fh)
            self.export_actions(fh)
            self.export_flags(fh)
            if (self.m_Flags & 0x1) == 0x1:
                self.export_sprite(fh)
            if (self.m_Flags & 0x400) == 0x400:
                self.export_frame(fh)
            if (self.m_Flags & 0x4000) == 0x4000:
                self.export_timelimit(fh)
            if (self.m_Flags & 0x10000) == 0x10000:
                self.export_collision(fh)
            if (self.m_Flags & 0x40000) == 0x40000:
                self.export_vel_scale(fh)
            if (self.m_Flags & 0x8000) == 0x8000:
                self.export_def_rotation(fh)
            if (self.service_flags & self.FL_SOC) == self.FL_SOC:
                self.export_description(fh)
            fh.close()

    def _import(self, path, mode):
        if mode == "bin":
            self.m_name = substr(path, 0, -3)
            fh = open(path, "rb")
            data = ""
            fh.read(data)
            self.data = data
            fh.close()
        elif mode == "ltx":
            fh = ini_file(path, "r")
            self.import_version(fh)
            self.import_name(fh)
            self.import_effectdata(fh)
            self.import_actions(fh)
            self.import_flags(fh)
            if (self.m_Flags & 0x1) == 0x1:
                self.import_sprite(fh)
            if (self.m_Flags & 0x400) == 0x400:
                self.import_frame(fh)
            if (self.m_Flags & 0x4000) == 0x4000:
                self.import_timelimit(fh)
            if (self.m_Flags & 0x10000) == 0x10000:
                self.import_collision(fh)
            if (self.m_Flags & 0x40000) == 0x40000:
                self.import_vel_scale(fh)
            if (self.m_Flags & 0x8000) == 0x8000:
                self.import_def_rotation(fh)
            if (self.service_flags & self.FL_SOC) == self.FL_SOC:
                self.import_description(fh)
            fh.close()


#######################################################################
class particles_group:
    # use strict;
    # use debug 'fail';

    PGD_CHUNK_VERSION = 1
    PGD_CHUNK_NAME = 2
    PGD_CHUNK_FLAGS = 3
    PGD_CHUNK_EFFECTS = 4
    PGD_CHUNK_TIMELIMIT = 5
    PGD_CHUNK_DESC = 6
    PGD_CHUNK_EFFECTS2 = 7

    FL_OLD = 0x1
    FL_SOC = 0x2

    def __init__(self, data=""):
        self.service_flags = 0
        self.data = data

    def read(self, mode):
        CDH = chunked(self.data, "data")
        while 1:
            (index, size) = CDH.r_chunk_open()
            if not (index is not None):
                break
            # if ((mode == 'bin') and index > PGD_CHUNK_NAME): 		break
            # SWITCH: {
            if index == self.PGD_CHUNK_VERSION:
                self.read_version(CDH)
            elif index == self.PGD_CHUNK_NAME:
                self.read_name(CDH)
            elif (mode == "ltx") and index == self.PGD_CHUNK_FLAGS:
                self.read_flags(CDH)
            elif (mode == "ltx") and index == self.PGD_CHUNK_EFFECTS:
                self.read_effects(CDH)
            elif (mode == "ltx") and index == self.PGD_CHUNK_TIMELIMIT:
                self.read_timelimit(CDH)
            elif (mode == "ltx") and index == self.PGD_CHUNK_DESC:
                self.read_description(CDH)
            elif (mode == "ltx") and index == self.PGD_CHUNK_EFFECTS2:
                self.read_effects2(CDH)
            elif mode == "ltx":
                fail("unknown chunk index " + index)
            # }
            CDH.r_chunk_close()

        CDH.close()

    def read_version(self, CDH):

        (self.version,) = unpack("v", CDH.r_chunk_data())
        if self.version != 3:
            fail("unsupported version " + self.version)

    def read_name(self, CDH):

        packet = data_packet(CDH.r_chunk_data())
        (self.m_name) = packet.unpack("Z*")
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_flags(self, CDH):

        packet = data_packet(CDH.r_chunk_data())
        (self.m_flags) = packet.unpack("V", 4)
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_effects(self, CDH):
        packet = data_packet(CDH.r_chunk_data())
        (count) = packet.unpack("V", 4)
        for i in range(count):
            effect = universal_dict_object()
            (
                effect.m_EffectName,
                effect.m_OnPlayChildName,
                effect.m_OnBirthChildName,
                effect.m_OnDeadChildName,
                effect.m_Time0,
                effect.m_Time1,
                effect.m_Flags,
            ) = packet.unpack("Z*Z*Z*Z*ffV")
            self.effects.append(effect)

        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_effects2(self, CDH):
        packet = data_packet(CDH.r_chunk_data())
        self.service_flags |= self.FL_OLD
        (count) = packet.unpack("V", 4)
        for i in range(count):
            effect = universal_dict_object()
            (
                effect.m_EffectName,
                effect.m_OnPlayChildName,
                effect.m_Time0,
                effect.m_Time1,
                effect.m_Flags,
            ) = packet.unpack("Z*Z*ffV")
            self.effects.append(effect)

        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_timelimit(self, CDH):
        packet = data_packet(CDH.r_chunk_data())
        (self.m_fTimeLimit) = packet.unpack("f", 4)
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def read_description(self, CDH):
        self.service_flags |= self.FL_SOC
        packet = data_packet(CDH.r_chunk_data())
        (self.m_Creator, self.m_Editor, self.m_CreateTime, self.m_EditTime) = (
            packet.unpack("Z*Z*VV")
        )
        if packet.resid() != 0:
            fail("data left in packet: " + packet.resid())

    def write(self, CDH, mode, index):
        if mode == "bin":
            CDH.w_chunk(index, self.data)
        elif mode == "ltx":
            CDH.w_chunk_open(index)
            self.write_version(CDH)
            self.write_name(CDH)
            self.write_flags(CDH)
            if (self.service_flags & self.FL_OLD) == 0:
                self.write_effects(CDH)
            else:
                self.write_effects2(CDH)

            self.write_timelimit(CDH)
            if (self.service_flags & self.FL_SOC) != 0:
                self.write_description(CDH)
            CDH.w_chunk_close()

    def write_version(self, CDH):
        CDH.w_chunk(self.PGD_CHUNK_VERSION, pack("v", self.version))

    def write_name(self, CDH):
        CDH.w_chunk(self.PGD_CHUNK_NAME, pack("Z*", self.m_name))

    def write_flags(self, CDH):
        CDH.w_chunk(self.PGD_CHUNK_FLAGS, pack("V", self.m_flags))

    def write_timelimit(self, CDH):
        CDH.w_chunk(self.PGD_CHUNK_TIMELIMIT, pack("f", self.m_fTimeLimit))

    def write_effects(self, CDH):
        CDH.w_chunk_open(self.PGD_CHUNK_EFFECTS)
        CDH.w_chunk_data(pack("V", (len(self.effects) - 1) + 1))
        for effect in self.effects:
            CDH.w_chunk_data(
                pack(
                    "Z*Z*Z*Z*ffV",
                    effect.m_EffectName,
                    effect.m_OnPlayChildName,
                    effect.m_OnBirthChildName,
                    effect.m_OnDeadChildName,
                    effect.m_Time0,
                    effect.m_Time1,
                    effect.m_Flags,
                ),
            )

        CDH.w_chunk_close()

    def write_effects2(self, CDH):
        CDH.w_chunk_open(self.PGD_CHUNK_EFFECTS2)
        CDH.w_chunk_data(pack("V", (len(self.effects) - 1) + 1))
        for effect in self.effects:
            CDH.w_chunk_data(
                pack(
                    "Z*Z*ffV",
                    effect.m_EffectName,
                    effect.m_OnPlayChildName,
                    effect.m_Time0,
                    effect.m_Time1,
                    effect.m_Flags,
                ),
            )

        CDH.w_chunk_close()

    def write_description(self, CDH):
        CDH.w_chunk(
            self.PGD_CHUNK_DESC,
            pack(
                "Z*Z*VV",
                self.m_Creator,
                self.m_Editor,
                self.m_CreateTime,
                self.m_EditTime,
            ),
        )

    def export(self, mode):

        path = split("\\", self.m_name)
        path.pop()
        path = join("\\", path)
        mkpath(path, 0)

        if mode == "bin":
            fh = open(self.m_name + ".pg", "wb")
            fh.write(self.data, length(self.data))
            fh.close()
        elif mode == "ltx":
            fh = open(self.m_name + "_group.ltx", "w", encoding="cp1251")
            fh.write("[general]\n")
            self.export_version(fh)
            fh.write(f"service_flags = {self.service_flags}\n")
            self.export_name(fh)
            self.export_flags(fh)
            self.export_timelimit(fh)
            if (self.service_flags & self.FL_SOC) != 0:
                self.export_description(fh)
            fh.write("\n[effects]\n")
            self.export_effects(fh)
            fh.close()

    def export_version(self, ini):
        ini.write(f"version = {self.version}\n")

    def export_name(self, ini):
        ini.write(f"name = {self.m_name}\n")

    def export_flags(self, ini):
        ini.write(f"flags = {self.m_flags}\n")

    def export_effects(self, ini):

        ini.write("effects_count = " + ((len(self.effects) - 1) + 1) + "\n")
        for i, effect in enumerate(self.effects):
            ini.write(f"{i}:effect_name = {effect.m_EffectName}\n")
            ini.write(f"{i}:on_play = {effect.m_OnPlayChildName}\n")
            if (self.service_flags & self.FL_OLD) == 0:
                ini.write(f"{i}:on_birth = {effect.m_OnBirthChildName}\n")
            if (self.service_flags & self.FL_OLD) == 0:
                ini.write(f"{i}:on_dead = {effect.m_OnDeadChildName}\n")
            ini.write(f"{i}:begin_time = {effect.m_Time0}\n")
            ini.write(f"{i}:end_time = {effect.m_Time1}\n")
            ini.write(f"{i}:flags = {effect.m_Flags}\n\n")

    def export_timelimit(self, ini):
        ini.write(f"timelimit = {self.m_fTimeLimit}\n")

    def export_description(self, ini):
        ini.write(f"creator = {self.m_Creator}\n")
        ini.write(f"editor = {self.m_Editor}\n")
        ini.write(f"create_time = {self.m_CreateTime}\n")
        ini.write(f"edit_time = {self.m_EditTime}\n")

    def _import(self, path, mode):
        if mode == "bin":
            self.m_name = substr(path, 0, -3)
            fh = open(path, "rb")
            data = ""
            fh.read(data)
            self.data = data
            fh.close()
        elif mode == "ltx":
            fh = ini_file(path, "r")
            self.import_version(fh)
            self.import_name(fh)
            self.import_flags(fh)
            self.service_flags = fh.value("general", "service_flags")
            self.import_timelimit(fh)
            if (self.service_flags & self.FL_SOC) != 0:
                self.import_description(fh)
            self.import_effects(fh)
            fh.close()

    def import_version(self, ini):
        self.version = ini.value("general", "version")

    def import_name(self, ini):
        self.m_name = ini.value("general", "name")

    def import_flags(self, ini):
        self.m_flags = ini.value("general", "flags")

    def import_timelimit(self, ini):
        self.m_fTimeLimit = ini.value("general", "timelimit")

    def import_description(self, ini):

        self.m_Creator = ini.value("general", "creator")
        self.m_Editor = ini.value("general", "editor")
        self.m_CreateTime = ini.value("general", "create_time")
        self.m_EditTime = ini.value("general", "edit_time")

    def import_effects(self, ini):
        count = ini.value("effects", "effects_count")
        for i in range(count):
            effect = universal_dict_object()
            effect.m_EffectName = ini.value("effects", f"{i}:effect_name")
            effect.m_OnPlayChildName = ini.value("effects", f"{i}:on_play")
            effect.m_OnBirthChildName = ini.value("effects", f"{i}:on_birth")
            effect.m_OnDeadChildName = ini.value("effects", f"{i}:on_dead")
            effect.m_Time0 = ini.value("effects", f"{i}:begin_time")
            effect.m_Time1 = ini.value("effects", f"{i}:end_time")
            effect.m_Flags = ini.value("effects", f"{i}:flags")
            self.effects.append(effect)


#######################################################################
class pa_source:
    # use strict;

    def read(self, packet):
        (self.m_Flags, self.type) = packet.unpack("VV", 8)
        self.position = packet.unpack("Vf16", 68)
        self.velocity = packet.unpack("Vf16", 68)
        self.rot = packet.unpack("Vf16", 68)
        self.size = packet.unpack("Vf16", 68)
        self.color = packet.unpack("Vf16", 68)
        (self.alpha, self.particle_rate, self.age, self.age_sigma) = packet.unpack(
            "ffff",
            16,
        )
        self.parent_vel = packet.unpack("f3", 12)
        (self.parent_motion) = packet.unpack("f", 4)


##############################
