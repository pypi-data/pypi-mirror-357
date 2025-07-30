# Module for handling level stalker files
# Update history:
# 	27/08/2012 - fix code for new fail() syntax
##################################################
import os
import re

from stkutils.binary_data import pack
from stkutils.chunked import chunked
from stkutils.data_packet import data_packet
from stkutils.file.ogf import ogf
from stkutils.ini_file import ini_file
from stkutils.level.level_cform import level_cform
from stkutils.perl_utils import fail, length, ref, uc, universal_dict_object


class level:
    # use strict;
    # use Cwd;
    # use chunked;
    # use level.level_cform;
    # use debug qw(fail);
    # use vars qw(@ISA @EXPORT_OK);
    # require Exporter;

    # @ISA		= qw(Exporter);
    # @EXPORT_OK	= qw(import_data export_data);
    def __init__(self, data=""):
        # my $class = shift;
        # my self = universal_dict_object();
        self.data = data
        # bless(self, $class);
        return self

    def version(*args, **kwargs):
        if len(args) == 2:
            args[0].fsl_header.xrlc_version = args[1]
        return args[0].fsl_header.xrlc_version

    def init_data_fields(self, *args, **kwargs):
        # my self = shift;
        self.fsl_header.xrlc_version = args[0]
        self.fsl_portals = fsl_portals(args[0])
        self.fsl_light_dynamic = fsl_light_dynamic(args[0])
        self.fsl_glows = fsl_glows(args[0])
        self.fsl_visuals = fsl_visuals(args[0])
        if os.path.exists("FSL_VB.bin") or os.path.exists("FSL_VB.ltx"):
            self.fsl_vertex_buffer = fsl_vertex_buffer(args[0])
        self.fsl_shaders = fsl_shaders(args[0])
        self.fsl_sectors = fsl_sectors(args[0])
        self.compressed = compressed(args[0])
        if args[0] > 8:
            if os.path.exists("FSL_IB.bin") or os.path.exists("FSL_IB.ltx"):
                self.fsl_index_buffer = fsl_index_buffer(args[0])

        if args[0] < 8:
            self.fsl_light_key_frames = fsl_light_key_frames(args[0])
            self.fsl_textures = fsl_textures(args[0])

        if args[0] == 9:
            self.fsl_shader_constant = fsl_shader_constant(args[0])

        if args[0] > 11:
            if os.path.exists("FSL_SWIS.bin") or os.path.exists("FSL_SWIS .ltx"):
                self.fsl_swis = fsl_swis(args[0])
        elif os.path.exists("FSL_CFORM.bin") or os.path.exists("FSL_CFORM.ltx"):
            self.fsl_cform = level_cform(args[0])

    def read(self, fh=None):
        # my self = shift;
        # my ($fh) = @_;
        need_close = False
        if fh is None:
            fh = chunked(self.data, "data")  # or fail("$!\n");
            need_close = True

        while 1:
            (index, size) = fh.r_chunk_open()
            if index is None:
                break
            # ($index is not None) or break;
            data = fh.r_chunk_data()

            if index == 0x1:
                self.fsl_header = fsl_header(data)
                self.fsl_header.decompile()
                self.compressed = compressed(self.fsl_header.xrlc_version)

            elif chunks.get_name(index, self.fsl_header.xrlc_version) == "FSL_CFORM":
                self.fsl_cform = level_cform(self.fsl_header.xrlc_version, data)

            elif chunks.get_name(index, self.fsl_header.xrlc_version) == "FSL_PORTALS":
                self.fsl_portals = fsl_portals(self.fsl_header.xrlc_version, data)

            elif (
                chunks.get_name(index, self.fsl_header.xrlc_version)
                == "FSL_SHADER_CONSTANT"
            ):
                self.fsl_shader_constant = fsl_shader_constant(
                    self.fsl_header.xrlc_version,
                    data,
                )

            elif (
                chunks.get_name(index, self.fsl_header.xrlc_version)
                == "FSL_LIGHT_DYNAMIC"
            ):
                self.fsl_light_dynamic = fsl_light_dynamic(
                    self.fsl_header.xrlc_version,
                    data,
                )

            elif (
                chunks.get_name(index, self.fsl_header.xrlc_version)
                == "FSL_LIGHT_KEY_FRAMES"
            ):
                self.fsl_light_key_frames = fsl_light_key_frames(
                    self.fsl_header.xrlc_version,
                    data,
                )

            elif chunks.get_name(index, self.fsl_header.xrlc_version) == "FSL_GLOWS":
                self.fsl_glows = fsl_glows(self.fsl_header.xrlc_version, data)

            elif chunks.get_name(index, self.fsl_header.xrlc_version) == "FSL_VISUALS":
                self.fsl_visuals = fsl_visuals(self.fsl_header.xrlc_version, data)

            elif chunks.get_name(index, self.fsl_header.xrlc_version) == "FSL_VB":
                self.fsl_vertex_buffer = fsl_vertex_buffer(
                    self.fsl_header.xrlc_version,
                    data,
                )

            elif chunks.get_name(index, self.fsl_header.xrlc_version) == "FSL_SWIS":
                self.fsl_swis = fsl_swis(self.fsl_header.xrlc_version, data)

            elif chunks.get_name(index, self.fsl_header.xrlc_version) == "FSL_IB":
                self.fsl_index_buffer = fsl_index_buffer(
                    self.fsl_header.xrlc_version,
                    data,
                )

            elif chunks.get_name(index, self.fsl_header.xrlc_version) == "FSL_TEXTURES":
                self.fsl_textures = fsl_textures(self.fsl_header.xrlc_version, data)

            elif chunks.get_name(index, self.fsl_header.xrlc_version) == "FSL_SHADERS":
                self.fsl_shaders = fsl_shaders(self.fsl_header.xrlc_version, data)

            elif chunks.get_name(index, self.fsl_header.xrlc_version) == "FSL_SECTORS":
                self.fsl_sectors = fsl_sectors(self.fsl_header.xrlc_version, data)

            elif index & 0x80000000:
                index -= 0x80000000
                self.compressed.add(index, data)

            else:
                fail(f"unexpected chunk {index} size {size}\n")
            # }
            fh.r_chunk_close()
        if need_close:
            fh.close()  # if ($#_ == -1);

    def copy(self, copy):
        copy.fsl_header = self.fsl_header
        copy.fsl_portals = self.fsl_portals
        copy.fsl_light_dynamic = self.fsl_light_dynamic
        copy.fsl_glows = self.fsl_glows
        copy.fsl_visuals = self.fsl_visuals
        copy.fsl_shaders = self.fsl_shaders
        copy.fsl_sectors = self.fsl_sectors

    def write(self, fh=None):
        need_close = False
        if fh is None:
            fh = chunked("", "data")  # or fail("$!\n");
            need_close = True

        ver = self.fsl_header.xrlc_version
        self.fsl_header.write(fh)
        if ver < 10:
            if self.fsl_cform.data is not None:
                self.fsl_cform.write(fh)
            elif self.compressed["FSL_CFORM"] is not None:
                self.compressed.write(
                    chunks.get_index("FSL_CFORM", self.fsl_header.xrlc_version),
                    fh,
                )
            else:
                fail("cant find FSL_CFORM")

            self.fsl_portals.write(fh)
        elif ver == 10:
            self.fsl_portals.write(fh)
            if self.fsl_cform.data is not None:
                self.fsl_cform.write(fh)
            elif self.compressed["FSL_CFORM"] is not None:
                self.compressed.write(
                    chunks.get_index("FSL_CFORM", self.fsl_header.xrlc_version),
                    fh,
                )
            else:
                fail("cant find FSL_CFORM")

        else:
            self.fsl_portals.write(fh)

        if ver == 9:
            self.fsl_shader_constant.write(fh)

        self.fsl_light_dynamic.write(fh)
        if ver < 8:
            self.fsl_light_key_frames.write(fh)

        self.fsl_glows.write(fh)
        if self.fsl_visuals.data is not None:
            self.fsl_visuals.write(fh)
        elif self.compressed["FSL_VISUALS"] is not None:
            self.compressed.write(
                chunks.get_index("FSL_VISUALS", self.fsl_header.xrlc_version),
                fh,
            )
        else:
            fail("cant find FSL_VISUALS")

        if ver < 13:
            if self.fsl_vertex_buffer.data is not None:
                self.fsl_vertex_buffer.write(fh)
            elif (
                chunks.get_index("FSL_VB", self.fsl_header.xrlc_version)
                and (self.compressed is not None)["FSL_VB"]
            ):
                self.compressed.write(
                    chunks.get_index("FSL_VB", self.fsl_header.xrlc_version),
                    fh,
                )
            else:
                fail("cant find FSL_VB")

            if ver > 11:
                if self.fsl_swis.data is not None:
                    self.fsl_swis.write(fh)
                elif self.compressed["FSL_SWIS"] is not None:
                    self.compressed.write("FSL_SWIS", fh)

            if ver > 8:
                if self.fsl_index_buffer.data is not None:
                    self.fsl_index_buffer.write(fh)
                elif (
                    chunks.get_index("FSL_IB", self.fsl_header.xrlc_version)
                    and (self.compressed is not None)["FSL_IB"]
                ):
                    self.compressed.write(
                        chunks.get_index("FSL_IB", self.fsl_header.xrlc_version),
                        fh,
                    )
                else:
                    fail("cant find FSL_IB")

        if ver < 8:
            self.fsl_textures.write(fh)
        self.fsl_shaders.write(fh)
        if self.fsl_sectors.data is not None:
            self.fsl_sectors.write(fh)
        elif self.compressed["FSL_SECTORS"] is not None:
            self.compressed.write(
                chunks.get_index("FSL_SECTORS", self.fsl_header.xrlc_version),
                fh,
            )
        else:
            fail("cant find FSL_SECTORS")

        if need_close:
            self.data = fh.data()
            fh.close()

    def my_import(self):
        # my self = shift;
        self.fsl_header = fsl_header()
        self.fsl_header.import_ltx()
        self.init_data_fields(self.fsl_header.xrlc_version)
        if self.fsl_cform.data is not None:
            self.import_data(self.fsl_cform)
        if self.fsl_portals.data is not None:
            self.import_data(self.fsl_portals)
        if self.fsl_shader_constant.data is not None:
            self.import_data(self.fsl_shader_constant)
        self.import_data(self.fsl_light_dynamic)
        if self.fsl_light_key_frames.data is not None:
            self.import_data(self.fsl_light_key_frames)
        self.import_data(self.fsl_glows)
        if self.fsl_visuals.data is not None:
            self.import_data(self.fsl_visuals)
        if self.fsl_vertex_buffer.data is not None:
            self.import_data(self.fsl_vertex_buffer)
        if self.fsl_swis.data is not None:
            self.import_data(self.fsl_swis)
        if self.fsl_index_buffer.data is not None:
            self.import_data(self.fsl_index_buffer)
        if self.fsl_textures.data is not None:
            self.import_data(self.fsl_textures)
        self.import_data(self.fsl_shaders)
        if self.fsl_sectors.data is not None:
            self.import_data(self.fsl_sectors)
        if self.compressed is not None:
            self.import_compressed(self.compressed)

    def export(self):
        # my self = shift;
        self.export_data(self.fsl_header, "ltx")
        if self.fsl_cform.data is not None:
            self.export_data(self.fsl_cform)
        if self.fsl_portals.data is not None:
            self.export_data(self.fsl_portals)
        if self.fsl_shader_constant.data is not None:
            self.export_data(self.fsl_shader_constant)
        self.export_data(self.fsl_light_dynamic)
        if self.fsl_light_key_frames.data is not None:
            self.export_data(self.fsl_light_key_frames)
        self.export_data(self.fsl_glows)
        if self.fsl_visuals.data is not None:
            self.export_data(self.fsl_visuals)
        if self.fsl_vertex_buffer.data is not None:
            self.export_data(self.fsl_vertex_buffer)
        if self.fsl_swis.data is not None:
            self.export_data(self.fsl_swis)
        if self.fsl_index_buffer.data is not None:
            self.export_data(self.fsl_index_buffer)
        if self.fsl_textures.data is not None:
            self.export_data(self.fsl_textures)
        self.export_data(self.fsl_shaders)
        if self.fsl_sectors.data is not None:
            self.export_data(self.fsl_sectors)
        if self.compressed is not None:
            for chunk in self.compressed.keys():
                self.compressed.export(chunk)

    def export_data(self, mode):
        # my (self, mode) = @_;

        # my $ref = ref(self);
        if mode is not None:
            if mode == "bin":
                self.export_bin(self)
            elif mode == "ltx":
                self.export_ltx()
            else:
                fail("Unsupported mode. Use only bin or ltx")

        else:
            self.export_bin(self)

    def export_bin(self):
        # my (self) = @_;

        _ref = ref(self)
        if rm := re.match(r"(level)_(\w+)", _ref):
            rm2 = rm[2]
            _ref = "FSL_" + rm2

        fh = open(uc(_ref) + ".bin", "wb")
        fh.write(self.data)
        fh.close()

    def import_data(self, mode):
        # my (self, mode) = @_;

        _ref = ref(self)
        if mode is not None:
            if mode == "bin":
                self.import_bin(self)
            elif mode == "ltx":
                self.import_ltx()
            else:
                fail("Unsupported mode. Use only bin or ltx")

        else:
            if rm := re.match(r"(level)_(\w+)", _ref):
                rm2 = rm[2]
                _ref = "FSL_" + rm2

            if os.path.exists(ref + ".ltx"):
                self.import_ltx()
            elif os.path.exists(ref + ".bin"):
                self.import_bin(self)
            else:
                fail("There is no " + ref(self) + ".ltx or " + ref(self) + ".bin")

    def import_bin(self):
        _ref = ref(self)
        if rm := re.match(r"(level)_(\w+)", _ref):
            rm2 = rm[2]
            _ref = "FSL_" + rm2
        fh = open(_ref + ".bin", "rb")  # or fail(ref(self).".bin: $!\n");
        # binmode $fh;
        data = ""
        data = fh.read()
        fh.close()
        self.data = data

    def import_compressed(self):
        # my (self) = @_;
        # my @comp_list = glob "{COMPRESSED}*.bin";
        comp_list = []
        for file in comp_list:
            self._import(file)

    def new_fsl_portals(*args, **kwargs):
        return fsl_portals(*args, **kwargs)

    def new_fsl_light_dynamic(*args, **kwargs):
        return fsl_light_dynamic(*args, **kwargs)

    def new_fsl_glows(*args, **kwargs):
        return fsl_glows(*args, **kwargs)

    def new_fsl_visuals(*args, **kwargs):
        return fsl_visuals(*args, **kwargs)

    def new_fsl_vertex_buffer(*args, **kwargs):
        return fsl_vertex_buffer(*args, **kwargs)

    def new_fsl_swis(*args, **kwargs):
        return fsl_swis(*args, **kwargs)

    def new_fsl_index_buffer(*args, **kwargs):
        return fsl_index_buffer(*args, **kwargs)

    def new_fsl_shaders(*args, **kwargs):
        return fsl_shaders(*args, **kwargs)

    def new_fsl_sectors(*args, **kwargs):
        return fsl_sectors(*args, **kwargs)


############################################################
class fsl_header:
    # use strict;
    # use ini_file;
    # use debug qw(fail);
    # use data_packet;
    def __init__(self, data=""):
        # my $class = shift;
        # my self = universal_dict_object();
        self.data = data

    # 	bless(self, $class);
    # 	return self;
    # }
    def decompile(self, *args, **kwargs):
        # my self = shift;
        packet = data_packet(self.data)
        (self.xrlc_version, self.xrlc_quality) = packet.unpack("vv", 4)
        if self.xrlc_version < 11:
            (self.name,) = packet.unpack("Z*")
        elif packet.resid() == 0:
            fail("there is some data left [" + packet.resid() + "] in FSL_HEADER")

    def compile(self):
        if self.xrlc_version > 10:
            data = pack("vv", self.xrlc_version, self.xrlc_quality)
        else:
            l = length(self.name)
            zc = 123 - l
            data = pack("vvZ*", self.xrlc_version, self.xrlc_quality, self.name)
            for i in range(zc):
                data += pack("C", 0)

        self.data = data

    def write(self, fh):
        fh.w_chunk(1, self.data)

    def export_ltx(self):
        fh = open(
            "FSL_HEADER.ltx",
            "w",
            encoding="cp1251",
        )  # or fail("FSL_HEADER.ltx: $!\n");
        fh.write("[header]\n")
        fh.write("xrLC version = self.xrlc_version\n")
        fh.write("xrLC quality = self.xrlc_quality\n")
        if self.xrlc_version < 11:
            fh.write("name = self.name\n")
        fh.close()

    def import_ltx(self):
        fh = ini_file("FSL_HEADER.ltx", "r")  # or fail("FSL_HEADER.ltx: $!\n");
        self.xrlc_version = fh.value("header", "xrLC version")
        self.xrlc_quality = fh.value("header", "xrLC quality")
        if self.xrlc_version < 11:
            self.name = fh.value("header", "name")
        fh.close()


#########################################################
class fsl_portals:
    # use strict;
    # use ini_file;
    # use debug qw(fail);
    # use data_packet;
    def __init__(self, data=""):
        # my $class = shift;
        # my self = universal_dict_object();
        # self.version = args[0];
        self.data = data  # (args[1] or '');

    # bless(self, $class);
    # return self;
    # }
    def decompile(self, mode):
        # my self = shift;
        # my mode = args[0];
        packet = data_packet(self.data)
        if packet.resid() != 0:
            return
        self.portal_count = packet.resid() / 0x50
        if mode and (mode == "full"):
            for i in range(self.portal_count):
                portal = universal_dict_object()
                (portal.sector_front, portal.sector_back) = packet.unpack("vv", 4)
                if self.version >= 8:
                    for j in range(6):
                        point = packet.unpack("f3", 12)
                        portal.vertices.append(point)

                    (portal.count,) = packet.unpack("V", 4)
                else:
                    (portal.count) = packet.unpack("V", 4)
                    for j in range(6):
                        point = packet.unpack("f3", 12)
                        portal.vertices.append(point)

                self.portals.append(portal)
            if packet.resid() == 0:
                fail("there is some data left in packet [" + packet.resid() + "]")

    def compile(self):
        data = ""
        if self.version >= 8:
            for portal in self.portals:
                data += pack("vv", portal.sector_front, portal.sector_back)
                for vertex in portal.vertices:
                    data += pack("f3", vertex)

                data += pack("V", portal.count)

        else:
            for portal in self.portals:
                data += pack("vv", portal.sector_front, portal.sector_back)
                data += pack("V", portal.count)
                for vertex in portal.vertices:
                    data += pack("f3", vertex)

        self.data = data

    def write(self, fh):
        index = chunks.get_index("FSL_PORTALS", self.version)
        fh.w_chunk(index, self.data)

    def export_ltx(self):
        fh = open(
            "FSL_PORTALS.ltx",
            "w",
            encoding="cp1251",
        )  # or fail("FSL_PORTALS.ltx: $!\n");

        for i, portal in enumerate(self.portals):
            fh.write("[i]\n")
            fh.write(f"sector_front = {portal.sector_front}\n")
            fh.write(f"sector_back = {portal.sector_back}\n")
            fh.write("vertex0 = %f,%f,%f\n" % (portal.vertices[0:2]))
            fh.write("vertex1 = %f,%f,%f\n" % (portal.vertices[3:5]))
            fh.write("vertex2 = %f,%f,%f\n" % (portal.vertices[6:8]))
            fh.write("vertex3 = %f,%f,%f\n" % (portal.vertices[9:11]))
            fh.write("vertex4 = %f,%f,%f\n" % (portal.vertices[12:14]))
            fh.write("vertex5 = %f,%f,%f\n" % (portal.vertices[15:17]))
            fh.write(f"count = {portal.count}\n\n")

        fh.close()

    def import_ltx(self):
        fh = ini_file("FSL_PORTALS.ltx", "r")  # or fail("FSL_PORTALS.ltx: $!\n");
        len = len(fh.sections_list)
        for i in range(len):
            portal = universal_dict_object()
            portal.sector_front = fh.value(i, "sector_front")
            portal.sector_back = fh.value(i, "sector_back")
            portal.count = fh.value(i, "count")
            portal.vertices[0:2] = re.split(r",\s*", fh.value(i, "vertex0"))
            portal.vertices[3:5] = re.split(r",\s*", fh.value(i, "vertex1"))
            portal.vertices[6:8] = re.split(r",\s*", fh.value(i, "vertex2"))
            portal.vertices[9:11] = re.split(r",\s*", fh.value(i, "vertex3"))
            portal.vertices[12:14] = re.split(r",\s*", fh.value(i, "vertex4"))
            portal.vertices[15:17] = re.split(r",\s*", fh.value(i, "vertex5"))
            self.portals.append(portal)

        fh.close()


#########################################################
class fsl_shader_constant:
    # use strict;
    # use debug qw(fail);
    # use ini_file;
    # use data_packet;
    def __init__(self, version, data=""):
        # my $class = shift;
        # my self = universal_dict_object();
        self.version = version  # args[0];
        self.data = data  # (args[1] or '');

    # 	bless(self, $class);
    # 	return self;
    # }
    def decompile(self, *args, **kwargs):
        # my self = shift;
        packet = data_packet(self.data)
        print("decompiling of FSL_SHADER_CONSTANT not implemented yet\n")

    def compile(self):
        data = ""
        print("compiling of FSL_SHADER_CONSTANT not implemented yet\n")
        self.data = data

    def write(self, fh):
        # my self = shift;
        # my ($fh) = @_;
        index = chunks.get_index("FSL_SHADER_CONSTANT", self.version)
        fh.w_chunk(index, self.data)

    def export_ltx(self):
        # my self = shift;

        fh = open(
            "FSL_SHADER_CONSTANT.ltx",
            "w",
            encoding="cp1251",
        )  # or fail("FSL_SHADER_CONSTANT.ltx: $!\n");
        print("exporting decompiled data of FSL_SHADER_CONSTANT not implemented yet\n")
        fh.close()

    def import_ltx(self):
        fh = ini_file(
            "FSL_SHADER_CONSTANT.ltx",
            "r",
        )  # or fail("FSL_SHADER_CONSTANT.ltx: $!\n");
        print("importing decompiled data of FSL_SHADER_CONSTANT not implemented yet\n")
        fh.close()


#########################################################
class fsl_light_dynamic:
    # use strict;
    # use ini_file;
    # use data_packet;
    # use debug qw(fail);
    lt_names = {
        1: "point",
        2: "spot",
        3: "directional",
    }

    reverse_lt_names = {
        "point": 1,
        "spot": 2,
        "directional": 3,
    }

    def __init__(self, version, data=""):
        self.version = version
        self.data = data

    def decompile(self):
        packet = data_packet(self.data)
        if self.version > 8:
            self.count = packet.resid() / 0x6C
            if packet.resid() % 108 != 0:
                fail("wrong size of FSL_LIGHT_DYNAMIC")
            for i in range(self.count):
                light = universal_dict_object()
                (light.controller_id, light.type) = packet.unpack("VV", 8)
                light.diffuse = packet.unpack("f4", 16)
                light.specular = packet.unpack("f4", 16)
                light.ambient = packet.unpack("f4", 16)
                light.position = packet.unpack("f3", 12)
                light.direction = packet.unpack("f3", 12)
                light.other = packet.unpack("f7", 28)
                self.lights.append(light)

        elif self.version > 5:
            self.count = packet.resid() / 0xB0
            if packet.resid() % 176 != 0:
                fail("wrong size of FSL_LIGHT_DYNAMIC")
            for i in range(self.count):
                light = universal_dict_object()
                (light.type) = packet.unpack("V", 4)
                light.diffuse = packet.unpack("f4", 16)
                light.specular = packet.unpack("f4", 16)
                light.ambient = packet.unpack("f4", 16)
                light.position = packet.unpack("f3", 12)
                light.direction = packet.unpack("f3", 12)
                light.other = packet.unpack("f7", 28)
                (light.unk1, light.unk2, light.name) = packet.unpack("VVZ*")
                l = 63 - len(light.name)
                light.garb = packet.unpack(f"C{l}")
                self.lights.append(light)

        else:
            self.fsl_light_dynamic.count = packet.resid() / 0x7C
            if packet.resid() % 124 != 0:
                fail("wrong size of FSL_LIGHT_DYNAMIC")
            for i in range(self.fsl_light_dynamic.count):
                light = universal_dict_object()
                (light.type) = packet.unpack("V", 4)
                light.diffuse = packet.unpack("f4", 16)
                light.specular = packet.unpack("f4", 16)
                light.ambient = packet.unpack("f4", 16)
                light.position = packet.unpack("f3", 12)
                light.direction = packet.unpack("f3", 12)
                light.other = packet.unpack("f7", 28)
                light.unk = packet.unpack("V5", 20)
                self.lights.append(light)

        if packet.resid() != 0:
            fail("there is some data left in packet [" + packet.resid() + "]")

    def compile(self):
        # my self = shift;
        data = ""
        if self.version > 8:
            for light in self.lights:
                data += pack(
                    "VVf4f4f4f3f3f7",
                    light.controller_id,
                    light.type,
                    light.diffuse,
                    light.specular,
                    light.ambient,
                    light.position,
                    light.direction,
                    light.other,
                )

        elif self.version > 5:
            for light in self.lights:
                data += pack(
                    "Vf4f4f4f3f3f7VVZ*",
                    light.type,
                    light.diffuse,
                    light.specular,
                    light.ambient,
                    light.position,
                    light.direction,
                    light.other,
                    light.unk1,
                    light.unk2,
                    light.name,
                )
                for i in range(64 - len(light.name)):
                    data += pack("C", 0xED)

        else:
            for light in self.lights:
                data += pack(
                    "Vf4f4f4f3f3f7V5",
                    light.type,
                    light.diffuse,
                    light.specular,
                    light.ambient,
                    light.position,
                    light.direction,
                    light.other,
                    light.unk,
                )

        self.data = data

    def write(self, fh):
        index = chunks.get_index("FSL_LIGHT_DYNAMIC", self.version)
        fh.w_chunk(index, self.data)

    def export_ltx(self):
        fh = open(
            "FSL_LIGHT_DYNAMIC.ltx",
            "w",
            encoding="cp1251",
        )  # or fail("FSL_LIGHT_DYNAMIC.ltx: $!\n");

        for i, light in enumerate(self.lights):
            fh.write("[i]\n")
            if light.controller_id is not None:
                fh.write(f"controller_id = {light.controller_id}\n")
            fh.write("type = %s\n" % (self.lt_names[light.type]))
            fh.write("diffuse = %f, %f, %f, %f\n" % light.diffuse)
            fh.write("specular = %f, %f, %f, %f\n" % light.specular)
            fh.write("ambient = %f, %f, %f, %f\n" % light.ambient)
            fh.write("position = %f, %f, %f\n" % light.position)
            fh.write("direction = %f, %f, %f\n" % light.direction)
            fh.write("range = %f\n" % (light.other[0]))
            fh.write("falloff = %f\n" % (light.other[1]))
            fh.write("attenuation0 = %f\n" % (light.other[2]))
            fh.write("attenuation1 = %f\n" % (light.other[3]))
            fh.write("attenuation2 = %f\n" % (light.other[4]))
            fh.write("theta = %f\n" % (light.other[5]))
            fh.write("phi = %f\n" % (light.other[6]))
            if light.unk1 is not None:
                fh.write(f"unk1 = {light.unk1}\n")
            if light.unk2 is not None:
                fh.write(f"unk2 = {light.unk2}\n")
            if light.name is not None:
                fh.write(f"name = {light.name}\n")
            if light.unk is not None:
                fh.write("unk_0 = %s\n" % (light.unk[0]))
                fh.write("unk_1 = %s\n" % (light.unk[1]))
                fh.write("unk_2 = %s\n" % (light.unk[2]))
                fh.write("unk_3 = %s\n" % (light.unk[3]))
                fh.write("unk_4 = %s\n" % (light.unk[4]))

            fh.write("\n")

        fh.close()

    def import_ltx(self):
        fh = ini_file(
            "FSL_LIGHT_DYNAMIC.ltx",
            "r",
        )  # or fail("FSL_LIGHT_DYNAMIC.ltx: $!\n");
        len = len(fh.sections_list)
        for i in range(len):
            light = universal_dict_object()
            light.controller_id = fh.value(i, "controller_id")
            light.type = self.reverse_lt_names[fh.value(i, "type")]
            light.diffuse = re.split(r"/,\s*/", fh.value(i, "diffuse"))
            light.specular = re.split(r"/,\s*/", fh.value(i, "specular"))
            light.ambient = re.split(r"/,\s*/", fh.value(i, "ambient"))
            light.position = re.split(r"/,\s*/", fh.value(i, "position"))
            light.direction = re.split(r"/,\s*/", fh.value(i, "direction"))
            light.other[0] = fh.value(i, "range")
            light.other[1] = fh.value(i, "falloff")
            light.other[2] = fh.value(i, "attenuation0")
            light.other[3] = fh.value(i, "attenuation1")
            light.other[4] = fh.value(i, "attenuation2")
            light.other[5] = fh.value(i, "theta")
            light.other[6] = fh.value(i, "phi")
            light.unk1 = fh.value(i, "unk1")
            light.unk2 = fh.value(i, "unk2")
            light.name = fh.value(i, "name")
            light.unk[0] = fh.value(i, "unk_0")
            light.unk[1] = fh.value(i, "unk_1")
            light.unk[2] = fh.value(i, "unk_2")
            light.unk[3] = fh.value(i, "unk_3")
            light.unk[4] = fh.value(i, "unk_4")
            self.lights.append(light)

        fh.close()


#########################################################
class fsl_light_key_frames:
    # use strict;
    # use ini_file;
    # use debug qw(fail);
    # use data_packet;
    def __init__(self, version, data=""):
        self.version = version
        self.data = data

    def decompile(self):
        packet = data_packet(self.data)
        print("decompiling of FSL_LIGHT_KEY_FRAMES not implemented yet\n")

    def compile(self):
        data = ""
        print("compiling of FSL_LIGHT_KEY_FRAMES not implemented yet\n")
        self.data = data

    def write(self, fh):
        index = chunks.get_index("FSL_LIGHT_KEY_FRAMES", self.version)
        fh.w_chunk(index, self.data)

    def export_ltx(self):
        fh = open(
            "FSL_LIGHT_KEY_FRAMES.ltx",
            "w",
            encoding="cp1251",
        )  # or fail("FSL_LIGHT_KEY_FRAMES.ltx: $!\n");
        print("exporting decompiled data of FSL_LIGHT_KEY_FRAMES not implemented yet\n")
        fh.close()

    def import_ltx(self):
        fh = ini_file(
            "FSL_LIGHT_KEY_FRAMES.ltx",
            "r",
        )  # or fail("FSL_LIGHT_KEY_FRAMES.ltx: $!\n");
        print("importing decompiled data of FSL_LIGHT_KEY_FRAMES not implemented yet\n")
        fh.close()


#########################################################
class fsl_glows:
    # use strict;
    # use ini_file;
    # use debug qw(fail);
    # use data_packet;
    def __init__(self, version, data=""):
        self.version = version
        self.data = data

    def decompile(self):
        packet = data_packet(self.data)
        if self.version > 11:
            count = packet.resid() / 0x12
            if packet.resid() % 18 != 0:
                fail("wrong size of FSL_GLOWS")
            for i in range(count):
                glow = universal_dict_object()
                glow.position = packet.unpack("f3", 12)
                (glow.radius, glow.shader_index) = packet.unpack("fv", 6)
                self.glows.append(glow)

        else:
            count = packet.resid() / 0x18
            if packet.resid() % 24 != 0:
                fail("wrong size of FSL_GLOWS")  # ;
            for i in range(count):
                glow = universal_dict_object()
                glow.position = packet.unpack("f3", 12)
                (glow.radius, glow.texture_index, glow.shader_index) = packet.unpack(
                    "fVV",
                    12,
                )
                self.glows.append(glow)

        if packet.resid() != 0:
            fail("there is some data left in packet [" + packet.resid() + "]")

    def compile(self):
        data = ""
        if self.version <= 11:
            for glow in self.glows:
                data += pack(
                    "f3fVV",
                    glow.position,
                    glow.radius,
                    glow.texture_index,
                    glow.shader_index,
                )

        else:
            for glow in self.glows:
                data += pack("f3fv", glow.position, glow.radius, glow.shader_index)

        self.data = data

    def write(self, fh):
        index = chunks.get_index("FSL_GLOWS", self.version)
        fh.w_chunk(index, self.data)

    def export_ltx(self):
        fh = open(
            "FSL_GLOWS.ltx",
            "w",
            encoding="cp1251",
        )  # or fail("FSL_GLOWS.ltx: $!\n")

        for i, glow in enumerate(self.glows):
            fh.write("[i]\n")
            fh.write("position = %f, %f, %f\n" % (glow.position[0:2]))
            fh.write("radius = %f\n" % glow.radius)
            if self.version <= 11:
                fh.write(f"texture_index = {glow.texture_index}\n")
            fh.write(f"shader_index = {glow.shader_index}\n\n")

        fh.close()

    def import_ltx(self):
        fh = ini_file("FSL_GLOWS.ltx", "r")  # or fail("FSL_GLOWS.ltx: $!\n");
        len = len(fh.sections_list)
        for i in range(len):
            glow = universal_dict_object()
            glow.position = re.split(r",\s*", fh.value(i, "position"))
            glow.radius = fh.value(i, "radius")
            if self.version <= 11:
                glow.texture_index = fh.value(i, "texture_index")
            glow.shader_index = fh.value(i, "shader_index")
            self.glows.append(glow)

        fh.close()


#########################################################
class fsl_visuals:
    # use strict;
    # use ini_file;
    # use debug qw(fail);
    # use data_packet;
    def __init__(self, version, data=""):
        self.version = version
        self.data = data

    def decompile(self, mode):
        fh = chunked(self.data, "data")
        i = 0
        while 1:
            (index, size) = fh.r_chunk_open()
            if not (index is not None):
                break
            if mode and (mode == "full"):
                visual = ogf()
                visual.read(fh)
                self.visuals.append(visual)

            i += 1
            fh.r_chunk_close()

        self.vis_count = i
        fh.close()

    def compile(self, mode, index):
        data = ""
        fh = chunked("", "data")
        i = index

        if index is None:
            i = 0
        if mode and (mode == "full"):
            for visual in self.visuals:
                fh.w_chunk_open(i)
                visual.write(fh)
                fh.w_chunk_close(i)
                i += 1

        self.data = fh.data()
        fh.close()

    def write(self, fh):
        index = chunks.get_index("FSL_VISUALS", self.version)
        fh.w_chunk(index, self.data)

    def export_ltx(*args, **kwargs):
        print("exporting decompiled data of FSL_VISUALS not implemented yet\n")

    def import_ltx(*args, **kwargs):
        print("importing decompiled data of FSL_VISUALS not implemented yet\n")


#########################################################
class fsl_vertex_buffer:
    # use strict;
    # use ini_file;
    # use data_packet;
    # use debug qw(fail);
    type_names = {
        1: "FLOAT2",
        2: "FLOAT3",
        3: "FLOAT4",
        4: "D3DCOLOR",
        6: "SHORT2",
        7: "SHORT4",
        17: "UNUSED",
    }

    method_names = {
        0: "DEFAULT",
        1: "PARTIALU",
        2: "PARTIALV",
        3: "CROSSUV",
        4: "UV",
    }
    usage_names = {
        0: "POSITION",
        1: "BLENDWEIGHT",
        2: "BLENDINDICES",
        3: "NORMAL",
        4: "PSIZE",
        5: "TEXCOORD",
        6: "TANGENT",
        7: "BINORMAL",
        8: "TESSFACTOR",
        9: "POSITIONT",
        10: "COLOR",
        11: "FOG",
        12: "SAMPLE",
    }

    def __init__(self, version, data=""):
        self.version = version
        self.data = data

    def decompile(self, mode):
        packet = data_packet(self.data)
        (self.vbufs_count) = packet.unpack("V", 4)
        if mode and (mode == "full"):
            if self.version > 8:
                for i in range(self.vbufs_count):
                    vertex_buffer = universal_dict_object()
                    vertice_count
                    type = []
                    usage = []
                    j = 0
                    while True:
                        d3d9ve = universal_dict_object()
                        (
                            d3d9ve.stream,
                            d3d9ve.offset,
                            d3d9ve.type,
                            d3d9ve.method,
                            d3d9ve.usage,
                            d3d9ve.usage_index,
                        ) = packet.unpack("v2C4", 8)
                        type.append(d3d9ve.type)
                        usage.append(d3d9ve.usage)
                        vertex_buffer.d3d9vertexelements.append(d3d9ve)
                        if d3d9ve.type == 0x11:
                            vertice_count = j
                            break
                        j += 1

                    (vert_count) = packet.unpack("V", 4)
                    for j in range(vert_count):
                        vertex = universal_dict_object()
                        texcoord = 0
                        for z in range(vertice_count):
                            if self.usage_names[usage[z]] == "POSITION":
                                vertex.points = packet.unpack("f3", 12)
                            elif self.usage_names[usage[z]] == "NORMAL":
                                vertex.normals = packet.unpack("C4", 4)
                            elif self.usage_names[usage[z]] == "TEXCOORD":
                                if self.type_names[type[z]] == "FLOAT2":  # :
                                    if texcoord == 0:
                                        texcoord += 1
                                        vertex.texcoords = packet.unpack("f2", 8)
                                        print("vertex.texcoords\n")
                                    else:
                                        vertex.lightmaps = packet.unpack("f2", 8)
                                        print("vertex.lightmaps\n")
                                # break SWITCH;};
                                elif self.type_names[type[z]] == "SHORT2":  # :
                                    if texcoord == 0:
                                        texcoord += 1
                                        vertex.texcoords = packet.unpack("v2", 4)
                                    else:
                                        vertex.lightmaps = packet.unpack("v2", 4)

                                # 	break SWITCH;};
                                elif self.type_names[type[z]] == "SHORT4":  # :
                                    vertex.texcoords = packet.unpack("v2", 4)
                                    vertex.lightmaps = packet.unpack("v2", 4)
                                # break SWITCH;};
                                else:
                                    fail("unsupported type [" + type[z] + "]")
                            # }; break SWITCH;

                            elif self.usage_names[usage[z]] == "TANGENT":
                                vertex.tangents = packet.unpack(
                                    "C4",
                                    4,
                                )  # break SWITCH;};
                            elif self.usage_names[usage[z]] == "BINORMAL":
                                vertex.binormals = packet.unpack(
                                    "C4",
                                    4,
                                )  # break SWITCH;};
                            elif self.usage_names[usage[z]] == "COLOR":
                                vertex.colors = packet.unpack(
                                    "C4",
                                    4,
                                )  # break SWITCH;};
                            else:
                                fail("unsupported usage [" + usage[z] + "]")

                        vertex_buffer.vertices.append(vertex)

                    # 			print packet.pos."\n";
                    self.vbufs.append(vertex_buffer)

        else:
            for i in range(self.vbufs_count):
                set = universal_dict_object()
                (set.fvf, set.n) = packet.unpack("VV", 8)
                self.vbufs.append(set)

        if packet.resid() != 0:
            fail("there is some data left in packet [" + packet.resid() + "]")

    def compile(self):
        data = ""
        data += pack("V", len(self.vbufs))
        if self.version > 8:
            for set in self.vbufs:
                type = []
                usage = []
                for d3d9ve in set.d3d9vertexelements:
                    type.append(d3d9ve.type)
                    usage.append(d3d9ve.usage)
                    data += pack(
                        "v2C4",
                        d3d9ve.stream,
                        d3d9ve.offset,
                        d3d9ve.type,
                        d3d9ve.method,
                        d3d9ve.usage,
                        d3d9ve.usage_index,
                    )

                data += pack("V", len(set.vertices))
                vert_count = len(set.d3d9vertexelements)
                for vertex in set.vertices:
                    packet = data_packet()
                    texcoord = 0
                    for z in range(vert_count):
                        # SWITCH: {
                        if self.usage_names[usage[z]] == "POSITION":
                            packet.pack("f3", vertex.points)  # break SWITCH;};
                        elif self.usage_names[usage[z]] == "NORMAL":
                            packet.pack("C4", vertex.normals)  # break SWITCH;};
                        elif self.usage_names[usage[z]] == "TEXCOORD":
                            # SWITCH: {
                            if self.type_names[type[z]] == "FLOAT2":
                                texcoord += 1
                                if texcoord == 1:
                                    packet.pack("f2", vertex.texcoords)
                                else:
                                    packet.pack("f2", vertex.lightmaps)

                            # break SWITCH;};
                            elif self.type_names[type[z]] == "SHORT2":
                                texcoord += 1
                                if texcoord == 1:
                                    packet.pack("v2", vertex.texcoords)
                                else:
                                    packet.pack("v2", vertex.lightmaps)

                            # break SWITCH;};
                            elif self.type_names[type[z]] == "SHORT4":
                                packet.pack("v2", vertex.texcoords)
                                packet.pack("v2", vertex.lightmaps)
                            # break SWITCH;};
                            else:
                                fail("unsupported type [" + type[z] + "]")
                        # }; break SWITCH;
                        # };
                        elif self.usage_names[usage[z]] == "TANGENT":
                            packet.pack("C4", vertex.tangents)  # break SWITCH;};
                        elif self.usage_names[usage[z]] == "BINORMAL":
                            packet.pack("C4", vertex.binormals)  # break SWITCH;};
                        elif self.usage_names[usage[z]] == "COLOR":
                            packet.pack("C4", vertex.colors)  # break SWITCH;};
                        else:
                            fail("unsupported usage [" + usage[z] + "]")
                    # }

                    data += packet.data()

        else:
            for set in self.vbufs:
                data += pack("VV", set.fvf, set.n)

        self.data = data

    def write(self, fh):
        index = chunks.get_index("FSL_VB", self.version)
        fh.w_chunk(index, self.data)

    def export_ltx(*args, **kwargs):
        print("exporting decompiled data of FSL_VB not implemented\n")

    def import_ltx(*args, **kwargs):
        print("importing decompiled data of FSL_VB not implemented\n")


#########################################################
class fsl_swis:
    # use strict;
    # use ini_file;
    # use data_packet;
    # use debug qw(fail);
    def __init__(self, version, data=""):
        self.version = version
        self.data = data

    def decompile(self, mode):
        packet = data_packet(self.data)
        (self.swibufs_count) = packet.unpack("V", 4)
        if mode and (mode == "full"):
            for i in range(self.swibufs_count):
                swibuf = universal_dict_object()
                swibuf.reserved = packet.unpack("V4", 16)
                (swibuf.sw_count) = packet.unpack("V", 4)
                for j in range(swibuf.sw_count):
                    slide_window = universal_dict_object()
                    (
                        slide_window.offset,
                        slide_window.num_tris,
                        slide_window.num_verts,
                    ) = packet.unpack("lvv", 8)
                    swibuf.slide_windows.append(slide_window)

                self.swibufs.append(swibuf)

            if packet.resid() != 0:
                fail("there is some data left in packet [" + packet.resid() + "]")

    def compile(self):
        data = ""
        data += pack("V", len(self.swibufs))
        for swibuf in self.swibufs:
            data += pack("V4V", swibuf.reserved, swibuf.sw_count)
            for window in swibuf.slide_windows:
                data += pack("lvv", window.offset, window.num_tris, window.num_verts)

        self.data = data

    def write(self, fh):
        index = chunks.get_index("FSL_SWIS", self.version)
        fh.w_chunk(index, self.data)

    def export_ltx(*args, **kwargs):
        print("exporting decompiled data of FSL_SWIS not implemented\n")

    def import_ltx(*args, **kwargs):
        print("importing decompiled data of FSL_SWIS not implemented\n")


#########################################################
class fsl_index_buffer:
    # use strict;
    # use ini_file;
    # use debug qw(fail);
    # use data_packet;
    def __init__(self, version, data=""):
        self.version = version
        self.data = data

    def decompile(self, mode):
        packet = data_packet(self.data)
        (self.ibufs_count) = packet.unpack("V", 4)
        if mode and (mode == "full"):
            for i in range(self.ibufs_count):
                (count) = packet.unpack("V", 4)
                buffer = universal_dict_object()
                buffer.indices = packet.unpack(f"v{count}")
                self.ibufs.append(buffer)

            if packet.resid() != 0:
                fail("there is some data left in packet [" + packet.resid() + "]")

    def compile(self):
        data = ""
        data += pack("V", len(self.ibufs))
        for ibuf in self.ibufs:
            count = len(ibuf.indices)
            data += pack("V", count)
            data += pack(f"v{count}", ibuf.indices)

        self.data = data

    def write(self, fh):
        index = chunks.get_index("FSL_IB", self.version)
        fh.w_chunk(index, self.data)

    def export_ltx(*args, **kwargs):
        print("exporting decompiled data of FSL_IB not implemented\n")

    def import_ltx(*args, **kwargs):
        print("importing decompiled data of FSL_IB not implemented\n")


#########################################################
class fsl_textures:
    # use strict;
    # use ini_file;
    # use debug qw(fail);
    # use data_packet;
    def __init__(self, version, data=""):
        self.version = version
        self.data = data

    def decompile(self):
        packet = data_packet(self.data)
        (count,) = packet.unpack("V", 4)
        self.textures = packet.unpack(f"(Z*){count}")

    def compile(self):
        data = ""
        data = pack("V", self.count)
        for i in range(self.count):
            data += pack("Z*", self.textures[i])

        self.data = data

    def write(self, fh):
        fh.w_chunk(2, self.data)

    def export_ltx(self):
        fh = open(
            "FSL_TEXTURES.ltx",
            "w",
            encoding="cp1251",
        )  # or fail("FSL_TEXTURES.ltx: $!\n");
        len = len(self.textures)
        for i in range(len):
            fh.write("[i]\n")
            fh.write("texture = self.textures[i]\n")

        fh.close()

    def import_ltx(self):
        fh = ini_file("FSL_TEXTURES.ltx", "r")  # or fail("FSL_TEXTURES.ltx: $!\n");
        for i in range(len(fh.sections_list) + 1):
            self.textures[i] = fh.value(i, "texture")

        self.count = len(fh.sections_list)
        fh.close()


#########################################################
class fsl_shaders:
    # use strict;
    # use ini_file;
    # use debug qw(fail);
    # use data_packet;
    def __init__(self, version, data=""):
        self.version = version
        self.data = data

    def decompile(self):
        packet = data_packet(self.data)
        (count) = packet.unpack("V", 4)
        for i in range(count):
            (str) = packet.unpack("Z*")
            if self.version > 11:
                (self.shaders[i], self.textures[i]) = re.split(r"\/", str)
            else:
                self.textures[i] = str

    def compile(self):
        data = ""
        count = len(self.textures)
        data = pack("V", count)
        if self.version > 10:
            data += "\0"
        if self.version > 11:
            for i in range(count):
                data += pack("Z*", "/".join(self.shaders[i], self.textures[i]))

        else:
            first_rec = 0
            if self.version > 10:
                first_rec = 1

            for i in range(first_rec, count):
                data += pack("Z*", self.textures[i])

        self.data = data

    def write(self, fh):
        index = chunks.get_index("FSL_SHADERS", self.version)
        fh.w_chunk(index, self.data)

    def export_ltx(self):
        fh = open(
            "FSL_SHADERS.ltx",
            "w",
            encoding="cp1251",
        )  # or fail("FSL_SHADERS.ltx: $!\n")
        count = len(self.textures)
        first_rec = 0
        if self.version > 10:
            first_rec = 1

        for i in range(first_rec, count):
            fh.write("[i]\n")
            if self.version > 11:
                fh.write("shader = self.shaders[i]\n")
            fh.write("textures = self.textures[i]\n")
            fh.write("\n")

        fh.close()

    def import_ltx(self):
        fh = ini_file("FSL_SHADERS.ltx", "r")  # or fail("FSL_SHADERS.ltx: $!\n");
        first_rec = 0
        if self.version > 10:
            first_rec = 1

        len = len(fh.sections_list) + 1 + first_rec
        for i in range(first_rec, len):
            if self.version > 11:
                self.shaders[i] = fh.value(i, "shader")
            self.textures[i] = fh.value(i, "textures")

        fh.close()


#########################################################
class fsl_sectors:
    # use strict;
    # use ini_file;
    # use debug qw(fail);
    # use data_packet;
    def __init__(self, version, data=""):
        self.version = version
        self.data = data

    def decompile(self, mode):
        cf = chunked(self.data, "data")
        i = 0
        while 1:
            (index, size) = cf.r_chunk_open()
            if index is None:
                break
            sector = universal_dict_object()
            if mode and (mode == "full"):
                while 1:
                    (id, size) = cf.r_chunk_open()
                    if id is None:
                        break

                    if id == 0x1:
                        self.decompile_portals(sector, cf)  # break SWITCH; };
                    elif id == 0x2:
                        self.decompile_root(sector, cf)  # break SWITCH; };
                    else:
                        fail(f"unexpected chunk {id} size {size} in {index}\n")

                    cf.r_chunk_close()

                self.sectors.append(sector)

            i += 1
            cf.r_chunk_close()

        self.sector_count = i
        cf.close()

    def decompile_portals(self, cf):
        packet = data_packet(cf.r_chunk_data())
        if packet.resid() == 0:
            return
        count = packet.resid() / 2
        if packet.resid() % 2 != 0:
            fail("wrong size of portals in FSL_SECTORS")
        self.portals = packet.unpack(f"v{count}")
        if packet.resid() != 0:
            fail("there is some data left in packet [" + packet.resid() + "]")

    def decompile_root(self, cf):
        packet = data_packet(cf.r_chunk_data())
        (self.root) = packet.unpack("V", 4)
        if packet.resid() == 0:
            fail("there is some data left in packet [" + packet.resid() + "]")

    def compile(self, i=0):
        cf = chunked("", "data")

        for sector in self.sectors:
            cf.w_chunk_open(i)
            cf.w_chunk(0x2, pack("V", sector.root))
            cf.w_chunk_open(0x1)
            for portal in sector.portals:
                cf.w_chunk_data(pack("v", portal))

            cf.w_chunk_close()
            cf.w_chunk_close()
            i += 1

        self.data = cf.data()

    def write(self, fh):
        index = chunks.get_index("FSL_SECTORS", self.version)
        fh.w_chunk(index, self.data)

    def export_ltx(self):
        fh = open(
            "FSL_SECTORS.ltx",
            "w",
            encoding="cp1251",
        )  # or fail("FSL_SECTORS.ltx: $!\n");
        for i, sector in enumerate(self.sectors):
            fh.write("[i]\n")
            portal_count = len(sector.portals)
            fh.write(f"portals_count = {portal_count}\n")
            for j, portal in enumerate(sector.portals):
                fh.write(f"portal_{j} = {portal}\n")

            fh.write(f"root = {sector.root}\n\n")

        fh.close()

    def import_ltx(self):
        fh = ini_file("FSL_SECTORS.ltx", "r")  # or fail("FSL_SECTORS.ltx: $!\n");
        len = len(fh.sections_list)
        for i in range(len):
            sector = universal_dict_object()
            portals_count = fh.value(i, "portals_count")
            for j in range(portals_count):
                sector.portals[j] = fh.value(i, f"portal_{j}")

            sector.root = fh.value(i, "root")
            self.sectors.append(sector)

        fh.close()


#########################################################
class chunks:
    chunk_table = (
        {"name": "FSL_HEADER", "version": 0, "chunk_index": 0x1},
        {"name": "FSL_TEXTURES", "version": 0, "chunk_index": 0x2},
        {"name": "FSL_SHADERS", "version": 5, "chunk_index": 0x2},
        {"name": "FSL_SHADERS", "version": 0, "chunk_index": 0x3},
        {"name": "FSL_VISUALS", "version": 5, "chunk_index": 0x3},
        {"name": "FSL_VISUALS", "version": 0, "chunk_index": 0x4},
        {"name": "FSL_PORTALS", "version": 9, "chunk_index": 0x4},
        {"name": "FSL_PORTALS", "version": 5, "chunk_index": 0x6},
        {"name": "FSL_PORTALS", "version": 0, "chunk_index": 0x7},
        {"name": "FSL_CFORM", "version": 5, "chunk_index": 0x5},
        {"name": "FSL_CFORM", "version": 0, "chunk_index": 0x6},
        {"name": "FSL_SHADER_CONSTANT", "version": 8, "chunk_index": 0x7},
        {"name": "FSL_LIGHT_KEY_FRAMES", "version": 0, "chunk_index": 0x9},
        {"name": "FSL_LIGHT_DYNAMIC", "version": 9, "chunk_index": 0x6},
        {"name": "FSL_LIGHT_DYNAMIC", "version": 8, "chunk_index": 0x8},
        {"name": "FSL_LIGHT_DYNAMIC", "version": 5, "chunk_index": 0x7},
        {"name": "FSL_LIGHT_DYNAMIC", "version": 0, "chunk_index": 0x8},
        {"name": "FSL_GLOWS", "version": 9, "chunk_index": 0x7},
        {"name": "FSL_GLOWS", "version": 5, "chunk_index": 0x9},
        {"name": "FSL_GLOWS", "version": 0, "chunk_index": 0xA},
        {"name": "FSL_SECTORS", "version": 9, "chunk_index": 0x8},
        {"name": "FSL_SECTORS", "version": 5, "chunk_index": 0xA},
        {"name": "FSL_SECTORS", "version": 0, "chunk_index": 0xB},
        {"name": "FSL_VB", "version": 12, "chunk_index": 0x9},
        {"name": "FSL_VB", "version": 9, "chunk_index": 0xA},
        {"name": "FSL_VB", "version": 8, "chunk_index": 0xC},
        {"name": "FSL_VB", "version": 5, "chunk_index": 0x4},
        {"name": "FSL_VB", "version": 0, "chunk_index": 0x5},
        {"name": "FSL_IB", "version": 12, "chunk_index": 0xA},
        {"name": "FSL_IB", "version": 9, "chunk_index": 0x9},
        {"name": "FSL_IB", "version": 8, "chunk_index": 0xB},
        {"name": "FSL_SWIS", "version": 9, "chunk_index": 0xB},
    )
    reverse_chunk_table = (
        {"name": "FSL_HEADER", "version": 0, "chunk_index": 0x1},
        {"name": "FSL_SHADERS", "version": 5, "chunk_index": 0x2},
        {"name": "FSL_TEXTURES", "version": 0, "chunk_index": 0x2},
        {"name": "FSL_VISUALS", "version": 5, "chunk_index": 0x3},
        {"name": "FSL_SHADERS", "version": 0, "chunk_index": 0x3},
        {"name": "FSL_PORTALS", "version": 9, "chunk_index": 0x4},
        {"name": "FSL_VB", "version": 5, "chunk_index": 0x4},
        {"name": "FSL_VISUALS", "version": 0, "chunk_index": 0x4},
        {"name": "FSL_CFORM", "version": 5, "chunk_index": 0x5},
        {"name": "FSL_VB", "version": 0, "chunk_index": 0x5},
        {"name": "FSL_LIGHT_DYNAMIC", "version": 9, "chunk_index": 0x6},
        {"name": "FSL_PORTALS", "version": 5, "chunk_index": 0x6},
        {"name": "FSL_CFORM", "version": 0, "chunk_index": 0x6},
        {"name": "FSL_GLOWS", "version": 9, "chunk_index": 0x7},
        {"name": "FSL_SHADER_CONSTANT", "version": 8, "chunk_index": 0x7},
        {"name": "FSL_LIGHT_DYNAMIC", "version": 5, "chunk_index": 0x7},
        {"name": "FSL_PORTALS", "version": 0, "chunk_index": 0x7},
        {"name": "FSL_SECTORS", "version": 9, "chunk_index": 0x8},
        {"name": "FSL_LIGHT_DYNAMIC", "version": 8, "chunk_index": 0x8},
        {"name": "FSL_LIGHT_DYNAMIC", "version": 0, "chunk_index": 0x8},
        {"name": "FSL_VB", "version": 12, "chunk_index": 0x9},
        {"name": "FSL_IB", "version": 9, "chunk_index": 0x9},
        {"name": "FSL_GLOWS", "version": 5, "chunk_index": 0x9},
        {"name": "FSL_LIGHT_KEY_FRAMES", "version": 0, "chunk_index": 0x9},
        {"name": "FSL_IB", "version": 12, "chunk_index": 0xA},
        {"name": "FSL_VB", "version": 9, "chunk_index": 0xA},
        {"name": "FSL_SECTORS", "version": 5, "chunk_index": 0xA},
        {"name": "FSL_GLOWS", "version": 0, "chunk_index": 0xA},
        {"name": "FSL_SWIS", "version": 9, "chunk_index": 0xB},
        {"name": "FSL_IB", "version": 5, "chunk_index": 0xB},
        {"name": "FSL_SECTORS", "version": 0, "chunk_index": 0xB},
        {"name": "FSL_VB", "version": 8, "chunk_index": 0xC},
    )

    @classmethod
    def get_index(cls, name, version):
        for chunk in cls.chunk_table:
            if (name == chunk.name) and (version > chunk.version):
                return chunk.chunk_index

        return None

    @classmethod
    def get_name(cls, *args, **kwargs):
        if args[0] & 0x80000000:
            return "none"

        for chunk in cls.reverse_chunk_table:
            if (args[0] == chunk.chunk_index) and (args[1] > chunk.version):
                return chunk.name

        return None


#########################################################
class compressed:
    # use strict;
    # use IO.File;
    # use debug qw(fail);
    def __init__(self, version, data=""):
        self.version = version
        self.data = data

    def add(self, *args):
        self[chunks.get_name(args[0], self.version)] = args[1]

    def write(self, index, fh):
        ind = 0x80000000 + index
        fh.w_chunk(ind, self[chunks.get_name(index, self.version)])

    def export(self, name):
        if name == "version":
            return
        outf = open(
            "COMPRESSED_" + name + ".bin",
            "wb",
        )  # or fail("COMPRESSED_$name.bin: $!\n");
        # binmode $outf;
        outf.write(self[name], length(self[name]))
        outf.close()

    def _import(self, name):
        chunk = None
        if name and (
            rm := re.match(r"^(COMPRESSED)_(\w+)", name)
        ):  # =~ // is not None) {
            chunk = rm[2]
        else:
            fail()

        fh = open(name, "rb")  # or fail("$name: $!\n");
        # binmode $fh;
        data = ""
        fh.read(data, (fh.stat())[7])
        fh.close()
        self[chunk] = data


###########################################################
