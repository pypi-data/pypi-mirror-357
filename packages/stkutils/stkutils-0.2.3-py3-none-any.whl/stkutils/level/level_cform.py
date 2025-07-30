"""
# Module for handling level.cform stalker files
# Update history:
#	27/08/2012 - fix code for new fail() syntax
##################################################
=comment
This is readme for level_cform.pm module. Using this module you can decompile and compile cform of s.t.a.l.k.e.r maps (build 1893 and later)
How it works.
1. new - create object of cform data:

my $cform = level_cform($some_handle);

There are two kinds of argument:
        -filename. For newer builds (1580 and newer, xrlc_version >= 12) where level.cform exists.
        -reference (it's important!) to cform chunk data. For older builds (before 1580, xrlc_version < 12) where cform is one of level chunks.

2. decompile - unpacks data string into hashes and scalars, containing handable data. Takes no arguments.
structure of object after decompiling:
        $cform.version - scalar, version of xrlc
        $cform.vertcount - scalar, number of vertices
        $cform.facecount - scalar, number of faces
        @{$cform.vertices}} - array, number of vertices. Each vertex contain only one reference to array @{$vertex.coords}}, which is array of three coordinates of vertex.
        @{$cform.faces}} - array, number of faces. Each face has a references to scalar $face.material and array @{$face.coords}} with three vertices of which face consists.

3. compile - packs data into one string data and puts ref to this data in $cform.data. Method is complete opposite to compile. Takes no arguments.
4. write - writes cform chunk, using filehandle as argument.
5. export - exports data in external file. Takes an argument:
        - 'bin' - exports undecompiled binary data into FSL_CFORM.bin
        - other or no arguments at all - exports decompiled data into text file FSL_CFORM.ltx.
6. import - imports data from file. Same arguments as for 'export'.

Copyrights:
recovering cform format for final games - bardak.
recovering cform format for builds and perl implementing - K.D.
Last modified: 01.10.2011 5:29

Have fun!
=cut
"""

from stkutils import perl_utils
from stkutils.data_packet import data_packet
from stkutils.perl_utils import length, universal_dict_object


class level_cform:
    # use strict;
    # use IO::File;
    # use data_packet;
    # use ini_file;
    # use debug qw(fail);
    def __init__(self, data=""):
        # my $class = shift;
        # my $self = universal_dict_object();
        self.bbox = perl_utils.universal_dict_object()
        self.data = data

    # $self.data = $_[0] if defined $_[0];
    # bless($self, $class);
    # return $self;

    # def DESTROY {
    # 	my $self = shift;
    # 	foreach my $coord (@{$self.vertices}}) {
    # 		$coord.[0] = undef;
    # 		$coord.[1] = undef;
    # 		$coord.[2] = undef;
    # 		@$coord = ();
    # 	}
    # 	foreach my $face (@{$self.faces}}) {
    # 		$face.vertices[0] = undef;
    # 		$face.vertices[1] = undef;
    # 		$face.vertices[2] = undef;
    # 		$face.material = undef;
    # 		%$face = ();
    # 	}
    # 	@{$self.faces}} = ();
    # 	@{$self.vertices}} = ();
    # }

    def decompile(self, mode):
        packet = data_packet(self.data)
        (self.version, self.vertcount, self.facecount) = packet.unpack("VVV", 12)
        self.bbox.min = packet.unpack("f3", 12)
        self.bbox.max = packet.unpack("f3", 12)
        if mode and (mode == "full"):
            for i in range(self.vertcount):
                coords = packet.unpack("f3", 12)
                self.vertices.append(coords)

            for i in range(self.facecount):
                face = universal_dict_object()
                face.vertices = packet.unpack("V3", 12)
                (face.material) = packet.unpack("V", 4)
                # material field is a material index on gamemtl.xr (xrlc ver.12 (build 1580-2218))
                # in newer builds (and all final games) it consist of additional data:
                # 	-1-14th bits is a material index
                # 	-15th bit is suppress shadows flag (on/off)
                # 	-16th bit is suppress wallmarks flag (on/off)
                # 	-17-32th bits is a sector (dunno what's this, it's from bardak's dumper)
                self.faces.append(face)

    # 	sleep(10);	#87432

    def compile(self):
        packet = data_packet()
        packet.pack(
            "VVVf3f3",
            self.version,
            self.vertcount,
            self.facecount,
            self.bbox.min,
            self.bbox.max,
        )
        for coord in self.vertices:
            packet.pack("f3", coord)

        for face in self.faces:
            packet.pack("V3V", face.vertices, face.material)

        self.data = packet.data()

    def write(self, fh):
        if self.version < 2:
            fh.w_chunk(0x6, self.data)
        elif self.version < 4:
            fh.w_chunk(0x5, self.data)
        else:
            fh.write(self.data, length(self.data))

    def export_ltx(self, fh):

        fh.write("[header]\n")
        fh.write(f"version = {self.version}\n")
        fh.write(f"vert_count = {self.vertcount}\n")
        fh.write(f"face_count = {self.facecount}\n")
        fh.write("bbox_min = %f, %f, %f\n" % self.bbox.min)
        fh.write("bbox_max = %f, %f, %f\n" % self.bbox.max)
        fh.write("\n[vertices]\n")

        for i, vertex in enumerate(self.vertices):
            fh.write(f"vertex_{i} = %f, %f, %f\n", vertex.coords)

        for j, face in enumerate(self.faces):
            fh.write(f"\n[face_{j}]\n")
            fh.write("vertices = %f, %f, %f\n" % face.coords)
            fh.write(f"material = {self.material}\n")

    def import_ltx(self, fh):
        self.version = fh.value("header", "version")
        self.vertcount = fh.value("header", "vert_count")
        self.facecount = fh.value("header", "face_count")
        self.bbox.min = perl_utils.split(r",\s*", fh.value("header", "bbox_min"))
        self.bbox.max = perl_utils.split(r",\s*", fh.value("header", "bbox_max"))

        for i in range(self.vertcount):
            vertex = universal_dict_object()
            vertex.coords = perl_utils.split(
                r",\s*",
                fh.value("vertices", f"vertex_{i}"),
            )
            self.vertices.append(vertex)

        for i in range(self.facecount):
            face = universal_dict_object()
            face.coords = perl_utils.split(r",\s*", fh.value(f"face_{i}", "vertices"))
            self.material = fh.value(f"face_{i}", "material")
            self.faces.append(face)

    def calculate_bbox(self):
        bbox = self.bbox
        vertices = self.vertices
        bbox.min[0] = vertices[0][0]
        bbox.min[1] = vertices[0][1]
        bbox.min[2] = vertices[0][2]
        bbox.max[0] = vertices[0][0]
        bbox.max[1] = vertices[0][1]
        bbox.max[2] = vertices[0][2]
        for vertex in vertices:
            bbox.min[0] = min(bbox.min[0], vertex[0])
            bbox.min[1] = min(bbox.min[1], vertex[1])
            bbox.min[2] = min(bbox.min[2], vertex[2])
            bbox.max[0] = max(bbox.max[0], vertex[0])
            bbox.max[1] = max(bbox.max[1], vertex[1])
            bbox.max[2] = max(bbox.max[2], vertex[2])
