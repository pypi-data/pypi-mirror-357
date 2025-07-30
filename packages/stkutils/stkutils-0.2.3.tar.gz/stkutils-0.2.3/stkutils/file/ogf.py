# Module for handling stalker OGF files
# Update history:
# 	27/08/2012 - fix code for new fail() syntax
###################################################################################################################
from stkutils.binary_data import pack, unpack
from stkutils.chunked import chunked
from stkutils.data_packet import data_packet
from stkutils.perl_utils import (
    die,
    fail,
    join,
    length,
    ref,
    substr,
    universal_dict_object,
)


class ogf:
    # use strict;
    # use debug qw(fail warn);
    # use data_packet;
    # use chunked;
    # use POSIX qw(ctime);
    esmFX = 0x1
    esmStopAtEnd = 0x2
    esmNoMix = 0x4
    esmSyncPart = 0x8
    esmHasMotionMarks = 0x10  # guessed name
    # vertex constants
    OGF_VERTEXFORMAT_FVF_OLD = 0x112
    OGF_VERTEXFORMAT_FVF_1L = 0x12071980
    OGF_VERTEXFORMAT_FVF_2L = 0x240E3300  # skeletonX_pm
    OGF_VERTEXFORMAT_FVF_NL = 0x36154C80
    OGF_VERTEXFORMAT_FVF_1_CS = 1
    OGF_VERTEXFORMAT_FVF_2_CS = 2
    OGF_VERTEXFORMAT_FVF_3_CS = 3
    OGF_VERTEXFORMAT_FVF_4_CS = 4
    # loddef constants
    OGF3_HOPPE_HEADER = 1
    OGF3_HOPPE_VERT_SPLITS = 2
    OGF3_HOPPE_FIX_FACES = 3
    # motion constants
    KPF_T_PRESENT = 0x01
    KPF_R_ABSENT = 0x02
    KPF_T_HQ = 0x04
    S_POINTS = 0x01
    S_NORMALS = 0x02
    S_TEXCOORDS = 0x04
    S_LIGHTMAPS = 0x08
    S_INFLUENCES = 0x10
    S_COLORS = 0x20
    UINT32_MAX = 0xFFFFFFFF
    chunks_loaded = {
        2: {
            "OGF_HEADER": 0x1,
            "OGF_TEXTURE": 0x2,
            "OGF_TEXTURE_L": 0x4,
            "OGF_CHILD_REFS": 0x5,
            "OGF_BBOX": 0x8,
            "OGF_VERTICES": 0x10,
            "OGF_INDICES": 0x20,
            "OGF_VCONTAINER": 0x40,
            "OGF_BSPHERE": 0x80,
        },
        3: {
            "OGF_HEADER": 0x1,
            "OGF_TEXTURE": 0x2,
            "OGF_TEXTURE_L": 0x4,
            "OGF_CHILD_REFS": 0x8,
            "OGF_BBOX": 0x10,
            "OGF_VERTICES": 0x20,
            "OGF_INDICES": 0x40,
            "OGF_LODDATA": 0x80,
            "OGF_VCONTAINER": 0x100,
            "OGF_BSPHERE": 0x200,
            "OGF_CHILDREN_L": 0x400,
            "OGF_S_BONE_NAMES": 0x800,
            "OGF_S_MOTIONS_0": 0x1000,
            "OGF_DPATCH": 0x2000,
            "OGF_S_LODS": 0x4000,
            "OGF_CHILDREN": 0x8000,
            "OGF_S_SMPARAMS_0": 0x10000,
            "OGF_ICONTAINER": 0x20000,
            "OGF_S_SMPARAMS_1": 0x40000,
            "OGF_LODDEF2": 0x80000,
            "OGF_TREEDEF2": 0x100000,
            "OGF_S_IKDATA_0": 0x200000,
            "OGF_S_USERDATA": 0x400000,
            "OGF_S_IKDATA_1": 0x800000,
            "OGF_S_MOTIONS_1": 0x1000000,
            "OGF_S_DESC": 0x2000000,
            "OGF_S_IKDATA_2": 0x4000000,
            "OGF_S_MOTION_REFS_0": 0x8000000,
        },
        4: {
            "OGF_HEADER": 0x1,
            "OGF_TEXTURE": 0x2,
            "OGF_VERTICES": 0x4,
            "OGF_INDICES": 0x8,
            "OGF_P_MAP": 0x10,
            "OGF_SWIDATA": 0x20,
            "OGF_VCONTAINER": 0x40,
            "OGF_ICONTAINER": 0x80,
            "OGF_CHILDREN": 0x100,
            "OGF_CHILDREN_L": 0x200,
            "OGF_LODDEF2": 0x400,
            "OGF_TREEDEF2": 0x800,
            "OGF_S_BONE_NAMES": 0x1000,
            "OGF_S_MOTIONS_1": 0x2000,
            "OGF_S_SMPARAMS_1": 0x4000,
            "OGF_S_IKDATA_2": 0x8000,
            "OGF_S_USERDATA": 0x10000,
            "OGF_S_DESC": 0x20000,
            "OGF_S_MOTION_REFS_0": 0x40000,
            "OGF_SWICONTAINER": 0x80000,
            "OGF_GCONTAINER": 0x100000,
            "OGF_FASTPATH": 0x200000,
            "OGF_S_LODS": 0x400000,
            "OGF_S_MOTION_REFS_1": 0x800000,
            "OGF_TEXTURE_L": 0x1000000,
            "OGF_CHILD_REFS": 0x2000000,
            "OGF_BBOX": 0x4000000,
            "OGF_LODDATA": 0x8000000,
            "OGF_BSPHERE": 0x10000000,
            "OGF_DPATCH": 0x20000000,
            "OGF_S_LODS_CSKY": 0x40000000,
        },
    }
    mt_names = {  # names of appropriate engine classes
        2: {
            0x0: "MT_NORMAL",  # FVisual
            0x1: "MT_HIERRARHY",  # FHierrarhyVisual
            0x2: "MT_PROGRESSIVE",  # FProgressiveFixedVisual
            0x3: "MT_PROGRESSIVE",  # FProgressiveFixedVisual
            0x7: "",
            0x8: "MT_SKELETON_RIGID",  # CKinematics
            0x9: "",
            0xB: "",
        },
        3: {
            0x0: "MT_NORMAL",  # FVisual
            0x1: "MT_HIERRARHY",  # FHierrarhyVisual
            0x2: "MT_PROGRESSIVE",  # FProgressiveFixedVisual
            0x3: "MT_SKELETON_GEOMDEF_PM",  # CSkeletonX_PM
            0x4: "MT_SKELETON_ANIM",  # CKinematics						//CKinematicsAnimated since build 1510
            0x6: "MT_DETAIL_PATCH",  # FDetailPatch
            0x7: "MT_SKELETON_GEOMDEF_ST",  # CSkeletonX_ST
            0x8: "MT_CACHED",  # FCached
            0x9: "MT_PARTICLE",  # CPSVisual
            0xA: "MT_PROGRESSIVE2",  # FProgressive
            0xB: "MT_LOD",  # FLod
            0xC: "MT_TREE",  # FTreeVisual
            0xD: "MT_PARTICLE_EFFECT",  # PS::CParticleEffect, not used		//introduced in build 1510
            0xE: "MT_PARTICLE_GROUP",  # PS::CParticleGroup, not used		//introduced in build 1510
            0xF: "MT_SKELETON_RIGID",  # CKinematics						//introduced in build 1510
        },
        4: {
            0x0: "MT_NORMAL",  # FVisual
            0x1: "MT_HIERRARHY",  # FHierrarhy_Visual
            0x2: "MT_PROGRESSIVE",  # FProgressive
            0x3: "MT_SKELETON_ANIM",  # CKinematics_Animated		#CSkeletonAnimated before 2205
            0x4: "MT_SKELETON_GEOMDEF_PM",  # CSkeletonX_PM
            0x5: "MT_SKELETON_GEOMDEF_ST",  # CSkeletonX_ST
            0x6: "MT_LOD",  # FLod
            0x7: "MT_TREE_ST",  # FTreeVisual_ST
            0x8: "MT_PARTICLE_EFFECT",  # CParticleEffect, not used
            0x9: "MT_PARTICLE_GROUP",  # CParticleGroup, not used
            0xA: "MT_SKELETON_RIGID",  # CKinematics
            0xB: "MT_TREE_PM",  # FTreeVisual_PM				#introduced in build 1957
        },
    }
    chunk_names = {
        2: {
            "OGF_HEADER": 0x1,
            "OGF_TEXTURE": 0x2,
            "OGF_TEXTURE_L": 0x3,
            "OGF_CHILD_REFS": 0x5,
            "OGF_BBOX": 0x6,
            "OGF_VERTICES": 0x7,
            "OGF_INDICES": 0x8,
            "OGF_LODDATA": 0x9,
            "OGF_S_MOTIONS_0": 0xA,  # ???
            "OGF_VCONTAINER": 0xB,
            "OGF_BSPHERE": 0xC,
            "OGF_CHILDREN_L": 0xD,
            "OGF_S_BONE_NAMES": 0xE,
        },
        3: {
            "OGF_HEADER": 0x1,
            "OGF_TEXTURE": 0x2,
            "OGF_TEXTURE_L": 0x3,
            "OGF_CHILD_REFS": 0x5,
            "OGF_BBOX": 0x6,
            "OGF_VERTICES": 0x7,
            "OGF_INDICES": 0x8,
            "OGF_LODDATA": 0x9,
            "OGF_VCONTAINER": 0xA,
            "OGF_BSPHERE": 0xB,
            "OGF_CHILDREN_L": 0xC,
            "OGF_S_BONE_NAMES": 0xD,
            "OGF_S_MOTIONS_0": 0xE,
            "OGF_DPATCH": 0xF,
            "OGF_S_LODS": 0x10,
            "OGF_CHILDREN": 0x11,
            "OGF_S_SMPARAMS_0": 0x12,
            "OGF_ICONTAINER": 0x13,
            "OGF_S_SMPARAMS_1": 0x14,
            "OGF_LODDEF2": 0x15,
            "OGF_TREEDEF2": 0x16,
            "OGF_S_IKDATA_0": 0x17,
            "OGF_S_USERDATA": 0x18,
            "OGF_S_IKDATA_1": 0x19,
            "OGF_S_MOTIONS_1": 0x1A,
            "OGF_S_DESC": 0x1B,
            "OGF_S_IKDATA_2": 0x1C,
            "OGF_S_MOTION_REFS_0": 0x1D,
        },
        4: {
            "OGF_HEADER": 0x1,
            "OGF_TEXTURE": 0x2,
            "OGF_VERTICES": 0x3,
            "OGF_INDICES": 0x4,
            "OGF_P_MAP": 0x5,  # used before build 1925
            "OGF_SWIDATA": 0x6,
            "OGF_VCONTAINER": 0x7,  # used before build 2205
            "OGF_ICONTAINER": 0x8,  # used before build 2205
            "OGF_CHILDREN": 0x9,
            "OGF_CHILDREN_L": 0xA,
            "OGF_LODDEF2": 0xB,
            "OGF_TREEDEF2": 0xC,
            "OGF_S_BONE_NAMES": 0xD,
            "OGF_S_MOTIONS_1": 0xE,  # used before build 2205
            "OGF_S_SMPARAMS_1": 0xF,  # used before build 2205
            "OGF_S_IKDATA_2": 0x10,
            "OGF_S_USERDATA": 0x11,
            "OGF_S_DESC": 0x12,
            "OGF_S_MOTION_REFS_0": 0x13,
            "OGF_SWICONTAINER": 0x14,  # introduced in build 1957
            "OGF_GCONTAINER": 0x15,  # introduced in build 2205
            "OGF_FASTPATH": 0x16,  # introduced in build 2205
            "OGF_S_LODS": 0x17,  # introduced in build ????
            "OGF_S_MOTION_REFS_1": 0x18,  # introduced in Clear Sky
        },
    }

    def __init__(self):

        # common params
        self.ogf_version = 0
        self.model_type = 0
        self.shader_id = 0
        self.texture_id = 0
        self.ogf_object = ""
        self.ogf_creator = ""
        self.unk = 0
        self.creator = ""
        self.create_time = 0
        self.editor = ""
        self.edit_time = 0
        self.texture_name = ""
        self.shader_name = ""
        self.userdata = ""
        # bounds of model
        self.bbox = universal_dict_object()
        self.bsphere = universal_dict_object()
        # offsets to geometry definition. exists if there is no vertices and indices in model
        self.m_fast = universal_dict_object()
        self.m_fast.swi = universal_dict_object()
        self.ext_vb_index = 0
        self.ext_vb_offset = 0
        self.ext_vb_size = 0
        self.ext_ib_index = 0
        self.ext_ib_offset = 0
        self.ext_ib_size = 0
        # geometry vertices
        self.vertices = universal_dict_object()
        # geometry indices
        self.indices = []
        # parts of the model in case of hierarhical. may be only one of following
        self.child_refs = []
        self.children_l = []
        self.children = []
        # bones data
        self.bones = []
        # motions data
        self.motion_refs_0 = 0
        self.motion_refs_1 = []
        self.motions = universal_dict_object()
        self.partitions = []
        # detalization change data. may be only one of following
        self.ext_swib_index = 0
        self.lod = universal_dict_object()
        self.swi = universal_dict_object()
        # lods - billboards. may be only one of following
        self.lods_ref = ""
        self.lods = []
        # unknown
        self.lod_faces = []
        self.treedef = universal_dict_object()
        # service
        self.ogf_subversion = 0
        self.loaded_chunks = 0

    def version(*args):
        if args[1] is not None:
            args[0].ogf_version = args[1]
        return args[0].ogf_version

    def calculate_subversion(self):
        if self.ogf_version != 4:
            return

    def read(
        self,
        data,
    ):  # обертка над _read, чтобы можно было передавать и данные, и хэндл.
        if ref(data) == "chunked":
            self._read(data)
            return

        cf = chunked(data, "data")
        self._read(cf)
        cf.close()

    def _read(self, cf):
        if not (cf.find_chunk(0x1)):
            fail("cannot find OGF_HEADER chunk")

        self.read_header(cf)
        cf.close_found_chunk()
        # SWITCH: {
        if self.mt_names[self.ogf_version][self.model_type] == "MT_NORMAL":
            self.read_visual(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_HIERRARHY":
            self.read_hierrarhy_visual(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_PROGRESSIVE":
            self.read_progressive(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_SKELETON_ANIM":
            self.read_kinematics_animated(cf)
        elif (
            self.mt_names[self.ogf_version][self.model_type] == "MT_SKELETON_GEOMDEF_PM"
        ):
            self.read_skeletonx_pm(cf)
        elif (
            self.mt_names[self.ogf_version][self.model_type] == "MT_SKELETON_GEOMDEF_ST"
        ):
            self.read_skeletonx_st(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_PROGRESSIVE2":
            self.read_progressive2(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_LOD":
            self.read_lod(cf)
        elif (
            self.mt_names[self.ogf_version][self.model_type] == "MT_TREE"
            or self.mt_names[self.ogf_version][self.model_type] == "MT_TREE_ST"
        ):
            self.read_tree_visual_st(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_SKELETON_RIGID":
            self.read_kinematics(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_TREE_PM":
            self.read_tree_visual_pm(cf)
        else:
            fail("unexpected model type " + str(self.model_type))

    def read_header(self, cf):

        packet = data_packet(cf.r_chunk_data())
        (self.ogf_version, self.model_type, self.shader_id) = packet.unpack("CCv", 4)
        if not self.ogf_version >= 2 and self.ogf_version <= 4:
            fail("unexpected ogf version " + self.ogf_version)
        if self.ogf_version == 4:
            self.read_bbox(packet)
            self.read_bsphere(packet)

        self.set_loaded("OGF_HEADER")

    def read_render_visual(self, cf):
        if self.ogf_version == 3:
            if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_BBOX"]):
                packet = data_packet(cf.r_chunk_data())
                self.read_bbox(packet)
                self.set_loaded("OGF_BBOX")
                cf.close_found_chunk()
            else:
                fail("cannot find OGF_BBOX chunk")

        if self.ogf_version != 4 and cf.find_chunk(
            self.chunk_names[self.ogf_version]["OGF_BSPHERE"],
        ):
            packet = data_packet(cf.r_chunk_data())
            self.read_bsphere(packet)
            self.set_loaded("OGF_BSPHERE")
            cf.close_found_chunk()

        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_S_DESC"]):
            self.read_s_desc(cf)
            cf.close_found_chunk()

        if self.ogf_version != 4 and cf.find_chunk(
            self.chunk_names[self.ogf_version]["OGF_TEXTURE_L"],
        ):
            self.read_texture_l(cf)
            cf.close_found_chunk()
        elif cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_TEXTURE"]):
            self.read_texture(cf)
            cf.close_found_chunk()

    def read_visual(self, cf):

        self.read_render_visual(cf)
        if self.ogf_version == 4 and cf.find_chunk(
            self.chunk_names[self.ogf_version]["OGF_GCONTAINER"],
        ):
            self.read_gcontainer(cf)
            cf.close_found_chunk()
            if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_FASTPATH"]):
                self.read_fastpath(cf)
                cf.close_found_chunk()

            return

        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_VCONTAINER"]):
            self.read_vcontainer(cf)
            cf.close_found_chunk()
        elif cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_VERTICES"]):
            self.read_vertices(cf)
            cf.close_found_chunk()

        if self.ogf_version != 2 and cf.find_chunk(
            self.chunk_names[self.ogf_version]["OGF_ICONTAINER"],
        ):
            self.read_icontainer(cf)
            cf.close_found_chunk()
        elif cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_INDICES"]):
            self.read_indices(cf)
            cf.close_found_chunk()

    def read_hierrarhy_visual(self, cf):

        self.read_render_visual(cf)
        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_CHILDREN_L"]):
            self.read_children_l(cf)
        elif self.ogf_version != 2 and cf.find_chunk(
            self.chunk_names[self.ogf_version]["OGF_CHILDREN"],
        ):
            self.read_children(cf)
        elif cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_CHILD_REFS"]):
            self.read_child_refs(cf)
        else:
            fail("Invalid visual, no children")

        cf.close_found_chunk()

    def read_progressive(self, cf):
        self.read_visual(cf)
        if self.ogf_version == 4 and cf.find_chunk(
            self.chunk_names[self.ogf_version]["OGF_SWIDATA"],
        ):
            self.read_swidata(cf)
            cf.close_found_chunk()
        elif cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_LODDATA"]):
            self.read_loddata(cf)
            cf.close_found_chunk()
        else:
            fail("Invalid visual, no loddata")

    def read_kinematics(self, cf):
        self.read_hierrarhy_visual(cf)
        if self.ogf_version == 4:
            size = cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_S_LODS"])
            if size:
                if size < 0x100:
                    self.read_s_lods_csky(cf)
                else:
                    self.read_s_lods(cf)

                cf.close_found_chunk()

        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_S_USERDATA"]):
            self.read_s_userdata(cf)
            cf.close_found_chunk()

        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_S_BONE_NAMES"]):
            self.read_s_bone_names(cf)
            cf.close_found_chunk()
        else:
            fail("cannot find OGF_S_BONE_NAMES")

        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_S_IKDATA_2"]):
            self.read_s_ikdata(cf, 2)
            cf.close_found_chunk()
        elif cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_S_IKDATA_1"]):
            self.read_s_ikdata(cf, 1)
            cf.close_found_chunk()
        elif cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_S_IKDATA_0"]):
            self.read_s_ikdata(cf, 0)
            cf.close_found_chunk()

    def read_kinematics_animated(self, cf):
        self.read_kinematics(cf)
        if self.ogf_version == 4 and cf.find_chunk(
            self.chunk_names[self.ogf_version]["OGF_S_MOTION_REFS_1"],
        ):
            self.read_smotion_refs_1(cf)
            cf.close_found_chunk()
            return
        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_S_MOTION_REFS_0"]):
            self.read_smotion_refs_0(cf)
            cf.close_found_chunk()
            return
        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_S_SMPARAMS_1"]):
            self.read_s_smparams(cf, 1)
            cf.close_found_chunk()
        elif cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_S_SMPARAMS_0"]):
            self.read_s_smparams(cf, 0)
            cf.close_found_chunk()

        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_S_MOTIONS_1"]):
            self.read_smotions(cf, 1)
            cf.close_found_chunk()
        elif cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_S_MOTIONS_0"]):
            self.read_smotions(cf, 0)
            cf.close_found_chunk()
        else:
            fail("Invalid visual, no motions")

    def read_skeletonx(self, cf):
        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_VERTICES"]):
            (format,) = unpack("V", cf.r_chunk_data())
            if (
                format != self.OGF_VERTEXFORMAT_FVF_1L
                or format == self.OGF_VERTEXFORMAT_FVF_2L
            ):
                fail("wrong vertex format (" + format + ")")
            cf.close_found_chunk()
            return
        fail("cannot find OGF_VERTICES")

    def read_skeletonx_pm(self, cf):
        self.read_skeletonx(cf)
        self.read_progressive(cf)

    def read_skeletonx_st(self, cf):
        self.read_skeletonx(cf)
        self.read_visual(cf)

    def read_progressive2(self, cf):
        self.read_render_visual(cf)
        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_LODS"]):
            self.read_s_lods(cf)
            cf.close_found_chunk()
        else:
            fail("Invalid visual, no lods")

    def read_lod(self, cf):
        self.read_hierrarhy_visual(cf)
        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_LODDEF2"]):
            self.read_loddef2(cf)
            cf.close_found_chunk()
        else:
            fail("cannot find chunk OGF_LODDEF2")

    def read_tree_visual(self, cf):
        self.read_visual(cf)
        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_TREEDEF2"]):
            self.read_treedef2(cf)
            cf.close_found_chunk()
        else:
            fail("cannot find OGF_TREEDEF2")

    def read_tree_visual_st(self, cf):
        self.read_tree_visual(cf)

    def read_tree_visual_pm(self, cf):
        self.read_tree_visual(cf)
        if cf.find_chunk(self.chunk_names[self.ogf_version]["OGF_SWICONTAINER"]):
            self.read_swicontainer(cf)
            cf.close_found_chunk()
        else:
            fail("cannot find OGF_SWICONTAINER")

    def read_bbox(self, packet):
        self.bbox.min = packet.unpack("f3", 12)
        self.bbox.max = packet.unpack("f3", 12)

    def read_bsphere(self, packet):
        self.bsphere.c = packet.unpack("f3", 12)
        (self.bsphere.r) = packet.unpack("f", 4)

    def read_s_desc(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (
            self.ogf_object,
            self.ogf_creator,
            self.unk,
            self.creator,
            self.create_time,
            self.editor,
            self.edit_time,
        ) = packet.unpack("Z*Z*VZ*VZ*V")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())
        self.set_loaded("OGF_S_DESC")

    def read_texture_l(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (self.texture_id, self.shader_id) = packet.unpack("VV", 8)
        self.set_loaded("OGF_TEXTURE_L")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def read_texture(self, cf):

        packet = data_packet(cf.r_chunk_data())
        (self.texture_name, self.shader_name) = packet.unpack("Z*Z*")
        self.set_loaded("OGF_TEXTURE")

    # if not packet.resid() == 0:
    # 	fail('there some data in packet left: '.packet.resid())

    def read_gcontainer(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (
            self.ext_vb_index,
            self.ext_vb_offset,
            self.ext_vb_size,
            self.ext_ib_index,
            self.ext_ib_offset,
            self.ext_ib_size,
        ) = packet.unpack("VVVVVV", 24)
        self.set_loaded("OGF_GCONTAINER")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def read_fastpath(self, cf):

        # 	$self.m_fast = cf.r_chunk_data();
        cf.find_chunk(0x15)
        packet = data_packet(cf.r_chunk_data())
        self.m_fast.gcontainer = packet.unpack("V6")
        self.m_fast.is_swi = 0
        cf.close_found_chunk()
        if cf.find_chunk(0x6):
            print("read swi\n")
            self.read_swidata(self.m_fast, cf)
            self.m_fast.is_swi = 1
            cf.close_found_chunk()

        self.set_loaded("OGF_FASTPATH")

    def read_vcontainer(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (self.ext_vb_index, self.ext_vb_offset, self.ext_vb_size) = packet.unpack(
            "VVV",
            12,
        )
        self.set_loaded("OGF_VCONTAINER")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def read_vertices(self, cf):
        data = cf.r_chunk_data()
        (vertex_format, vertex_count) = unpack("VV", substr(data, 0, 8, ""))
        self.vertices.format = vertex_format
        if vertex_format == self.OGF_VERTEXFORMAT_FVF_OLD:
            for i in range(vertex_count):
                packet = data_packet(substr(data, 0, 32, ""))
                vertex = universal_dict_object()
                vertex.point = packet.unpack("f3", 12)
                vertex.normal = packet.unpack("f3", 12)
                vertex.textcoords = packet.unpack("f2", 8)
                self.vertices.data.append(vertex)

        elif self.ogf_version == 3 and vertex_format == self.OGF_VERTEXFORMAT_FVF_1L:
            for i in range(vertex_count):
                packet = data_packet(substr(data, 0, 36, ""))
                vertex = universal_dict_object()
                vertex.point = packet.unpack("f3", 12)
                vertex.normal = packet.unpack("f3", 12)
                vertex.textcoords = packet.unpack("f2", 8)
                (vertex.matrix) = packet.unpack("V", 4)
                self.vertices.data.append(vertex)

        elif (
            vertex_format == self.OGF_VERTEXFORMAT_FVF_1L
            or vertex_format == self.OGF_VERTEXFORMAT_FVF_1_CS
        ):
            for i in range(vertex_count):
                packet = data_packet(substr(data, 0, 60, ""))
                vertex = universal_dict_object()
                vertex.point = packet.unpack("f3", 12)
                vertex.normal = packet.unpack("f3", 12)
                vertex.t = packet.unpack("f3", 12)
                vertex.b = packet.unpack("f3", 12)
                vertex.textcoords = packet.unpack("f2", 8)
                (vertex.matrix) = packet.unpack("V", 4)
                self.vertices.data.append(vertex)

        elif (
            vertex_format == self.OGF_VERTEXFORMAT_FVF_2L
            or vertex_format == self.OGF_VERTEXFORMAT_FVF_2_CS
        ):
            for i in range(vertex_count):
                packet = data_packet(substr(data, 0, 64, ""))
                vertex = universal_dict_object()
                (vertex.matrix0, vertex.matrix1) = packet.unpack("vv", 4)
                vertex.point = packet.unpack("f3", 12)
                vertex.normal = packet.unpack("f3", 12)
                vertex.t = packet.unpack("f3", 12)
                vertex.b = packet.unpack("f3", 12)
                (vertex.w) = packet.unpack("f", 4)
                vertex.textcoords = packet.unpack("f2", 8)
                self.vertices.data.append(vertex)

        elif vertex_format == self.OGF_VERTEXFORMAT_FVF_3_CS:
            for i in range(vertex_count):
                packet = data_packet(substr(data, 0, 70, ""))
                vertex = universal_dict_object()
                (vertex.matrix0, vertex.matrix1, vertex.matrix2) = packet.unpack(
                    "vvv",
                    6,
                )
                vertex.point = packet.unpack("f3", 12)
                vertex.normal = packet.unpack("f3", 12)
                vertex.t = packet.unpack("f3", 12)
                vertex.b = packet.unpack("f3", 12)
                (vertex.w0, vertex.w1) = packet.unpack("ff", 8)
                vertex.textcoords = packet.unpack("f2", 8)
                self.vertices.data.append(vertex)

        elif vertex_format == self.OGF_VERTEXFORMAT_FVF_4_CS:
            for i in range(vertex_count):
                packet = data_packet(substr(data, 0, 76, ""))
                vertex = universal_dict_object()
                (vertex.matrix0, vertex.matrix1, vertex.matrix2, vertex.matrix3) = (
                    packet.unpack("vvvv", 8)
                )
                vertex.point = packet.unpack("f3", 12)
                vertex.normal = packet.unpack("f3", 12)
                vertex.t = packet.unpack("f3", 12)
                vertex.b = packet.unpack("f3", 12)
                (vertex.w0, vertex.w1, vertex.w2) = packet.unpack("fff", 12)
                vertex.textcoords = packet.unpack("f2", 8)
                self.vertices.data.append(vertex)

        else:
            fail("unsupported FVF")

        if length(data) != 0:
            fail("there some data in packet left: " + length(data))
        self.set_loaded("OGF_VERTICES")

    def read_icontainer(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (self.ext_ib_index, self.ext_ib_offset, self.ext_ib_size) = packet.unpack(
            "VVV",
            12,
        )
        self.set_loaded("OGF_ICONTAINER")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def read_indices(self, cf):

        data = cf.r_chunk_data()
        (indices_count,) = unpack("V", substr(data, 0, 4, ""))
        for i in range(indices_count):
            (index) = substr(data, 0, 2, "")
            self.indices.append(index)

        if length(data) != 0:
            fail("there some data in packet left: " + length(data))
        self.set_loaded("OGF_INDICES")

    def read_children_l(self, cf):
        packet = data_packet(cf.r_chunk_data())
        self.children_l = packet.unpack("V/V")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())
        self.set_loaded("OGF_CHILDREN_L")

    def read_children(self, cf):
        expected_id = 0
        while True:
            (nnnn, size) = cf.r_chunk_open()
            if not (nnnn is not None):
                break
            if nnnn != expected_id:
                fail(f"unexpected chunk {nnnn}")
            child = ogf()
            child.read(cf)
            cf.r_chunk_close()
            self.children.append(child)
            expected_id += 1

        self.set_loaded("OGF_CHILDREN")

    def read_child_refs(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (count) = packet.unpack("V", 4)
        for i in range(count):
            (ref) = packet.unpack("Z*")
            self.child_refs.append(ref)

        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())
        self.set_loaded("OGF_CHILD_REFS")

    def read_swidata(self, cf):
        packet = data_packet(cf.r_chunk_data())
        self.swi.reserved = packet.unpack("V4", 16)
        (swi_count) = packet.unpack("V", 4)
        for i in range(swi_count):
            swi = universal_dict_object()
            (swi.offset, swi.num_tris, swi.num_verts) = packet.unpack("lvv", 8)
            self.swi.data.append(swi)

        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())
        if self.ogf_version is not None:
            self.set_loaded(self, "OGF_SWIDATA")

    def read_loddata(self, cf):
        while 1:
            (id, size) = cf.r_chunk_open()
            if not (id is not None):
                break

            if id == self.OGF3_HOPPE_HEADER:
                self.read_hoppe_header(self.loddata, cf)
            elif id == self.OGF3_HOPPE_VERT_SPLITS:
                self.read_hoppe_vertsplits(self.loddata, self, cf)
            elif id == self.OGF3_HOPPE_FIX_FACES:
                self.read_hoppe_fix_faces(self.loddata, cf)
            else:
                fail(f"unexpected chunk {id}")

            cf.r_chunk_close()

        cf.r_chunk_close()
        self.set_loaded("OGF_LODDATA")

    def read_hoppe_header(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (self.min_vertices, self.max_vertices) = packet.unpack("VV", 4)

    def read_hoppe_vertsplits(self, _global, cf):
        packet = data_packet(cf.r_chunk_data())
        self.num_vertsplits = _global.vertex_count - self.min_vertices
        for i in range(self.num_vertsplits):
            split = universal_dict_object()
            (split.vert, split.num_tris, split.num_verts) = packet.unpack("vCC", 4)
            self.vertsplits.append(split)

    def read_hoppe_fix_faces(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (self.num_fix_faces) = packet.unpack("V", 4)
        self.fix_faces = packet.unpack(f"(v){self.num_fix_faces}")

    def read_s_lods_csky(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (self.lods_ref) = packet.unpack("Z*")
        self.set_loaded("OGF_S_LODS_CSKY")

    def read_s_lods(self, cf):
        expected_id = 0
        while True:
            (nnnn, size) = cf.r_chunk_open()
            if not (nnnn is not None):
                break
            if nnnn != expected_id:
                fail(f"unexpected chunk {nnnn}")
            lod = ogf()
            lod.read(cf)
            cf.r_chunk_close()
            self.lods.append(lod)
            expected_id += 1

        self.set_loaded("OGF_S_LODS")

    def read_s_userdata(self, cf):
        packet = data_packet(cf.r_chunk_data())
        n = packet.resid()
        (self.userdata) = packet.unpack(f"a{n}")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())
        self.set_loaded("OGF_S_USERDATA")

    def read_s_bone_names(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (count) = packet.unpack("V", 4)
        for i in range(count):
            bone = universal_dict_object()
            (bone.name, bone.parent) = packet.unpack("Z*Z*")
            self.read_obb(bone, packet)
            self.bones.append(bone)

        self.set_loaded("OGF_S_BONE_NAMES")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def is_root(*args):
        return args[0].parent == ""

    def read_obb(*args):
        self = args[0]
        self.rotate = args[1].unpack("f9", 36)
        self.translate = args[1].unpack("f3", 12)
        self.halfsize = args[1].unpack("f3", 12)

    def read_s_ikdata(self, cf, mode):
        self.set_loaded("OGF_S_IKDATA_" + mode)  # temp
        return  # temp
        packet = data_packet(cf.r_chunk_data())
        for bone in self.bones:
            ik = universal_dict_object()
            ik.bone_shape = universal_dict_object()
            ik.joint_data = universal_dict_object()
            if mode == 2:
                (ik.version, ik.game_mtl_name) = packet.unpack("VZ*")
            else:
                (ik.game_mtl_name) = packet.unpack("Z*")

            read_s_bone_shape(ik.bone_shape, packet)
            read_s_joint_ik_data(ik.joint_data, packet, ik.version)
            ik.bind_offset = math.create("vector", 3)
            ik.bind_offset.set(packet.unpack("f3", 12))
            ik.bind_rotate = math.create("vector", 3)
            ik.bind_rotate.set(packet.unpack("f3", 12))
            (ik.mass, ik.center_of_mass) = packet.unpack("ff3", 16)
            bone.ik_data.append(ik)

        self.set_loaded("OGF_S_IKDATA_" + mode)
        if packet.resid() != 0:
            fail("there some data in packet left: ".packet.resid())

    def read_s_bone_shape(*args):
        self = args[0]
        (self.type, self.flags) = args[1].unpack("vv", 4)
        self.box = universal_dict_object()
        self.sphere = universal_dict_object()
        self.cylinder = universal_dict_object()
        self.read_obb(self.box, args[1])
        self.read_sphere(self.sphere, args[1])
        self.read_cylinder(self.cylinder, args[1])

    def read_sphere(*args):
        self = args[0]
        self.p = args[1].unpack("f3", 12)
        (self.r) = args[1].unpack("f", 4)

    def read_cylinder(*args):
        self = args[0]
        self.center = args[1].unpack("f3", 12)
        self.direction = args[1].unpack("f3", 12)
        (self.height) = args[1].unpack("f", 4)
        (self.radius) = args[1].unpack("f", 4)

    def read_s_joint_ik_data(self, packet, version):
        (self.type) = packet.unpack("V", 4)
        self.limits = []
        self.limits[0] = universal_dict_object()
        self.read_s_joint_limit(self.limits[0], packet)
        self.limits[1] = universal_dict_object()
        self.read_s_joint_limit(self.limits[1], packet)
        self.limits[2] = universal_dict_object()
        self.read_s_joint_limit(self.limits[2], packet)
        (self.spring_factor, self.damping_factor) = packet.unpack("ff", 8)
        if version != 0:
            (self.ik_flags, self.break_force, self.break_torque) = packet.unpack(
                "Vff",
                12,
            )
        if version == 2:
            (self.friction) = packet.unpack("f", 4)

    def read_s_joint_limit(*args):
        self = args[0]
        self.limit = args[1].unpack("f2", 8)
        (self.spring_factor, self.damping_factor) = args[1].unpack("ff", 8)

    def read_smotion_refs_1(self, cf):
        packet = data_packet(cf.r_chunk_data())
        self.motion_refs_1 = packet.unpack("V/(Z*)")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())
        self.set_loaded("OGF_S_MOTION_REFS_1")

    def read_smotion_refs_0(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (self.motion_refs_0) = packet.unpack("Z*")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())
        self.set_loaded("OGF_S_MOTION_REFS_0")

    def read_s_smparams(self, cf, mode):

        packet = data_packet(cf.r_chunk_data())
        if mode == 1:
            (self.motions.params_version) = packet.unpack(
                "v",
                2,
            )  ### build 1865 - exists!!!
        (partition_count) = packet.unpack("v", 2)
        for i in range(partition_count):
            part = universal_dict_object()
            (part.name, part.bone_count) = packet.unpack("Z*v")
            for i in range(part.bone_count):
                bone = universal_dict_object()
                if mode == 0 or self.motions.params_version == 1:
                    (bone.bone_id) = packet.unpack("V", 4)
                elif self.motions.params_version == 2:
                    (bone.bone_name) = packet.unpack("Z*")
                elif (
                    self.motions.params_version == 3 or self.motions.params_version == 4
                ):
                    (bone.bone_name, bone.bone_id) = packet.unpack("Z*V")

                part.bones.append(bone)

            self.partitions.append(part)

        (motion_count) = packet.unpack("v", 2)
        for i in range(motion_count):
            mot = universal_dict_object()
            if mode == 1:
                (mot.name, mot.flags) = packet.unpack("Z*V")
                self.read_motion_def(mot, packet)
                if self.motions.params_version == 4:
                    (num_marks) = packet.unpack("V", 4)
                    for j in range(num_marks):
                        mmark = universal_dict_object()
                        self.read_motion_mark(mmark, packet)
                        mot.mmarks.append(mmark)

                else:
                    (mot.name, mot.flags) = packet.unpack("Z*C")
                    self.read_motion_def(mot, packet)
                    flag = packet.unpack("C", 1)
                    if flag != 1:
                        mot.flags += 0x2

            self.motions.data.append(mot)

        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())
        self.set_loaded("OGF_S_SMPARAMS_" + mode)

    def read_motion_def(*args):
        self = args[0]
        (
            self.bone_or_part,
            self.motion,
            self.speed,
            self.power,
            self.accrue,
            self.falloff,
        ) = args[1].unpack("vvffff", 20)

    def read_motion_mark(*args):
        self = args[0]
        self.name = ""

        while 1:
            (c) = args[1].unpack("a")
            if c == "\n" or c == "\r":
                break
            self.name += c

        (c) = args[1].unpack("a")
        if c != "\n":
            die()
        (count) = args[1].unpack("V", 4)
        for i in range(count):
            int = universal_dict_object()
            (int.min, int.max) = args[1].unpack("ff", 8)
            self.intervals.append(int)

    def read_smotions(self, cf, mode):
        expected_id = 0
        while True:
            (nnnn, size) = cf.r_chunk_open()
            if not (nnnn is not None):
                break
            if nnnn != expected_id:
                fail(f"unexpected chunk {nnnn}")
            if nnnn == 0:
                (motions_count,) = unpack("V", cf.r_chunk_data())
                if motions_count != len(self.motions.data):
                    fail(
                        "motions count ("
                        + motions_count
                        + ") didnot match motion params count ("
                        + len(self.motions.data)
                        + ")",
                    )
            else:
                pass
            # temp
            # read_motion($self.motions.data[$nnnn - 1], cf, $mode);

            cf.r_chunk_close()
            expected_id += 1

        self.set_loaded("OGF_S_MOTIONS_" + mode)

    def read_motion(self, cf, mode):
        packet = data_packet(cf.r_chunk_data())
        (self.name, self.keys_count) = packet.unpack("Z*V")
        # print(f"{self.name}, {self.keys_count}\n")
        if self.keys_count == 0:
            if packet.resid() != 0:
                fail("there some data in packet left: " + packet.resid())
            return

        if mode == 1:
            i = 0
            while packet.resid() > 0:
                keyst = []
                bone = universal_dict_object()
                (bone.flags) = packet.unpack("C", 1)
                # print(f"{i}:{bone.flags}\n")
                if bone.flags & ~7 != 0:
                    fail("flags didnot match:" + bone.flags)
                if bone.flags & self.KPF_R_ABSENT:
                    bone.keysr = packet.unpack("s4", 4)
                    print("keysr = " + join(",", bone.keysr) + "\n")
                else:
                    (bone.crc_keysr, bone.keysr) = packet.unpack(
                        f"V(s4){self.keys_count}",
                        4 + 4 * self.keys_count,
                    )
                    print(f"keysr = {bone.crc_keysr}, " + join(",", bone.keysr) + "\n")

                # 		dequantize_qr(\bone.keysr);
                if bone.flags & self.KPF_T_PRESENT:
                    (bone.crc_keyst) = packet.unpack("V", 4)
                    if bone.flags & self.KPF_T_HQ:
                        bone.keyst = packet.unpack(
                            f"(s3){self.keys_count}",
                            3 * self.keys_count,
                        )
                        print("keyst = " + join(",", bone.keyst) + "\n")
                    else:
                        bone.keyst = packet.unpack(
                            f"(c3){self.keys_count}",
                            3 * self.keys_count,
                        )
                        print("keyst = " + join(",", bone.keyst) + "\n")

                    bone.sizet = packet.unpack("f3", 12)
                    print("sizet = " + join(",", bone.sizet) + "\n")
                elif bone.flags & self.KPF_T_HQ != 0:
                    die()

                bone.initt = packet.unpack("f3", 12)
                print("initt = " + join(",", bone.initt) + "\n")
                self.bones.append(bone)
                i += 1

        else:
            i = 0
            while packet.resid() > 0:
                bone = universal_dict_object()
                bone.keys = packet.unpack(
                    f"(s4f3){self.keys_count}",
                    16 * self.keys_count,
                )
                # 		dequantize_qr(\bone.keysr);
                self.bones.append(bone)
                i += 1

        if packet.resid() != 0:
            fail("there some data in packet left: ".packet.resid())

    def read_loddef(self):
        pass

    # if ( !IReader__find_chunk(a3, 21, 0) )
    #    xrDebug__fail(Debug, "data.find_chunk(OGF_LODDEF)", ".\\FLOD.cpp", 10);
    #  v6 = (int)((char *)v5 + 144);
    # v69 = 8;
    # do
    #  {
    #   v7 = v6 - 56;
    #    IReader__r(v4, v6 - 56, 96);
    #    v8 = *(float *)(v6 - 32) - *(float *)(v6 - 56);
    #    v9 = *(float *)(v6 - 28) - *(float *)(v6 - 52);
    #    v10 = *(float *)(v6 - 24) - *(float *)(v6 - 48);
    #    v11 = *(float *)(v6 - 8) - *(float *)(v6 - 32);
    #    v12 = *(float *)(v6 - 4) - *(float *)(v6 - 28);
    #    v13 = *(float *)v6 - *(float *)(v6 - 24);
    #    v48 = v13 * v9 - v12 * v10;
    #    v52 = v10 * v11 - v13 * v8;
    #    v56 = v12 * v8 - v9 * v11;
    #    v70 = v56 * v56 + v52 * v52 + v48 * v48;
    #    if ( std__numeric_limits_float___min() >= v70 )
    #    {
    #      v14 = v56;
    #    }
    #    else
    #    {
    #      v15 = sqrt(1.0 / v70);
    #      v48 = v48 * v15;
    #      v52 = v52 * v15;
    #      v14 = v15 * v56;
    #    }
    #    v66 = v14;
    #    v16 = *(float *)(v6 - 8) - *(float *)(v6 - 32);
    #    v60 = v48;
    #    v63 = v52;
    #    v17 = *(float *)(v6 - 4) - *(float *)(v6 - 28);
    #    v18 = *(float *)v6 - *(float *)(v6 - 24);
    #    v19 = *(float *)(v6 + 16) - *(float *)(v6 - 8);
    #    v20 = *(float *)(v6 + 20) - *(float *)(v6 - 4);
    #    v21 = *(float *)(v6 + 24) - *(float *)v6;
    #    v49 = v21 * v17 - v20 * v18;
    #    v53 = v18 * v19 - v21 * v16;
    #    v57 = v20 * v16 - v17 * v19;
    #    v71 = v57 * v57 + v53 * v53 + v49 * v49;
    #    if ( std__numeric_limits_float___min() >= v71 )
    #    {
    #      v22 = v57;
    #    }
    #    else
    #    {
    #      v23 = sqrt(1.0 / v71);
    #      v49 = v49 * v23;
    #      v53 = v53 * v23;
    #      v22 = v23 * v57;
    #    }
    #    v61 = v49 + v60;
    #    v64 = v53 + v63;
    #    v67 = v22 + v66;
    #    v24 = *(float *)(v6 + 16) - *(float *)(v6 - 8);
    #    v25 = *(float *)(v6 + 20) - *(float *)(v6 - 4);
    #    v26 = *(float *)(v6 + 24) - *(float *)v6;
    #    v27 = *(float *)v7 - *(float *)(v6 + 16);
    #    v28 = *(float *)(v6 - 52) - *(float *)(v6 + 20);
    #    v29 = *(float *)(v6 - 48) - *(float *)(v6 + 24);
    #    v50 = v29 * v25 - v28 * v26;
    #    v54 = v26 * v27 - v29 * v24;
    #    v58 = v28 * v24 - v25 * v27;
    #    v72 = v58 * v58 + v54 * v54 + v50 * v50;
    #    if ( std__numeric_limits_float___min() >= v72 )
    #    {
    #      v30 = v58;
    #    }
    #    else
    #    {
    #      v31 = sqrt(1.0 / v72);
    #      v50 = v50 * v31;
    #      v54 = v54 * v31;
    #      v30 = v31 * v58;
    #    }
    #    v62 = v50 + v61;
    #    v65 = v54 + v64;
    #    v68 = v30 + v67;
    #    v32 = *(float *)v7 - *(float *)(v6 + 16);
    #    v33 = *(float *)(v6 - 52) - *(float *)(v6 + 20);
    #    v34 = *(float *)(v6 - 48) - *(float *)(v6 + 24);
    #    v35 = *(float *)(v6 - 32) - *(float *)v7;
    #    v36 = *(float *)(v6 - 28) - *(float *)(v6 - 52);
    #    v37 = *(float *)(v6 - 24) - *(float *)(v6 - 48);
    #    v51 = v37 * v33 - v36 * v34;
    #    v55 = v34 * v35 - v37 * v32;
    #    v59 = v36 * v32 - v33 * v35;
    #    v73 = v59 * v59 + v55 * v55 + v51 * v51;
    #   if ( std__numeric_limits_float___min() >= v73 )
    #    {
    #      v38 = v59;
    #    }
    #    else
    #    {
    #      v39 = sqrt(1.0 / v73);
    #      v51 = v51 * v39;
    #      v55 = v55 * v39;
    #      v38 = v39 * v59;
    #    }
    #    v6 += 108;
    #    v40 = v69-- == 1;
    #    v41 = v38 + v68;
    #    v42 = (v51 + v62) * 0.25;
    #    v43 = (v55 + v65) * 0.25;
    #    v44 = v41 * 0.25;
    #    v45 = sqrt(1.0 / (v44 * v44 + v43 * v43 + v42 * v42));
    #    *(float *)(v6 - 68) = v42 * v45;
    #    *(float *)(v6 - 64) = v43 * v45;
    #    *(float *)(v6 - 60) = v44 * v45;
    #    *(float *)(v6 - 68) = -*(float *)(v6 - 68);
    #    *(float *)(v6 - 64) = -*(float *)(v6 - 64);
    #    *(float *)(v6 - 60) = -*(float *)(v6 - 60);
    #  }
    #  while ( !v40 );

    def read_loddef2(self, cf):
        packet = data_packet(cf.r_chunk_data())
        for i in range(8):
            lod_face = universal_dict_object()
            for j in range(4):
                vertex = universal_dict_object()
                vertex.v = packet.unpack("f3", 12)
                vertex.t = packet.unpack("f2", 8)
                (vertex.c_rgb_hemi, vertex.c_sun) = packet.unpack("VC", 5)
                vertex.pad = packet.unpack("C3", 12)
                lod_face.vertices.append(vertex)

            self.lod_faces.append(lod_face)

        self.set_loaded("OGF_LODDEF2")
        if packet.resid() != 0:
            fail("there some data in packet left: " + packet.resid())

    def read_treedef(self):
        pass

    #  IReader__r(v5, (char *)v4 + 132, 64);
    #  IReader__r(v5, (char *)v4 + 196, 16);
    #  IReader__r(v5, (char *)v4 + 212, 16);
    #  *((_DWORD *)v4 + 16) = CShaderManager__CreateGeom(v25, *((_DWORD *)v4 + 17), *((_DWORD *)v4 + 20));
    #  *((_DWORD *)v4 + 24) = sub_599BF0("consts");
    #  *((_DWORD *)v4 + 25) = sub_599BF0("wave");
    #  *((_DWORD *)v4 + 26) = sub_599BF0("wind");
    #  *((_DWORD *)v4 + 27) = sub_599BF0("c_bias");
    #  *((_DWORD *)v4 + 28) = sub_599BF0("c_scale");
    #  *((_DWORD *)v4 + 29) = sub_599BF0("m_m2w");
    #  *((_DWORD *)v4 + 30) = sub_599BF0("m_w2v2p");
    #  *((_DWORD *)v4 + 31) = sub_599BF0("v_eye");

    def read_treedef2(self, cf):
        packet = data_packet(cf.r_chunk_data())
        self.treedef.tree_xform = packet.unpack("f16", 64)
        self.treedef.c_scale = universal_dict_object()
        self.treedef.c_bias = universal_dict_object()
        self.read_ogf_color(self.treedef.c_scale, packet)
        self.read_ogf_color(self.treedef.c_bias, packet)
        self.set_loaded("OGF_TREEDEF2")
        die()
        if packet.resid() != 0:
            fail("there some data in packet left: ".packet.resid())

    def read_ogf_color(self, packet):
        self.rgb = packet.unpack("f3", 12)
        (self.hemi, self.sun) = packet.unpack("ff", 8)

    def read_swicontainer(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (self.ext_swib_index) = packet.unpack("V", 4)

    def write(self, cf, subversion):
        self.subversion = subversion
        self.write_header(cf)

        if self.mt_names[self.ogf_version][self.model_type] == "MT_NORMAL":
            self.write_visual(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_HIERRARHY":
            self.write_hierrarhy_visual(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_PROGRESSIVE":
            self.write_progressive(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_SKELETON_ANIM":
            self.write_kinematics_animated(cf)
        elif (
            self.mt_names[self.ogf_version][self.model_type] == "MT_SKELETON_GEOMDEF_PM"
        ):
            self.write_skeletonx_pm(cf)
        elif (
            self.mt_names[self.ogf_version][self.model_type] == "MT_SKELETON_GEOMDEF_ST"
        ):
            self.write_skeletonx_st(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_PROGRESSIVE2":
            self.write_progressive2(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_LOD":
            self.write_lod(cf)
        elif (
            self.mt_names[self.ogf_version][self.model_type] == "MT_TREE"
            or self.mt_names[self.ogf_version][self.model_type] == "MT_TREE_ST"
        ):
            self.write_tree_visual_st(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_SKELETON_RIGID":
            self.write_kinematics(cf)
        elif self.mt_names[self.ogf_version][self.model_type] == "MT_TREE_PM":
            self.write_tree_visual_pm(cf)
        else:
            fail(f"unexpected model model_type {self.model_type}")

    def write_header(self, cf):
        cf.w_chunk_open(0x1)
        cf.w_chunk_data(pack("CCv", self.ogf_version, self.model_type, self.shader_id))
        if self.ogf_version == 4:
            self.write_bbox(cf)
            self.write_bsphere(cf)

        cf.w_chunk_close()

    def write_render_visual(self, cf):
        if self.ogf_version == 3 and self.check_loaded("OGF_BBOX"):
            cf.w_chunk_open(0x6)
            self.write_bbox(cf)
            cf.w_chunk_close()

        if self.ogf_version == 3 and self.check_loaded("OGF_BSPHERE"):
            cf.w_chunk_open(0xB)
            self.write_bsphere(cf)
            cf.w_chunk_close()

        if self.check_loaded("OGF_S_DESC"):
            self.write_s_desc(cf)

        if self.ogf_version == 3 and self.check_loaded("OGF_TEXTURE_L"):
            self.write_texture_l(cf)

        if self.check_loaded("OGF_TEXTURE"):
            self.write_texture(cf)

    def write_visual(self, cf):
        self.write_render_visual(cf)
        if self.ogf_version == 4 and self.check_loaded("OGF_GCONTAINER"):
            self.write_gcontainer(cf)
            if self.check_loaded("OGF_FASTPATH"):
                self.write_fastpath(cf)

        if self.check_loaded("OGF_VCONTAINER"):
            self.write_vcontainer(cf)
        elif self.check_loaded("OGF_VERTICES"):
            self.write_vertices(cf)

        if self.check_loaded("OGF_ICONTAINER"):
            self.write_icontainer(cf)
        elif self.check_loaded("OGF_INDICES"):
            self.write_indices(cf)

    def write_hierrarhy_visual(self, cf):
        self.write_render_visual(cf)
        if self.check_loaded("OGF_CHILDREN_L"):
            self.write_children_l(cf)
        elif self.check_loaded("OGF_CHILDREN"):
            self.write_children(cf)
        elif self.check_loaded("OGF_CHILD_REFS"):
            self.write_child_refs(cf)

    def write_progressive(self, cf):
        self.write_visual(cf)
        if self.ogf_version == 4:
            self.write_swidata(cf)
        else:
            self.write_loddata(cf)

    def write_kinematics(self, cf):
        self.write_hierrarhy_visual(cf)
        if self.ogf_version == 4:
            if self.check_loaded("OGF_S_LODS_CSKY"):
                self.write_s_lods_csky(cf)
            elif self.check_loaded("OGF_S_LODS"):
                self.write_s_lods(cf)

        if self.check_loaded("OGF_S_USERDATA"):
            self.write_s_userdata(cf)

        if self.check_loaded("OGF_S_BONE_NAMES"):
            self.write_s_bone_names(cf)

        if self.check_loaded("OGF_S_IKDATA_2"):
            self.write_s_ikdata(cf, 2)
        elif self.check_loaded("OGF_S_IKDATA_1"):
            self.write_s_ikdata(cf, 1)

    def write_kinematics_animated(self, cf):
        self.write_kinematics(cf)
        if self.ogf_version == 4 and self.check_loaded("OGF_S_MOTION_REFS_1"):
            self.write_smotion_refs_1(cf)
            return
        if self.check_loaded("OGF_S_MOTION_REFS_0"):
            self.write_smotion_refs_0(cf)
            return
        if self.check_loaded("OGF_S_SMPARAMS_1"):
            self.write_s_smparams(cf, 1)
        elif self.ogf_version == 3 and self.check_loaded("OGF_S_SMPARAMS_0"):
            self.write_s_smparams(cf, 2)

        if self.check_loaded("OGF_S_MOTIONS_1"):
            self.write_smotions(cf, 1)
        elif self.ogf_version == 3 and self.check_loaded("OGF_S_MOTIONS_0"):
            self.write_smotions(cf, 0)
        else:
            fail("no motions to write")

    def write_skeletonx_pm(self, cf):
        self.write_progressive(cf)

    def write_skeletonx_st(self, cf):
        self.write_visual(cf)

    def write_progressive2(self, cf):
        self.write_render_visual(cf)
        self.write_s_lods(cf)

    def write_lod(self, cf):
        self.write_hierrarhy_visual(cf)
        if self.check_loaded("OGF_LODDEF2"):
            self.write_loddef2(cf)

    def write_tree_visual(self, cf):
        self.write_visual(cf)
        self.write_treedef2(cf)

    def write_tree_visual_st(self, cf):
        self.write_tree_visual(cf)

    def write_tree_visual_pm(self, cf):
        self.write_tree_visual(cf)
        self.write_swicontainer(cf)

    def write_bbox(self, cf):
        cf.w_chunk_data(pack("f3f3", self.bbox.min, self.bbox.max))

    def write_bsphere(self, cf):
        cf.w_chunk_data(pack("f3f", self.bsphere.c, self.bsphere.r))

    def write_s_desc(self, cf):
        cf.w_chunk(
            self.chunk_names[self.ogf_version]["OGF_S_DESC"],
            pack(
                "Z*Z*VZ*VZ*V",
                self.ogf_object,
                self.ogf_creator,
                self.unk,
                self.creator,
                self.create_time,
                self.editor,
                self.edit_time,
            ),
        )

    def write_texture_l(self, cf):
        cf.w_chunk(
            self.chunk_names[self.ogf_version]["OGF_TEXTURE_L"],
            pack("VV", self.texture_id, self.shader_id),
        )

    def write_texture(self, cf):
        cf.w_chunk(
            self.chunk_names[self.ogf_version]["OGF_TEXTURE"],
            pack("Z*Z*", self.texture_name, self.shader_name),
        )

    def write_gcontainer(self, cf):
        cf.w_chunk(
            self.chunk_names[self.ogf_version]["OGF_GCONTAINER"],
            pack(
                "VVVVVV",
                self.ext_vb_index,
                self.ext_vb_offset,
                self.ext_vb_size,
                self.ext_ib_index,
                self.ext_ib_offset,
                self.ext_ib_size,
            ),
        )

    def write_fastpath(self, cf):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_FASTPATH"])
        cf.w_chunk(0x15, pack("V6", self.m_fast.gcontainer))
        if self.m_fast.is_swi == 1:
            print("write swi\n")
            self.write_swidata(self.m_fast, cf)

        cf.w_chunk_close()

    # 	cf.w_chunk($chunk_names[self.ogf_version]['OGF_FASTPATH'], $self.m_fast);

    def write_vcontainer(self, cf):
        cf.w_chunk(
            self.chunk_names[self.ogf_version]["OGF_VCONTAINER"],
            pack("VVV", self.ext_vb_index, self.ext_vb_offset, self.ext_vb_size),
        )

    def write_vertices(self, cf):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_VERTICES"])
        cf.w_chunk_data(pack("VV", self.vertex_format, self.vertex_count))
        if self.vertex_format == self.OGF_VERTEXFORMAT_FVF_OLD:
            for vertice in self.vertices:
                cf.w_chunk_data(
                    pack("f3f3f2", vertice.point, vertice.normal, vertice.textcoords),
                )

        elif (
            self.ogf_version == 3 and self.vertex_format == self.OGF_VERTEXFORMAT_FVF_1L
        ):
            for vertice in self.vertices:
                cf.w_chunk_data(
                    pack(
                        "f3f3f2l",
                        vertice.point,
                        vertice.normal,
                        vertice.textcoords,
                        vertice.matrix,
                    ),
                )

        elif (
            self.vertex_format == self.OGF_VERTEXFORMAT_FVF_1L
            or self.vertex_format == self.OGF_VERTEXFORMAT_FVF_1_CS
        ):
            for vertice in self.vertices:
                cf.w_chunk_data(
                    pack(
                        "f3f3f3f3f2l",
                        vertice.point,
                        vertice.normal,
                        vertice.t,
                        vertice.b,
                        vertice.textcoords,
                        vertice.matrix,
                    ),
                )

        elif (
            self.vertex_format == self.OGF_VERTEXFORMAT_FVF_2L
            or self.vertex_format == self.OGF_VERTEXFORMAT_FVF_2_CS
        ):
            for vertice in self.vertices:
                cf.w_chunk_data(
                    pack(
                        "vvf3f3f3f3ff2",
                        vertice.matrix0,
                        vertice.matrix1,
                        vertice.point,
                        vertice.normal,
                        vertice.t,
                        vertice.b,
                        vertice.w,
                        vertice.textcoords,
                    ),
                )

        elif self.vertex_format == self.OGF_VERTEXFORMAT_FVF_3_CS:
            for vertice in self.vertices:
                cf.w_chunk_data(
                    pack(
                        "vvvf3f3f3f3fff2",
                        vertice.matrix0,
                        vertice.matrix1,
                        vertice.matrix2,
                        vertice.point,
                        vertice.normal,
                        vertice.t,
                        vertice.b,
                        vertice.w0,
                        vertice.w1,
                        vertice.textcoords,
                    ),
                )

        elif self.vertex_format == self.OGF_VERTEXFORMAT_FVF_4_CS:
            for vertice in self.vertices:
                cf.w_chunk_data(
                    pack(
                        "vvvvf3f3f3f3ffff2",
                        vertice.matrix0,
                        vertice.matrix1,
                        vertice.matrix2,
                        vertice.matrix3,
                        vertice.point,
                        vertice.normal,
                        vertice.t,
                        vertice.b,
                        vertice.w0,
                        vertice.w1,
                        vertice.w2,
                        vertice.textcoords,
                    ),
                )

        cf.w_chunk_close()

    def write_icontainer(self, cf):
        cf.w_chunk(
            self.chunk_names[self.ogf_version]["OGF_ICONTAINER"],
            pack("VVV", self.ext_ib_index, self.ext_ib_offset, self.ext_ib_size),
        )

    def write_indices(self, cf):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_INDICES"])
        cf.w_chunk_data(pack("V", self.indices_count))
        for index in self.indices:
            cf.w_chunk_data(pack("v", index))

        cf.w_chunk_close()

    def write_children_l(self, cf):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_CHILDREN_L"])
        cf.w_chunk_data(pack("V", len(self.children_l)))
        for child in self.children_l:
            cf.w_chunk_data(pack("V", child))

        cf.w_chunk_close()

    def write_children(self, cf):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_CHILDREN"])
        id = 0
        for child in self.children:
            cf.w_chunk_open(id)
            child.write(cf)
            cf.w_chunk_close()
            id += 1

        cf.w_chunk_close()

    def write_child_refs(self, cf):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_CHILD_REFS"])
        cf.w_chunk_data(pack("V", len(self.children_l)))
        for child in self.child_refs:
            cf.w_chunk_data(pack("Z*", child))

        cf.w_chunk_close()

    def write_swidata(self, cf):
        cf.w_chunk_open(0x6)  # временный  хак, замените меня
        cf.w_chunk_data(pack("V4V", self.swi.reserved, (len(self.swi.data) - 1) + 1))
        for swi in self.swi.data:
            cf.w_chunk_data(pack("lvv", swi.offset, swi.num_tris, swi.num_verts))

        cf.w_chunk_close()

    def write_loddata(self, cf):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_LODDATA"])
        for lod in self.loddata:
            self.write_hoppe_header(lod, cf)
            self.write_hoppe_vertsplits(lod, cf)
            self.write_hoppe_fix_faces(lod, cf)

        cf.w_chunk_close()

    def write_hoppe_header(self, cf):
        cf.w_chunk(
            self.OGF3_HOPPE_HEADER,
            pack("VV", self.min_vertices, self.max_vertices),
        )

    def write_hoppe_vertsplits(self, cf):
        cf.w_chunk_open(self.OGF3_HOPPE_VERT_SPLITS)
        for vertsplit in self.vertsplits:
            cf.w_chunk_data(
                pack("vCC", vertsplit.vert, vertsplit.num_tris, vertsplit.num_verts),
            )

        cf.w_chunk_close()

    def write_hoppe_fix_faces(self, cf):
        cf.w_chunk_open(self.OGF3_HOPPE_FIX_FACES)
        cf.w_chunk_data(pack("V", self.num_fix_faces))
        cf.w_chunk_data(pack(f"(v){self.num_fix_faces}", self.fix_faces))
        cf.w_chunk_close()

    def write_s_lods_csky(self, cf):
        cf.w_chunk(
            self.chunk_names[self.ogf_version]["OGF_S_LODS"],
            substr(pack("Z*", self.s_lods_ref), 0, -1),
        )

    def write_s_lods(self, cf):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_S_LODS"])
        id = 0
        for lod in self.s_lods:
            cf.w_chunk_open(id)
            lod.write(cf)
            cf.w_chunk_close()
            id += 1

        cf.w_chunk_close()

    def write_s_userdata(self, cf):
        len = length(self.userdata)
        cf.w_chunk(
            self.chunk_names[self.ogf_version]["OGF_S_USERDATA"],
            pack(f"a{len}", self.userdata),
        )

    def write_s_bone_names(self, cf):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_S_BONE_NAMES"])
        cf.w_chunk_data(pack("V", (len(self.bone_names) - 1) + 1))
        for bone_name_obj in self.bone_names:
            cf.w_chunk_data(pack("Z*Z*", bone_name_obj.name, bone_name_obj.parent_name))
            self.write_obb(bone_name_obj, cf)

        cf.w_chunk_close()

    def write_obb(self, cf):
        cf.w_chunk_data(pack("f9f3f3", self.rotate, self.translate, self.halfsize))

    def write_sphere(*args):
        self = args[0]
        args[1].w_chunk_data(pack("f3f", self.p, self.r))

    def write_cylinder(*args):
        self = args[0]
        args[1].w_chunk_data(
            pack("f3f3ff", self.center, self.direction, self.height, self.radius),
        )

    def write_s_ikdata(self, cf, mode):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_S_IKDATA_" + mode])
        for ik in self.ik_data:
            if mode == 2:
                cf.w_chunk_data(pack("VZ*", ik.version, ik.game_mtl_name))
            else:
                cf.w_chunk_data(pack("Z*", ik.game_mtl_name))

            self.write_s_bone_shape(ik.bone_shape, cf)
            self.write_s_joint_ik_data(ik.joint_data, cf)
            if mode > 0:
                cf.w_chunk_data(pack("f3f3", ik.bind_rotation, ik.bind_position))

            cf.w_chunk_data(pack("ff3", ik.mass, ik.center_of_mass))

        cf.w_chunk_close()

    def write_s_bone_shape(*args):
        self = args[0]
        args[1].w_chunk_data(pack("vv", self.type, self.flags))
        self.write_obb(self.box, args[1])
        self.write_sphere(self.sphere, args[1])
        self.write_cylinder(self.cylinder, args[1])

    def write_s_joint_ik_data(*args):
        self = args[0]
        args[1].w_chunk_data(pack("V", self.type))
        self.write_s_joint_limit(self.limits[0], args[1])
        self.write_s_joint_limit(self.limits[1], args[1])
        self.write_s_joint_limit(self.limits[2], args[1])
        args[1].w_chunk_data(
            pack(
                "ffVff",
                self.spring_factor,
                self.damping_factor,
                self.ik_flags,
                self.break_force,
                self.break_torque,
            ),
        )
        if self.friction is not None:
            args[1].w_chunk_data(pack("f", self.friction))

    def write_s_joint_limit(*args):
        self = args[0]
        args[1].w_chunk_data(
            pack("f2ff", self.limit, self.spring_factor, self.damping_factor),
        )

    def write_smotion_refs_1(self, cf):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_S_MOTION_REFS_1"])
        cf.w_chunk_data(pack("V", (len(self.motion_refs_1) - 1) + 1))
        for ref in self.motion_refs_1:
            cf.w_chunk_data(pack("Z*", ref))

        cf.w_chunk_close()

    def write_smotion_refs_0(self, cf):
        cf.w_chunk(
            self.chunk_names[self.ogf_version]["OGF_S_MOTION_REFS_0"],
            pack("Z*", self.motion_refs_0),
        )

    def write_s_smparams(self, cf, mode):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_S_SMPARAMS_" + mode])
        cf.w_chunk_data(
            pack(
                "vv",
                self.sm_params_version,
                (len(self.s_smparams_partitions) - 1) + 1,
            ),
        )
        for part in self.s_smparams_partitions:
            cf.w_chunk_data(pack("Z*v", part.name, part.bone_count))
            for bone in part.bones:
                if mode == 0 or self.sm_params_version == 1:
                    cf.w_chunk_data(pack("V", bone.bone_id))
                elif self.sm_params_version == 2:
                    cf.w_chunk_data(pack("Z*", bone.bone_name))
                elif self.sm_params_version == 3 or self.sm_params_version == 4:
                    cf.w_chunk_data(pack("Z*V", bone.bone_name, bone.bone_id))

        cf.w_chunk_data(pack("v", (len(self.s_smparams_motions) - 1) + 1))
        for mot in self.s_smparams_motions:
            if mode == 1:
                cf.w_chunk_data(pack("Z*V", mot.name, mot.flags))
                self.write_motion_def(mot, cf)
                if self.sm_params_version == 4:
                    cf.w_chunk_data(pack("V", (len(mot.mmarks) - 1) + 1))
                    for nmark in mot.mmarks:
                        self.write_motion_mark(nmark, cf)

            else:
                flag = 0
                if mot.flags & 0x2:
                    mot.flags -= 0x2
                    flag = 1

                cf.w_chunk_data(pack("Z*C", mot.name, mot.flags))
                self.write_motion_def(mot, cf)
                cf.w_chunk_data(pack("C", flag))

        cf.w_chunk_close()

    def write_motion_def(self, cf):
        cf.w_chunk_data(
            pack(
                "vvffff",
                self.bone_or_part,
                self.motion,
                self.speed,
                self.power,
                self.accrue,
                self.falloff,
            ),
        )

    def write_motion_mark(self, cf):
        len = length(self.name)
        cf.w_chunk_data(pack(f"(a){len}", self.name))
        cf.w_chunk_data(pack("V", (len(self.intervals) - 1) + 1))
        for int in self.intervals:
            cf.w_chunk_data(pack("ff", int.min, int.max))

    def write_smotions(self, cf, mode):

        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_S_MOTIONS_" + mode])
        cf.w_chunk_open(0)
        cf.w_chunk_data(pack("V", self.motions_count))
        cf.w_chunk_close()
        id = 1
        for motion in self.motions:
            cf.w_chunk_open(id)
            id += 1
            self.write_motion(motion, cf, mode)
            cf.w_chunk_close()

        cf.w_chunk_close()

    def write_motion(self, cf, mode):
        cf.w_chunk_data(pack("Z*V", self.name, self.keys_count))
        if self.keys_count == 0:
            return

        if mode == 1:
            for bone in self.bones:
                cf.w_chunk_data(pack("C", bone.flags))
                if bone.flags & self.KPF_R_ABSENT:
                    cf.w_chunk_data(pack("s4", bone.keysr))
                else:
                    cf.w_chunk_data(
                        pack(f"V(s4){self.keys_count}", bone.crc_keysr, bone.keysr),
                    )

                if bone.flags & self.KPF_T_PRESENT:
                    cf.w_chunk_data(pack("V", bone.crc_keyst))
                    if bone.flags & self.KPF_T_HQ:
                        for j in range(self.keys_count):
                            cf.w_chunk_data(pack("s3", bone.keyst[j * 3 : j * 3 + 2]))

                    else:
                        for j in range(self.keys_count):
                            cf.w_chunk_data(pack("c3", bone.keyst[j * 3 : j * 3 + 2]))

                    cf.w_chunk_data(pack("f3", bone.sizet))

                cf.w_chunk_data(pack("f3", bone.initt))

        else:
            for bone in self.bones:
                for n in range(self.keys_count):
                    cf.w_chunk_data(pack("s4f3", bone.keys[n * 7 : n * 7 + 6]))

    def write_loddef2(self, cf):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_LODDEF2"])
        for lod_face in self.lod_faces:
            for vertex in lod_face.vertices:
                cf.w_chunk_data(
                    pack(
                        "f3f2VCC3",
                        vertex.v,
                        vertex.t,
                        vertex.c_rgb_hemi,
                        vertex.c_sun,
                        vertex.pad,
                    ),
                )

        cf.w_chunk_close()

    def write_treedef2(self, cf):
        cf.w_chunk_open(self.chunk_names[self.ogf_version]["OGF_TREEDEF2"])
        cf.w_chunk_data(pack("f16", self.tree_xform))
        self.write_ogf_color(self.c_scale, cf)
        self.write_ogf_color(self.c_bias, cf)
        cf.w_chunk_close()

    def write_ogf_color(self, cf):
        cf.w_chunk_data(pack("f3ff", self.rgb, self.hemi, self.sun))

    def write_swicontainer(self, cf):
        cf.w_chunk(
            self.chunk_names[self.ogf_version]["OGF_SWICONTAINER"],
            pack("V", self.ext_swib_index),
        )

    def set_loaded(self, chunk):
        self.loaded_chunks += self.chunks_loaded[self.ogf_version][chunk]

    def list_chunks(self):
        values = []
        for chunk in self.chunks_loaded[self.ogf_version].keys():
            if self.loaded_chunks & self.chunks_loaded[self.ogf_version][chunk]:
                values.append(chunk)

        return values

    def check_loaded(self, chunk):
        return self.loaded_chunks & self.chunks_loaded[self.ogf_version][chunk]

    def check_unhandled_chunks(self, cf):
        rev_names = reversed(self.chunk_names[self.ogf_version])
        cf.seek(0)
        while 1:
            (index, size) = cf.r_chunk_open()
            if not (index is not None):
                break
            if index == 0 and size == 0:
                break
            cf.r_chunk_close()
            if not (self.check_loaded(rev_names[index])):
                name = rev_names[index]
                if name:
                    fail(f"chunk {name} is unhandled")
                else:
                    fail(f"chunk {index} is unhandled")
