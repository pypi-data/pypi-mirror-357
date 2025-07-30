# Module for handling stalker *.graph files
# Update history:
# 	27/08/2012 - fix data for new fail() syntax
##########################################################
import os

from stkutils import gg_version
from stkutils.binary_data import unpack
from stkutils.data_packet import data_packet
from stkutils.level.level_gct import level_gct
from stkutils.perl_utils import (
    fail,
    join,
    length,
    rename,
    substr,
    universal_dict_object,
)


class gg_header(universal_dict_object):
    header_1472 = (  # 12 байт
        {"name": "version", "type": "u32"},
        {"name": "vertex_count", "type": "u32"},
        {"name": "level_count", "type": "u32"},
    )
    header_1935 = (  # 20 байт
        {"name": "version", "type": "u32"},
        {"name": "level_count", "type": "u32"},
        {"name": "vertex_count", "type": "u32"},
        {"name": "edge_count", "type": "u32"},
        {"name": "level_point_count", "type": "u32"},
    )
    header_2215 = (  # 36 байт
        {"name": "version", "type": "u32"},
        {"name": "level_count", "type": "u32"},
        {"name": "vertex_count", "type": "u32"},
        {"name": "edge_count", "type": "u32"},
        {"name": "level_point_count", "type": "u32"},
        {"name": "guid", "type": "guid"},
    )
    header_SOC = (  # 28 байт
        {"name": "version", "type": "u8"},
        {"name": "vertex_count", "type": "u16"},
        {"name": "edge_count", "type": "u32"},
        {"name": "level_point_count", "type": "u32"},
        {"name": "guid", "type": "guid"},
        {"name": "level_count", "type": "u8"},
    )

    def read(*args):
        self = args[0]
        if args[2] == "1469" or args[2] == "1472":
            args[1].unpack_properties(args[0], self.header_1472)
        elif args[2] == "1510" or args[2] == "1935":
            args[1].unpack_properties(args[0], self.header_1935)
        elif args[2] == "2215":
            args[1].unpack_properties(args[0], self.header_2215)
        else:
            args[1].unpack_properties(args[0], self.header_SOC)

    def write(*args):
        self = args[0]
        if args[2] == "1469" or args[2] == "1472":
            args[1].pack_properties(args[0], self.header_1472)
        elif args[2] == "1510" or args[2] == "1935":
            args[1].pack_properties(args[0], self.header_1935)
        elif args[2] == "2215":
            args[1].pack_properties(args[0], self.header_2215)
        else:
            args[1].pack_properties(args[0], self.header_SOC)

    def export(self, fh, lg):

        fh.write(f"version = {self.version}\n")
        fh.write(f"level_count = {self.level_count}\n")
        fh.write(f"vertex_count = {self.vertex_count}\n")
        if not lg and self.level_point_count is not None:
            fh.write(f"level_point_count = {self.level_point_count}\n")
        if self.edge_count is not None:
            fh.write(f"edge_count = {self.edge_count}\n")
        fh.write("\n")


#######################################################################
class gg_level(universal_dict_object):
    level_1469 = (
        {"name": "level_name", "type": "sz"},
        {"name": "offset", "type": "f32v3"},
    )
    level_1472 = (
        {"name": "level_name", "type": "sz"},
        {"name": "offset", "type": "f32v3"},
        {"name": "level_id", "type": "u32"},
    )
    level_1935 = (
        {"name": "level_name", "type": "sz"},
        {"name": "offset", "type": "f32v3"},
        {"name": "level_id", "type": "u32"},
        {"name": "section_name", "type": "sz"},
    )
    level_2215 = (
        {"name": "level_name", "type": "sz"},
        {"name": "offset", "type": "f32v3"},
        {"name": "level_id", "type": "u32"},
        {"name": "section_name", "type": "sz"},
        {"name": "guid", "type": "guid"},
    )
    level_SOC = (
        {"name": "level_name", "type": "sz"},
        {"name": "offset", "type": "f32v3"},
        {"name": "level_id", "type": "u8"},
        {"name": "section_name", "type": "sz"},
        {"name": "guid", "type": "guid"},
    )

    def read(*args):
        self = args[0]
        if args[2] == "1469":
            args[1].unpack_properties(args[0], self.level_1469)
            if args[0].level_name == "level2_test":
                args[0].level_id = 0
            elif args[0].level_name == "occ_part":
                args[0].level_id = 1
            else:
                args[0].level_id = 2

        elif args[2] == "1472" or args[2] == "1510":
            args[1].unpack_properties(args[0], self.level_1472)
        elif args[2] == "1935":
            args[1].unpack_properties(args[0], self.level_1935)
        elif args[2] == "2215":
            args[1].unpack_properties(args[0], self.level_2215)
        else:
            args[1].unpack_properties(args[0], self.level_SOC)

    def write(*args):
        self = args[0]
        if args[2] == "1469":
            args[1].pack_properties(args[0], self.level_1469)
        elif args[2] == "1472" or args[2] == "1510":
            args[1].pack_properties(args[0], self.level_1472)
        elif args[2] == "1935":
            args[1].pack_properties(args[0], self.level_1935)
        elif args[2] == "2215":
            args[1].pack_properties(args[0], self.level_2215)
        else:
            args[1].pack_properties(args[0], self.level_SOC)

    def export(self, fh, lg):
        fh.write(f"level_name = {self.level_name}\n")
        if not lg and (self.level_id is not None):
            fh.write(f"level_id = {self.level_id}\n")
        if not lg and (self.section_name is not None):
            fh.write(f"section_name = {self.section_name}\n")
        fh.write("offset = " + join(",", self.offset) + "\n\n")


#######################################################################
class gg_vertex(universal_dict_object):
    # use strict;
    vertex_1472 = (
        {"name": "level_point", "type": "f32v3"},
        {"name": "game_point", "type": "f32v3"},
        {"name": "level_id", "type": "u8"},
        {"name": "level_vertex_id", "type": "u24"},
        {"name": "vertex_type", "type": "u8v4"},
        {"name": "edge_count", "type": "u8"},
        {"name": "edge_offset", "type": "u24"},
    )
    vertex_1935 = (
        {"name": "level_point", "type": "f32v3"},
        {"name": "game_point", "type": "f32v3"},
        {"name": "level_id", "type": "u8"},
        {"name": "level_vertex_id", "type": "u24"},
        {"name": "vertex_type", "type": "u8v4"},
        {"name": "edge_count", "type": "u8"},
        {"name": "edge_offset", "type": "u24"},
        {"name": "level_point_count", "type": "u8"},
        {"name": "level_point_offset", "type": "u24"},
    )
    vertex_SOC = (
        {"name": "level_point", "type": "f32v3"},
        {"name": "game_point", "type": "f32v3"},
        {"name": "level_id", "type": "u8"},
        {"name": "level_vertex_id", "type": "u24"},
        {"name": "vertex_type", "type": "u8v4"},
        {"name": "edge_offset", "type": "u32"},
        {"name": "level_point_offset", "type": "u32"},
        {"name": "edge_count", "type": "u8"},
        {"name": "level_point_count", "type": "u8"},
    )

    def read(self, packet, graph):
        # self = args[0]
        ver = gg_version.gg_version
        eOffset = graph.edges_offset
        lpOffset = graph.level_points_offset
        if ver == "1469" or ver == "1472":
            packet.unpack_properties(self, self.vertex_1472)
        elif ver == "1510" or ver == "1935" or ver == "2215":
            packet.unpack_properties(self, self.vertex_1935)
        else:
            packet.unpack_properties(self, self.vertex_SOC)

        if ver == "1469" or ver == "1472" or graph.level_graph():
            self.edge_index = (self.edge_offset - eOffset) / (graph.edge_block_size())
        else:
            self.edge_index = (self.edge_offset - eOffset) / (graph.edge_block_size())
            self.level_point_index = (
                self.level_point_offset - eOffset - lpOffset
            ) / 0x14

    def write(*args):
        self = args[0]
        ver = gg_version.gg_version
        eOffset = args[2].edges_offset
        lpOffset = args[2].level_points_offset
        if ver == "1469" or ver == "1472":
            args[1].pack_properties(args[0], self.vertex_1472)
        elif ver == "1510" or ver == "1935" or ver == "2215":
            args[0].edge_offset = (
                args[2].edge_block_size() * args[0].edge_index + eOffset
            )
            if not args[2].level_graph():
                args[0].level_point_offset = (
                    0x14 * args[0].level_point_index + eOffset + lpOffset
                )
            else:
                args[0].level_point_offset = 0
                args[0].level_point_count = 0

            args[1].pack_properties(args[0], self.vertex_1935)
        else:
            args[0].edge_offset = (
                args[2].edge_block_size() * args[0].edge_index + eOffset
            )
            if not args[2].level_graph():
                args[0].level_point_offset = (
                    0x14 * args[0].level_point_index + eOffset + lpOffset
                )
            else:
                args[0].level_point_offset = 0
                args[0].level_point_count = 0

            args[1].pack_properties(args[0], self.vertex_SOC)

    def export(self, fh, lg):

        fh.write("level_point = " + join(",", self.level_point), "\n")
        if not lg:
            fh.write("game_point = " + join(",", self.game_point), "\n")
        if not lg:
            fh.write(f"level_id = {self.level_id}\n")
        fh.write(f"level_vertex_id = {self.level_vertex_id}\n")
        fh.write("vertex_type = ", join(",", self.vertex_type), "\n")
        if self.level_point_count is not None:
            fh.write(
                f"level_points = {self.level_point_index}, {self.level_point_count}\n",
            )
        fh.write(f"edges = {self.edge_index}, {self.edge_count}\n\n")


#######################################################################
class gg_edge(universal_dict_object):
    edge_builds = (
        {"name": "game_vertex_id", "type": "u32"},
        {"name": "distance", "type": "f32"},
    )
    edge_SOC = (
        {"name": "game_vertex_id", "type": "u16"},
        {"name": "distance", "type": "f32"},
    )

    def read(*args):
        self = args[0]
        if args[2] == "soc" or args[2] == "cop":
            args[1].unpack_properties(args[0], self.edge_SOC)
        else:
            args[1].unpack_properties(args[0], self.edge_builds)

    def write(*args):
        self = args[0]
        if args[2] == "soc" or args[2] == "cop":
            args[1].pack_properties(args[0], self.edge_SOC)
        else:
            args[1].pack_properties(args[0], self.edge_builds)

    def export(self, fh):
        fh.write(f"game_vertex_id = {self.game_vertex_id}\n")
        fh.write(f"distance = {self.distance}\n\n")


#######################################################################
class gg_level_point(universal_dict_object):
    properties_info = (
        {"name": "point", "type": "f32v3"},
        {"name": "level_vertex_id", "type": "u32"},
        {"name": "distance", "type": "f32"},
    )

    def read(*args):
        self = args[0]
        args[1].unpack_properties(args[0], self.properties_info)

    def write(*args):
        self = args[0]
        args[1].pack_properties(args[0], self.properties_info)

    def export(self, fh):
        fh.write("point = " + join(",", self.point) + "\n")
        fh.write(f"level_vertex_id = {self.level_vertex_id}\n")
        fh.write(f"distance = {self.distance}\n\n")


#######################################################################
class gg_cross_table(universal_dict_object):
    properties_info = (
        {"name": "size", "type": "u32"},
        {"name": "version", "type": "u32"},
        {"name": "cell_count", "type": "u32"},
        {"name": "vertex_count", "type": "u32"},
        {"name": "level_guid", "type": "guid"},
        {"name": "game_guid", "type": "guid"},
    )

    def __init__(self):
        self.cells = universal_dict_object()

    def read(*args):
        self = args[0]
        args[1].unpack_properties(args[0], self.properties_info)

    def export(self, fh):
        fh.write(f"version = {self.version}\n")
        fh.write(f"cell_count = {self.cell_count}\n")
        fh.write(f"vertex_count = {self.vertex_count}\n")
        fh.write(f"level_guid = {self.level_guid}\n")
        fh.write(f"game_guid = {self.game_guid}\n")
        fh.write("\n")


#######################################################################
class graph:

    def __init__(self, data=""):
        self.header = gg_header()
        self.data = data
        self.level_by_id = universal_dict_object()
        self.level_by_guid = universal_dict_object()
        self.lp_offsets = universal_dict_object()
        self.lp_counts = universal_dict_object()
        self.ct_size = universal_dict_object()
        self.ct_offset = universal_dict_object()
        self.raw_cross_tables = universal_dict_object()
        self.raw_vertices = ""
        self.raw_edges = ""
        self.raw_level_points_all = ""
        self.raw_cross_tables_all = ""
        self.is_level_graph = 0
        self.gg_version = None
        self.levels = []
        self.raw_level_points = []
        self.vertices = []
        self.edges = []
        self.level_by_name = {}
        self.cross_tables = []
        self.level_points = []

    def check_graph_version(self):
        self.gg_version = "1510"
        (switch,) = unpack("V", substr(self.data, 0, 4))
        if switch <= 8:
            if switch == 8:
                self.gg_version = "2215"
            elif switch == 3:
                (edge_count,) = unpack("V", substr(self.data, 12, 4))
                if edge_count > 50000:
                    self.gg_version = "1469"

        else:
            (version,) = unpack("C", substr(self.data, 0, 1))
            if version == 8:
                self.gg_version = "soc"
            elif version > 8:
                self.gg_version = "cop"
            else:
                fail("wrong graph format")

    def decompose(self):
        print("reading game graph...\n")
        if not (self.gg_version is not None):
            self.check_graph_version()

        self.read_header(substr(self.data, 0, self.header_size()))
        self.level_size = 0x1000
        if length(self.data) < 0x1000:
            self.level_size = length(self.data)
        self.read_levels(substr(self.data, 0, self.level_size))
        self.raw_vertices = substr(self.data, self.vertices_offset, self.edges_offset)
        if self.gg_version == "1469" or self.gg_version == "1472" or self.level_graph():
            self.raw_edges = substr(self.data, self.vertices_offset + self.edges_offset)
            if (
                self.gg_version == "1469"
                and not self.level_graph()
                and length(self.data) != self.vertices_offset + self.edges_offset
            ):
                self.error_handler("1472")
                return

        else:
            if (
                self.gg_version == "1510"
                and not self.level_graph()
                and length(self.data)
                != self.vertices_offset
                + self.edges_offset
                + self.level_points_offset
                + self.header.level_point_count * 0x14
            ):
                self.error_handler("1935")
                return

            self.raw_edges = substr(
                self.data,
                self.vertices_offset + self.edges_offset,
                self.level_points_offset,
            )
            if self.gg_version == "cop":
                self.raw_level_points_all = substr(
                    self.data,
                    self.vertices_offset + self.edges_offset + self.level_points_offset,
                    self.cross_tables_offset,
                )
                self.split_ct_block()
            else:
                self.raw_level_points_all = substr(
                    self.data,
                    self.vertices_offset + self.edges_offset + self.level_points_offset,
                )

    def split_lp_block(self):
        if self.header.level_count == 1:
            self.raw_level_points[self.levels[0].level_name] = self.raw_level_points_all
            return

        for level in self.levels:
            if level.level_point_offset + level.level_point_count * 0x14 < length(
                self.raw_level_points_all,
            ):
                self.raw_level_points[level.level_name] = substr(
                    self.raw_level_points_all,
                    level.level_point_offset,
                    level.level_point_count * 0x14,
                )
            else:
                self.raw_level_points[level.level_name] = substr(
                    self.raw_level_points_all,
                    level.level_point_offset,
                )

    def split_ct_block(self):
        if self.header.level_count == 1:
            self.raw_cross_tables[self.levels[0].level_name] = self.raw_cross_tables_all
            return

        self.raw_cross_tables_all = substr(
            self.data,
            self.vertices_offset
            + self.edges_offset
            + self.level_points_offset
            + self.cross_tables_offset,
        )
        com_offset = (
            self.vertices_offset
            + self.edges_offset
            + self.level_points_offset
            + self.cross_tables_offset
        )
        self.read_ct_offsets()
        for level in self.levels:
            if self.ct_offset[level.level_name] + self.ct_size[
                level.level_name
            ] < length(self.raw_cross_tables_all):
                self.raw_cross_tables[level.level_name] = substr(
                    self.raw_cross_tables_all,
                    self.ct_offset[level.level_name],
                    self.ct_size[level.level_name],
                )
            else:
                self.raw_cross_tables[level.level_name] = substr(
                    self.raw_cross_tables_all,
                    self.ct_offset[level.level_name],
                )

    def read_header(self, *args):
        print("	reading header...\n")
        self.header.read(data_packet(args[0]), self.gg_version)
        self.edges_offset = self.header.vertex_count * self.vertex_block_size()
        if not (self.gg_version == "1469" or self.gg_version == "1472"):
            self.level_points_offset = self.header.edge_count * self.edge_block_size()

        if self.gg_version == "cop":
            self.cross_tables_offset = self.header.level_point_count * 0x14

    def read_levels(self, *args):
        print("	reading levels...\n")
        packet = data_packet(substr(args[0], self.header_size()))
        for i in range(self.header.level_count):
            level = gg_level()
            level.read(packet, self.gg_version)
            self.levels.append(level)

        for level in self.levels:
            self.level_by_id[level.level_id] = level
            self.level_by_name[level.level_name] = level

        self.vertices_offset = self.level_size - packet.resid()

    def read_vertices(self):
        print("	reading vertices...\n")
        packet = data_packet(self.raw_vertices)
        for i in range(self.header.vertex_count):
            vertex = gg_vertex()
            vertex.read(packet, self)
            self.vertices.append(vertex)

        game_vertex_id = 0
        level_id = -1
        level_count = 1
        self.level_by_guid[self.header.vertex_count] = "_level_unknown"
        for vertex in self.vertices:
            ### fill some level properties
            if vertex.level_id != level_id:
                level_curr = self.level_by_id[vertex.level_id]
                if level_id > 0:
                    level_prev = self.level_by_id[level_id]
                level_curr.vertex_index = game_vertex_id
                level_curr.edge_index = vertex.edge_index
                level_curr.level_point_index = vertex.level_point_index
                level_curr.level_point_offset = (
                    vertex.level_point_offset
                    - self.edges_offset
                    - self.level_points_offset
                )
                ### maintain last level ($vertex.level_id != $level_id can't be true)
                if level_id > 0:
                    level_prev.vertex_count = game_vertex_id - level_prev.vertex_index
                    level_prev.edge_count = (
                        level_curr.edge_index - level_prev.edge_index
                    )
                    level_prev.level_point_count = (
                        level_curr.level_point_index - level_prev.level_point_index
                    )

                if (
                    self.header.level_count == 1
                    or self.header.level_count == level_count
                ):
                    level_curr.vertex_count = (
                        self.header.vertex_count - level_curr.vertex_index
                    )
                    level_curr.edge_count = (
                        self.header.edge_count - level_curr.edge_index
                    )
                    level_curr.level_point_count = (
                        self.header.level_point_count - level_curr.level_point_index
                    )
                    self.level_by_guid[game_vertex_id] = level_curr.level_name
                    return

                level_count += 1
                level_id = vertex.level_id
                self.level_by_guid[game_vertex_id] = level_curr.level_name

            game_vertex_id += 1

    def read_edges(self):
        print("	reading edges...\n")
        packet = data_packet(self.raw_edges)
        edge_count = 0
        if self.gg_version == "1469" or self.gg_version == "1472" or self.level_graph():
            edge_count = (packet.resid()) / self.edge_block_size()
        else:
            edge_count = self.header.edge_count

        for i in range(edge_count):
            edge = gg_edge()
            edge.read(packet, self.gg_version)
            self.edges.append(edge)

    def read_level_points(self):
        if self.raw_level_points_all == "":
            return
        packet = data_packet(self.raw_level_points_all)
        print("	reading level points...\n")
        for i in range(self.header.level_point_count):
            level_point = gg_level_point()
            level_point.read(packet)
            self.level_points.append(level_point)

    def read_lp_offsets(self):
        self.lp_offsets = universal_dict_object()
        self.lp_counts = universal_dict_object()
        for vertex in self.vertices:
            level = self.level_by_id[vertex.level_id]
            if not (self.lp_offsets[level.level_name] is not None):
                self.lp_offsets[level.level_name] = (
                    vertex.level_point_offset
                )  ####оффсеты идут с начала файла!
                self.lp_counts[level.level_name] = vertex.level_point_count
                var = self.offset_for_ct + self.lp_offsets[level.level_name]
            else:
                self.lp_counts[level.level_name] += vertex.level_point_count

    def read_cross_tables(self):
        if self.header.version < 4:
            return
        print("	reading cross tables...\n")
        for level in self.levels:
            cross_table = level_gct(self.raw_cross_tables[level.level_name])
            cross_table.read("full")
            cross_table.level_name = level.level_name
            self.cross_tables.append(cross_table)

    def read_ct_offsets(self):
        offset = 0
        data = self.raw_cross_tables_all
        len = length(data)
        for level in self.levels:
            (self.ct_size[level.level_name],) = unpack("V", substr(data, 0, 0x04))
            self.ct_offset[level.level_name] = (
                offset  ####оффсеты идут с начала блока кросс-таблиц!
            )
            offset += self.ct_size[level.level_name]
            if length(data) > self.ct_size[level.level_name]:
                data = substr(data, self.ct_size[level.level_name])

    def load_cross_tables(self):
        if self.gg_version == "cop" or self.header.version < 4:
            return
        print("	loading cross tables...\n")
        for level in self.levels:
            fnane = os.path.join("levels", level.level_name, "level.gct")
            fh = open(fnane, "rb")
            data = ""
            fh.read(data)
            fh.close()
            self.raw_cross_tables[level.level_name] = data

    def save_cross_tables(self):
        if self.gg_version == "cop" or self.header.version < 4:
            return
        print("	saving cross tables...\n")
        for level in self.levels:
            fn = os.path.join("levels", level.level_name, "level.gct")
            rename(fn, fn + ".bak")  # or unlink $fn.'bak' and rename $fn, $fn.'.bak';
            fh = open(fn, "wb")  # or fail("$! $fn\n");
            # binmode $fh;
            if not (self.raw_cross_tables[level.level_name] is not None):
                fail("cannot find cross table for level " + level.level_name)
            fh.write(
                self.raw_cross_tables[level.level_name],
                length(self.raw_cross_tables[level.level_name]),
            )
            fh.close()

    def compose(self):
        h = self.write_header()
        l = self.write_levels()
        hlve = h[l[self.raw_vertices[self.raw_edges]]]
        if (
            (self.gg_version != "1469")
            and (self.gg_version != "1472")
            and (not self.level_graph())
        ):
            if self.raw_level_points is not None:
                lp_data = ""
                for level in self.levels:
                    lp_data += self.raw_level_points[level.level_name]

                self.raw_level_points_all = lp_data

            hlve += self.raw_level_points_all
            if self.gg_version == "cop":
                ct_data = ""
                for level in self.levels:
                    ct_data += self.raw_cross_tables[level.level_name]

                self.raw_cross_tables_all = ct_data
                hlve += self.raw_cross_tables_all

        self.data = hlve

    def write_header(self):
        print("	writing header...\n")
        packet = data_packet()
        self.header.write(packet, self.gg_version)
        return packet.data()

    def write_levels(self):
        print("	writing levels...\n")
        packet = data_packet()
        for level in self.levels:
            level.write(packet, self.gg_version)

        return packet.data()

    def write_vertices(self):
        print("	writing vertices...\n")
        packet = data_packet()
        for vertex in self.vertices:
            vertex.write(packet, self)

        self.raw_vertices = packet.data()

    def write_edges(self):
        print("	writing edges...\n")
        packet = data_packet()
        for edge in self.edges:
            edge.write(packet, self.gg_version)

        self.raw_edges = packet.data()

    def write_level_points(self):
        if self.gg_version == "1469" or self.gg_version == "1472":
            return
        print("	writing level points...\n")
        packet = data_packet()
        for lpoint in self.level_points:
            lpoint.write(packet, self.gg_version)

        self.raw_level_points_all = packet.data()

    def write_cross_tables(self):
        if self.header.version < 4:
            return
        print("	writing cross tables...\n")
        for ct in self.cross_tables:
            ct.write("full")
            self.raw_cross_tables[ct.level_name] = ct.data

    def export_header(self, fh):
        print("	exporting header...\n")
        fh.write("[header]\n")
        lg = self.level_graph()
        self.header.export(fh, lg)

    def export_levels(self, fh):

        print("	exporting levels...\n")

        lg = self.level_graph()
        for i, level in enumerate(self.levels):
            fh.write(f"[level_{i}]\n")
            level.export(fh, lg)

    def export_vertices(self, fh):
        lg = self.level_graph()
        print("	exporting vertices...\n")
        for i, vertex in enumerate(self.vertices):
            fh.write(f"[vertex_{i}]\n")
            vertex.export(fh, lg)

    def export_edges(self, fh):

        print("	exporting edges...\n")
        for i, edge in enumerate(self.edges):
            fh.write(f"[edge_{i}]\n")
            edge.export(fh)

    def export_level_points(self, fh):

        if self.raw_level_points_all == "":
            return

        print("	exporting level points...\n")
        for i, level_point in enumerate(self.level_points):
            fh.write(f"[level_point_{i}]\n")
            level_point.export(fh)

    def export_cross_tables(self, fh):
        print("	exporting cross tables...\n")
        for i, cross_table in enumerate(self.cross_tables):
            fh.write(f"[cross_table_{i}]\n")
            cross_table.export(fh)
            fh.write(f"level_name = {cross_table.level_name}\n")
            for j in range(cross_table.cell_count):
                graph_id = cross_table.cells[j].graph_id
                distance = cross_table.cells[j].distance
                fh.write(f"node{j} = {graph_id}, {distance}\n")

    def show_links(self, fn):
        if self.header.level_count == 1:
            return
        level_by_id = universal_dict_object()
        for level in self.levels:
            level_by_id[level.level_id] = level

        if fn is not None:
            fh = open(fn, "a")
        for vid, vertex in enumerate(self.vertices):
            for i in range(vertex.edge_count):
                edge = self.edges[vertex.edge_index + i]
                vid2 = edge.game_vertex_id
                vertex2 = self.vertices[vid2]
                if vertex.level_id != vertex2.level_id:
                    level = level_by_id[vertex.level_id]
                    level2 = level_by_id[vertex2.level_id]
                    name = level.level_name
                    name2 = level2.level_name
                    if fn is not None:
                        fh.write(
                            "%s (%d) --%5.2f-. %s (%d)\n" % name,
                            vid,
                            edge.distance,
                            name2,
                            vid2,
                        )
                    # 					fh.write("$name ($vid) --  $edge.distance  -. $name2 ($vid2)\n")
                    else:
                        print(
                            "%s (%d) --%5.2f-. %s (%d)\n"
                            % (name, vid, edge.distance, name2, vid2),
                        )

        if fn is not None:
            fh.close()

    def show_guids(self, fn):

        if self.header.level_count == 1:
            return
        level_by_id = universal_dict_object()
        for level in self.levels:
            level_by_id[level.level_id] = level

        level_id = -1
        if fn is not None:
            fh = open(fn, "a")
        for game_vertex_id, vertex in enumerate(self.vertices):
            if vertex.level_id != level_id:
                level = level_by_id[vertex.level_id]
                if fn is not None:
                    fh.write(
                        f"\n[${level.level_name}]\ngvid0 = {game_vertex_id}\nid = {vertex.level_id}\n",
                    )
                else:
                    print(
                        "{"
                        + f" gvid0 = {game_vertex_id},		name = '${level.level_name}'"
                        + " },\n",
                    )

                level_id = vertex.level_id

        if fn is not None:
            fh.close()

    def gvid_by_name(self, *args):
        # rev = reverse %[self.level_by_guid];
        # for level in  (sort {$b cmp $a} keys %rev) {
        # 	if (args[0] == $level) {
        # 		return $rev[level];
        # 	}
        # }
        # return None;
        return self.level_by_guid.get(args[0], None)

    def level_name(self, *args):
        if not (args[0] is not None):
            return "_level_unknown"
        sorted_guids = list(reversed(sorted(self.level_by_guid.keys())))
        for guid in sorted_guids:
            if args[0] >= guid:
                return self.level_by_guid[guid]

        return "_level_unknown"

    # return self.level_by_guid.get(args[0], None)

    def level_id(self, *args):  # returns level id by level name
        if args[0] is None:
            return 65535
        for id in self.level_by_id.keys():
            if self.level_by_id[id].level_name == args[0]:
                return id

        return 65535

    def level_name_by_id(self, *args):  # returns level name by level id
        if not (args[0] is not None):
            return "_level_unknown"
        for id in self.level_by_id.keys():
            if args[0] == id:
                return self.level_by_id[id].level_name

        return "_level_unknown"

    def edge_block_size(self):
        ver = self.gg_version
        if ver == "soc" or ver == "cop":
            return 0x06
        return 0x08

    def vertex_block_size(*args):
        ver = gg_version.gg_version
        if ver == "1469" or ver == "1472":
            return 0x24
        if ver == "1510" or ver == "1935" or ver == "2215":
            return 0x28
        return 0x2A

    def header_size(*args):
        ver = gg_version.gg_version
        if ver == "1469" or ver == "1472":
            return 0x0C
        if ver == "1510" or ver == "1935":
            return 0x14
        if ver == "2215":
            return 0x24
        return 0x1C

    def level_graph(*args):
        return args[0].is_level_graph == 1

    def is_old(*args):
        return gg_version.gg_version == "1469" or gg_version.gg_version == "1472"

    def error_handler(self, *args):
        print("Graph seems to be a args[0] type. Reading again...\n")
        self.gg_version = args[0]
        self.levels = ()
        self.decompose()


#####################################################################
