# S.T.A.L.K.E.R. gamemtl.xr handling module
# Update history:
# 	30/08/2012 - initial release
##############################################
import os

from stkutils.binary_data import pack, unpack
from stkutils.ini_file import ini_file
from stkutils.perl_utils import defstr, fail, join, split, universal_dict_object
from stkutils.utils import get_filelist


class gamemtl_xr:
    # use strict;
    # use stkutils::data_packet;
    # use stkutils::ini_file;
    # use stkutils::debug qw(fail warn);
    # use stkutils::utils qw(get_filelist);
    # use File::Path;

    GAMEMTLS_CHUNK_VERSION: 0x1000
    GAMEMTLS_CHUNK_AUTOINC: 0x1001
    GAMEMTLS_CHUNK_MATERIALS: 0x1002
    GAMEMTLS_CHUNK_MATERIAL_PAIRS: 0x1003

    # def new {
    # 	my $class = shift;
    # 	my $self = universal_dict_object();
    # 	bless $self, $class;
    # 	return $self;
    # }
    def read(self, CDH):
        print("reading...\n")
        while 1:
            (index, size) = CDH.r_chunk_open()
            if not index is not None:
                break
            # SWITCH: {
            if index == self.GAMEMTLS_CHUNK_VERSION:
                self.read_version(CDH)
            elif index == self.GAMEMTLS_CHUNK_AUTOINC:
                self.read_autoinc(CDH)
            elif index == self.GAMEMTLS_CHUNK_MATERIALS:
                self.read_materials(CDH)
            elif index == self.GAMEMTLS_CHUNK_MATERIAL_PAIRS:
                self.read_material_pairs(CDH)
            else:
                fail("unknown chunk index " + index)
            # }
            CDH.r_chunk_close()

        CDH.close()

    def read_version(self, CDH):

        print("	version\n")
        self.version = unpack("v", CDH.r_chunk_data())
        if self.version != 1:
            fail("unsupported version " + self.version)

    def read_autoinc(self, CDH):
        # my $self = shift;
        # my ($) = @_;
        print("	autoinc\n")
        (self.material_index, self.material_pair_index) = unpack(
            "VV",
            CDH.r_chunk_data(),
        )

    def read_materials(self, CDH):
        print("	materials\n")
        while 1:
            (index, size) = CDH.r_chunk_open()
            if not index is not None:
                break
            mat = material()
            mat.read(CDH)
            self.materials.append(mat)
            CDH.r_chunk_close()

    def read_material_pairs(self, CDH):

        print("	material pairs\n")
        while 1:
            (index, size) = CDH.r_chunk_open()
            if not index is not None:
                break
            mat_p = material_pairs()
            mat_p.read(CDH)
            self.material_pairs.append(mat_p)
            CDH.r_chunk_close()

    def write(self, CDH):
        print("writing...\n")

        self.defst_mat_names()
        self.write_version(CDH)
        self.write_autoinc(CDH)
        self.write_materials(CDH)
        self.write_material_pairs(CDH)

    def write_version(self, CDH):
        print("	version\n")
        CDH.w_chunk(self.GAMEMTLS_CHUNK_VERSION, pack("v", self.version))

    def write_autoinc(self, CDH):

        print("	autoinc\n")
        CDH.w_chunk(
            self.GAMEMTLS_CHUNK_AUTOINC,
            pack("VV", self.material_index, self.material_pair_index),
        )

    def write_materials(self, CDH):
        # my $self = shift;
        # my ($) = @_;
        print("	materials\n")
        CDH.w_chunk_open(self.GAMEMTLS_CHUNK_MATERIALS)

        for i, mat in enumerate(self.materials):
            mat.write(CDH, i)

        CDH.w_chunk_close()

    def write_material_pairs(self, CDH):

        print("	material pairs\n")
        CDH.w_chunk_open(self.GAMEMTLS_CHUNK_MATERIAL_PAIRS)

        for i, mat_p in enumerate(self.material_pairs):
            mat_p.write(CDH, i)

        CDH.w_chunk_close()

    def export(self, folder):
        print("exporting...\n")
        os.path.mkdir(folder, 0)
        # chdir $folder# or fail('cannot change dir to '.$folder);

        ini = open("game_materials.ltx", "w")  # or fail("game_materials.ltx: $!\n");
        ini.write("[general]\n")
        ini.write(f"version = {self.version}\n")
        ini.write(f"material_index = {self.material_index}\n")
        ini.write(f"material_pair_index = {self.material_pair_index}\n")
        ini.close()

        self.defst_mat_ids()
        self.export_materials()
        self.export_material_pairs()

    def export_materials(self):
        # my $self = shift;
        print("	materials\n")
        for mat in self.materials:
            mat.export()

    def export_material_pairs(self):
        print("	material pairs\n")
        for mat_p in self.material_pairs:
            mat_p.export()

    def my_import(self, folder):
        print("importing...\n")
        ini = ini_file(
            folder + "game_materials.ltx",
            "r",
        )  # or fail("game_materials.ltx: $!\n");
        self.version = ini.value("general", "version")
        self.material_index = ini.value("general", "material_index")
        self.material_pair_index = ini.value("general", "material_pair_index")
        ini.close()

        self.import_materials(folder)
        self.import_material_pairs(folder)

    def import_materials(self, folder):
        print("	materials\n")
        mats = get_filelist(folder + r"\MATERIALS", "ltx")

        for path in mats:
            mat = material()
            mat._import(path)
            self.materials.append(mat)

    def import_material_pairs(self, folder, mode):
        print("	material pairs\n")
        mat_ps = get_filelist(folder + r"\MATERIAL_PAIRS", "ltx")

        for path in mat_ps:
            mat_p = material_pairs()
            mat_p._import(path)
            self.material_pairs.append(mat_p)

    def defst_mat_ids(self):

        mtl_by_id = universal_dict_object()
        for mat in self.materials:
            mtl_by_id[mat.ID] = mat.m_Name

        for mat_p in self.material_pairs:
            mat_p.mtl0 = mtl_by_id[mat_p.mtl0]
            mat_p.mtl1 = mtl_by_id[mat_p.mtl1]

    def defst_mat_names(self):
        mtl_by_name = universal_dict_object()
        for mat in self.materials:
            mtl_by_name[mat.m_Name] = mat.ID

        for mat_p in self.material_pairs:
            mat_p.mtl0 = mtl_by_name[mat_p.mtl0]
            mat_p.mtl1 = mtl_by_name[mat_p.mtl1]


#######################################################################
class material:
    # use strict;
    # use stkutils::debug qw(fail);

    GAMEMTL_CHUNK_MAIN: 0x1000
    GAMEMTL_CHUNK_FLAGS: 0x1001
    GAMEMTL_CHUNK_PHYSICS: 0x1002
    GAMEMTL_CHUNK_FACTORS: 0x1003
    GAMEMTL_CHUNK_FLOTATION: 0x1004
    GAMEMTL_CHUNK_DESC: 0x1005
    GAMEMTL_CHUNK_INJURY: 0x1006
    GAMEMTL_CHUNK_DENSITY: 0x1007
    GAMEMTL_CHUNK_SHOOTING: 0x1008

    mflags: (
        {"name": "MF_BREAKABLE", "value": 0x1},
        {"name": "MF_UNK_0x2", "value": 0x2},
        {"name": "MF_BOUNCEABLE", "value": 0x4},
        {"name": "MF_SKIDMARK", "value": 0x8},
        {"name": "MF_BLOODMARK", "value": 0x10},
        {"name": "MF_CLIMABLE", "value": 0x20},
        {"name": "MF_UNK_0x40", "value": 0x40},
        {"name": "MF_PASSABLE", "value": 0x80},
        {"name": "MF_DYNAMIC", "value": 0x100},
        {"name": "MF_LIQUID", "value": 0x200},
        {"name": "MF_SUPPRESS_SHADOW", "value": 0x400},
        {"name": "MF_SUPPRESS_WALLMARKS", "value": 0x800},
        {"name": "MF_ACTOR_OBSTACLE", "value": 0x1000},
        {"name": "MF_BULLET_NO_RICOSHET", "value": 0x2000},
        {"name": "MF_INJURIOUS", "value": 0x10000000},
        {"name": "MF_SHOOTABLE", "value": 0x20000000},
        {"name": "MF_TRANSPARENT", "value": 0x40000000},
        {"name": "MF_SLOW_DOWN", "value": 0x80000000},
    )

    def __init__(self, data=""):
        self.service_flags = 0
        self.data = data

    def read(self, CDH):
        while 1:
            (index, size) = CDH.r_chunk_open()
            if not index is not None:
                break
            # SWITCH: {
            if index == self.GAMEMTL_CHUNK_MAIN:
                (self.ID, self.m_Name) = unpack("VZ*", CDH.r_chunk_data())
            elif index == self.GAMEMTL_CHUNK_FLAGS:
                self.m_Flags = unpack("V", CDH.r_chunk_data())
            elif index == self.GAMEMTL_CHUNK_PHYSICS:
                (
                    self.fPHFriction,
                    self.fPHDamping,
                    self.fPHSpring,
                    self.fPHBounceStartVelocity,
                    self.fPHBouncing,
                ) = unpack("f5", CDH.r_chunk_data())
            elif index == self.GAMEMTL_CHUNK_FACTORS:
                (
                    self.fShootFactor,
                    self.fBounceDamageFactor,
                    self.fVisTransparencyFactor,
                    self.fSndOcclusionFactor,
                ) = unpack("f4", CDH.r_chunk_data())
            elif index == self.GAMEMTL_CHUNK_FLOTATION:
                self.fFlotationFactor = unpack("f", CDH.r_chunk_data())
            elif index == self.GAMEMTL_CHUNK_DESC:
                self.m_Desc = unpack("Z*", CDH.r_chunk_data())
            elif index == self.GAMEMTL_CHUNK_INJURY:
                (self.fInjuriousSpeed,) = unpack("f", CDH.r_chunk_data())
            elif index == self.GAMEMTL_CHUNK_DENSITY:
                (self.fDensityFactor,) = unpack("f", CDH.r_chunk_data())
            elif index == self.GAMEMTL_CHUNK_SHOOTING:
                (self.fShootingMP,) = unpack("f", CDH.r_chunk_data())
            else:
                fail("unknown chunk index " + index)
            # }
            CDH.r_chunk_close()

    def write(self, CDH, index):
        CDH.w_chunk_open(index)
        CDH.w_chunk(self.GAMEMTL_CHUNK_MAIN, pack("VZ*", self.ID, self.m_Name))
        if self.m_Desc is not None:
            CDH.w_chunk(self.GAMEMTL_CHUNK_DESC, pack("Z*", self.m_Desc))
        CDH.w_chunk(self.GAMEMTL_CHUNK_FLAGS, pack("V", self.m_Flags))
        CDH.w_chunk(
            self.GAMEMTL_CHUNK_PHYSICS,
            pack(
                "f5",
                self.fPHFriction,
                self.fPHDamping,
                self.fPHSpring,
                self.fPHBounceStartVelocity,
                self.fPHBouncing,
            ),
        )
        CDH.w_chunk(
            self.GAMEMTL_CHUNK_FACTORS,
            pack(
                "f4",
                self.fShootFactor,
                self.fBounceDamageFactor,
                self.fVisTransparencyFactor,
                self.fSndOcclusionFactor,
            ),
        )

        if self.fShootingMP is not None:
            CDH.w_chunk(self.GAMEMTL_CHUNK_SHOOTING, pack("f", self.fShootingMP))
        if self.fFlotationFactor is not None:
            CDH.w_chunk(self.GAMEMTL_CHUNK_FLOTATION, pack("f", self.fFlotationFactor))
        if self.fInjuriousSpeed is not None:
            CDH.w_chunk(self.GAMEMTL_CHUNK_INJURY, pack("f", self.fInjuriousSpeed))
        if self.fDensityFactor is not None:
            CDH.w_chunk(self.GAMEMTL_CHUNK_DENSITY, pack("f", self.fDensityFactor))
        CDH.w_chunk_close()

    def export(self):

        os.path.mkdir("MATERIALS", 0)
        path = split("\\", self.m_Name)
        path.pop()
        path = join("\\", path)
        if path and path != "":
            os.path.mkdir("MATERIALS\\" + path, 0)

        fn = "MATERIALS\\" + self.m_Name + ".ltx"
        bin_fh = open(fn, "w", encoding="cp1251")  # or fail("$fn: $!\n");
        bin_fh.write("[general]\n")
        bin_fh.write(f"id = {self.ID}\n")
        bin_fh.write(f"name = {self.m_Name}\n")
        bin_fh.write(f"description = {self.m_Desc}\n")  # added in build 1623
        bin_fh.write("\n[flags]\n")
        self.set_flags()
        bin_fh.write(f"flags = {self.m_Flags}\n")
        bin_fh.write("\n[physics]\n")
        bin_fh.write("fPHFriction = %.5g\n" % self.fPHFriction)
        bin_fh.write("fPHDamping = %.5g\n" % self.fPHDamping)
        bin_fh.write("fPHSpring = %.5g\n" % self.fPHSpring)
        bin_fh.write("fPHBounceStartVelocity = %.5g\n" % self.fPHBounceStartVelocity)
        bin_fh.write("fPHBouncing = %.5g\n" % self.fPHBouncing)
        bin_fh.write("\n[factors]\n")
        bin_fh.write("fShootFactor = %.5g\n" % self.fShootFactor)
        bin_fh.write("fBounceDamageFactor = %.5g\n" % self.fBounceDamageFactor)
        bin_fh.write("fVisTransparencyFactor = %.5g\n" % self.fVisTransparencyFactor)
        bin_fh.write("fSndOcclusionFactor = %.5g\n" % self.fSndOcclusionFactor)
        if self.fShootingMP is not None:
            bin_fh.write(
                "fShootingMP = %.5g\n" % self.fShootingMP,
            )  # added in Call Of Pripyat
        if self.fFlotationFactor is not None:
            bin_fh.write(
                "fFlotationFactor = %.5g\n" % self.fFlotationFactor,
            )  # added in build 1623
        if self.fInjuriousSpeed is not None:
            bin_fh.write(
                "fInjuriousSpeed = %.5g\n" % self.fInjuriousSpeed,
            )  # added in build 2205
        if self.fDensityFactor is not None:
            bin_fh.write(
                "fDensityFactor = %.5g\n\n" % self.fDensityFactor,
            )  # added in Clear Sky
        bin_fh.close()

    def _import(self, src):

        cf = ini_file(src, "r")  # or fail("$src: $!\n");
        self.ID = cf.value("general", "id")
        self.m_Name = cf.value("general", "name")
        self.m_Desc = cf.value("general", "description")
        self.m_Flags = cf.value("flags", "flags")
        self.get_flags()
        self.fPHFriction = cf.value("physics", "fPHFriction")
        self.fPHDamping = cf.value("physics", "fPHDamping")
        self.fPHSpring = cf.value("physics", "fPHSpring")
        self.fPHBounceStartVelocity = cf.value("physics", "fPHBounceStartVelocity")
        self.fPHBouncing = cf.value("physics", "fPHBouncing")
        self.fShootFactor = cf.value("factors", "fShootFactor")
        self.fBounceDamageFactor = cf.value("factors", "fBounceDamageFactor")
        self.fVisTransparencyFactor = cf.value("factors", "fVisTransparencyFactor")
        self.fSndOcclusionFactor = cf.value("factors", "fSndOcclusionFactor")
        self.fShootingMP = cf.value("factors", "fShootingMP")
        self.fFlotationFactor = cf.value("factors", "fFlotationFactor")
        self.fInjuriousSpeed = cf.value("factors", "fInjuriousSpeed")
        self.fDensityFactor = cf.value("factors", "fDensityFactor")
        cf.close()

    def get_flags(self):
        temp = split(r",\s*", self.m_Flags)
        ftemp = 0
        for fl in temp:
            for k in self.mflags:
                if k.name == fl:
                    ftemp += k.value

        self.m_Flags = ftemp

    def set_flags(self):
        temp = ""
        for k in self.mflags:
            if (self.m_Flags & k.value) == k.value:
                temp += k.name
                temp += ","
                self.m_Flags -= k.value

        if self.m_Flags != 0:
            print("%#x\n" % self.m_Flags)
            fail("some flags left\n")
        self.m_Flags = defstr(temp, 0, -1)


#######################################################################
class material_pairs:
    # use strict;
    # use stkutils::debug qw(fail);

    GAMEMTLPAIR_CHUNK_PAIR = 0x1000
    GAMEMTLPAIR_CHUNK_1616_1 = 0x1001
    GAMEMTLPAIR_CHUNK_BREAKING = 0x1002
    GAMEMTLPAIR_CHUNK_STEP = 0x1003
    GAMEMTLPAIR_CHUNK_1616_2 = 0x1004
    GAMEMTLPAIR_CHUNK_COLLIDE = 0x1005

    mflags = (
        {"name": "MPF_BREAKING_SOUNDS", "value": 0x2},
        {"name": "MPF_STEP_SOUNDS", "value": 0x4},
        {"name": "MPF_COLLIDE_SOUNDS", "value": 0x10},
        {"name": "MPF_COLLIDE_PARTICLES", "value": 0x20},
        {"name": "MPF_COLLIDE_MARKS", "value": 0x40},
    )

    def __init__(self, data=""):
        self.data = data

    # 	my $class = shift;
    # 	my $self = universal_dict_object();
    # 	$self.data = '';
    # 	$self.data = $_[0] if $#_ == 0;
    # 	bless $self, $class;
    # 	return $self;
    # }
    def read(self, CDH):

        while 1:
            (index, size) = CDH.r_chunk_open()
            if not index is not None:
                break

            if index == self.GAMEMTLPAIR_CHUNK_PAIR:
                (self.mtl0, self.mtl1, self.ID, self.ID_parent, self.OwnProps) = unpack(
                    "V5",
                    CDH.r_chunk_data(),
                )
            elif index == self.GAMEMTLPAIR_CHUNK_1616_1:
                (self.unk_1,) = unpack("V", CDH.r_chunk_data())
            elif index == self.GAMEMTLPAIR_CHUNK_BREAKING:
                (self.BreakingSounds,) = unpack("Z*", CDH.r_chunk_data())
            elif index == self.GAMEMTLPAIR_CHUNK_STEP:
                (self.StepSounds,) = unpack("Z*", CDH.r_chunk_data())
            elif index == self.GAMEMTLPAIR_CHUNK_1616_2:
                (self.unk_2,) = unpack("Z*", CDH.r_chunk_data())
            elif index == self.GAMEMTLPAIR_CHUNK_COLLIDE:
                (self.CollideSounds, self.CollideParticles, self.CollideMarks) = unpack(
                    "Z*Z*Z*",
                    CDH.r_chunk_data(),
                )
            else:
                fail("unknown chunk index " + index)

            CDH.r_chunk_close()

    def write(self, CDH, index):

        CDH.w_chunk_open(index)
        CDH.w_chunk(
            self.GAMEMTLPAIR_CHUNK_PAIR,
            pack("V5", self.mtl0, self.mtl1, self.ID, self.ID_parent, self.OwnProps),
        )
        if self is not None.unk_1:
            CDH.w_chunk(self.GAMEMTLPAIR_CHUNK_1616_1, pack("V", self.unk_1))
        CDH.w_chunk(self.GAMEMTLPAIR_CHUNK_BREAKING, pack("Z*", self.BreakingSounds))
        CDH.w_chunk(self.GAMEMTLPAIR_CHUNK_STEP, pack("Z*", self.StepSounds))
        if self is not None.unk_2:
            CDH.w_chunk(self.GAMEMTLPAIR_CHUNK_1616_2, pack("Z*", self.unk_2))
        CDH.w_chunk(
            self.GAMEMTLPAIR_CHUNK_COLLIDE,
            pack(
                "Z*Z*Z*",
                self.CollideSounds,
                self.CollideParticles,
                self.CollideMarks,
            ),
        )
        CDH.w_chunk_close()

    def export(self, mode):

        os.path.mkdir("MATERIAL_PAIRS", 0)

        fn = "MATERIAL_PAIRS\\" + self.ID + ".ltx"
        bin_fh = open(fn, "w", encoding="cp1251")  # or fail("$fn: $!\n");
        bin_fh.write("[general]\n")
        bin_fh.write(f"id = {self.ID}\n")
        if self.ID_parent == 0xFFFFFFFF:
            bin_fh.write("parent_id = none\n")
        else:
            bin_fh.write(f"parent_id = {self.ID_parent}\n")

        bin_fh.write(f"mtl0 = {self.mtl0}\n")
        bin_fh.write(f"mtl1 = {self.mtl1}\n")
        self.set_props()
        bin_fh.write(f"OwnProps = {self.OwnProps}\n")
        bin_fh.write("\n[breaking]\n")
        bin_fh.write(f"BreakingSounds = {self.BreakingSounds}\n")
        bin_fh.write("\n[step]\n")
        bin_fh.write(f"StepSounds = {self.StepSounds}\n")
        bin_fh.write("\n[collide]\n")
        bin_fh.write(f"CollideSounds = {self.CollideSounds}\n")
        bin_fh.write(f"CollideParticles = {self.CollideParticles}\n")
        bin_fh.write(f"CollideMarks = {self.CollideMarks}\n")
        if self.unk_1 is not None and self.unk_2 is not None:
            bin_fh.write("\n[unk]\n")
            bin_fh.write(f"unk_1 = {self.unk_1}\n")
            bin_fh.write(f"unk_2 = {self.unk_2}\n")

        bin_fh.close()

    def _import(self, src):

        cf = ini_file(src, "r")  # or fail("$src: $!\n");
        self.ID = cf.value("general", "id")
        self.ID_parent = cf.value("general", "parent_id")
        if self.ID_parent == "none":
            self.ID_parent = 0xFFFFFFFF
        self.mtl0 = cf.value("general", "mtl0")
        self.mtl1 = cf.value("general", "mtl1")
        self.OwnProps = cf.value("general", "OwnProps")
        self.get_props()
        self.BreakingSounds = cf.value("breaking", "BreakingSounds")
        self.StepSounds = cf.value("step", "StepSounds")
        self.CollideSounds = cf.value("collide", "CollideSounds")
        self.CollideParticles = cf.value("collide", "CollideParticles")
        self.CollideMarks = cf.value("collide", "CollideMarks")
        if cf.section_exists("unk"):
            self.unk_1 = cf.value("unk", "unk_1")
            self.unk_2 = cf.value("unk", "unk_2")

        cf.close()

    def get_props(self):
        temp = ""
        if self.OwnProps == "none":
            self.OwnProps = 0xFFFFFFFF
            return

        if self.OwnProps == "all":
            self.OwnProps = 0
            return

        temp = split(r",\s*", self.OwnProps)
        ftemp = 0
        for fl in temp:
            for k in self.mflags:
                if k.name == fl:
                    ftemp += k.value

        self.OwnProps = ftemp

    def set_props(self):
        temp = ""
        if self.OwnProps == 0xFFFFFFFF:
            self.OwnProps = "none"
            return

        if self.OwnProps == 0:
            self.OwnProps = "all"
            return

        if (self.OwnProps & 0xFFFFFFFF) > 0xFF:
            self.OwnProps &= 0x76

        for k in self.mflags:
            if (self.OwnProps & k.value) == k.value:
                temp += k.name
                temp += ","
                self.OwnProps -= k.value

        if self.OwnProps != 0:
            print("%#x\n" % self.OwnProps)
            fail("some flags left\n")
        self.OwnProps = defstr(temp, 0, -1)


#######################################################################
