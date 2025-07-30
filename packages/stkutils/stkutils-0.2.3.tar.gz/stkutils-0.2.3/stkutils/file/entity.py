# Module for stalker spawn reading
# Update history:
# 	06/04/2014 - LA spawn unpacking added
# 	27/08/2012 - fix code for new fail() syntax, add some new Artos stuff
#######################################################################
import os.path

from stkutils import perl_utils
from stkutils.binary_data import pack, unpack
from stkutils.chunked import chunked
from stkutils.data_packet import data_packet
from stkutils.ini_file import ini_file
from stkutils.perl_utils import fail, lc, ref, substr, universal_dict_object
from stkutils.scan_test import scan

FULL_IMPORT = 0x0


class entity(universal_dict_object):
    #
    # use scan;
    # use data_packet;
    #
    FL_LEVEL_SPAWN = 0x01
    FL_IS_2942 = 0x04
    FL_IS_25XX = 0x08
    FL_NO_FATAL = 0x10
    FL_HANDLED = 0x20
    FL_SAVE = 0x40
    FL_LA = 0x80

    # use vars qw(@ISA @EXPORT_OK);
    # require Exporter;

    # ISA		= (Exporter,)
    EXPORT_OK = (
        FL_LEVEL_SPAWN,
        FL_IS_2942,
        FL_IS_25XX,
        FL_NO_FATAL,
        FL_HANDLED,
        FL_SAVE,
        FL_LA,
    )

    def __init__(self):
        super().__init__()
        # my $class = shift;
        # my $self = universal_dict_object();
        self.cse_object = perl_utils.universal_dict_object()
        self.cse_object.client_data_path = ""
        self.cse_object.flags = 0
        self.cse_object.ini = None
        self.cse_object.user_ini = None
        self.markers = perl_utils.universal_dict_object()

    def init_abstract(self):
        cse_abstract.init(self.cse_object)

    def init_object(self):
        self.cse_object.init(self.cse_object)

    def read(self, cf: chunked, version: int):
        # my $self = shift;
        # my ($cf, $version) = **kwargs;
        if not self.level():
            if version > 79:
                while 1:
                    (index, size) = cf.r_chunk_open()
                    if index is None:
                        break
                    # defined($index) or last;
                    id = None
                    if index == 0:
                        if version < 95:
                            self.read_new(cf)
                        else:
                            (id,) = unpack("v", cf.r_chunk_data())

                    elif index == 1:
                        if version < 95:
                            (id,) = unpack("v", cf.r_chunk_data())
                        else:
                            self.read_new(cf)

                    cf.r_chunk_close()

            else:
                data = cf.r_chunk_data()
                (size16,) = unpack("v", substr(data, 0, 2))
                st_packet = data_packet(substr(data, 2, size16))
                up_packet = data_packet(substr(data, size16 + 4))
                self.read_m_spawn(st_packet)
                self.read_m_update(up_packet)

        else:
            self.read_m_spawn(data_packet(cf.r_chunk_data()))

    def read_new(self, cf):
        # my $self = shift;
        # my ($cf) = **kwargs;
        while 1:
            (index, size) = cf.r_chunk_open()
            # defined($index) or last
            if index is None:
                break
            data = cf.r_chunk_data()
            (size16,) = unpack("v", substr(data, 0, 2))
            if size16 != (size - 2):
                fail("alife object size mismatch")
            # packet = data_packet(\substr(data, 2));
            packet = data_packet(substr(data, 2))
            if index == 0:
                self.read_m_spawn(packet)
            elif index == 1:
                self.read_m_update(packet)

            cf.r_chunk_close()

    def read_m_spawn(self, packet):
        # my $self = shift;
        # my ($packet) = **kwargs;
        self.init_abstract()
        cse_abstract.state_read(self.cse_object, packet)
        sName = lc(self.cse_object.section_name)
        class_name = None
        if self.cse_object.user_ini is not None:
            class_name = self.cse_object.user_ini.value("sections", f"'{sName}'")
        if self.cse_object.ini is not None and class_name is None:
            class_name = self.cse_object.ini.value("sections", f"'{sName}'")
        if class_name is None:
            class_name = scan.get_class(sName)
        if class_name is None:
            fail("unknown class for section " + self.cse_object.section_name)

        self.cse_object: universal_dict_object = perl_utils.bless(
            self.cse_object,
            class_name,
            globals(),
        )
        # print(f"{class_name} ({self.cse_object.name})\n")
        if not hasattr(self.cse_object, "state_read"):
            fail(
                "unknown clsid "
                + class_name
                + " for section "
                + self.cse_object.section_name,
            )
        # handle SCRPTZN
        if self.cse_object.version > 118:
            if sName == "sim_faction":
                # bless self.cse_object, 'se_sim_faction'
                perl_utils.bless(self.cse_object, "se_sim_faction", globals())
                # self.cse_object = se_sim_faction()

        # handle wrong classes for weapon in ver 118
        if self.cse_object.version == 118 and self.cse_object.script_version > 5:
            # soc
            if "ak74u" in sName or "vintore" in sName:
                self.cse_object = perl_utils.bless(
                    self.cse_object,
                    "cse_alife_item_weapon_magazined",
                    globals(),
                )
                # self.cse_objec = cse_alife_item_weapon_magazined()

        self.init_object()
        self.cse_object.state_read(self.cse_object, packet)
        # shut up warnings for smart covers with extra data (acdccop bug)
        if (ref(self.cse_object) == "se_smart_cover") and (packet.resid() % 2 == 0):

            if packet.resid() != 0:
                return
        # correct reading check
        if packet.resid() != 0:
            warning(
                "state data left ["
                + str(packet.resid())
                + "] in entity "
                + self.cse_object.name,
            )

    def read_m_update(self, packet):
        # my $self = shift;
        # my ($packet) = **kwargs;
        cse_abstract.update_read(self.cse_object, packet)
        if getattr(self.cse_object, "update_read", None) is not None:
            # do {self.cse_object.update_read(self, packet)};
            self.cse_object.update_read(self.cse_object, packet)
        if packet.resid() != 0:
            self.error("update data left")
            # self.error('.read_m_update', 'packet.resid() == 0',
            #            'update data left [' + str(packet.resid()) + '] in entity ' + str(self.cse_object.name))

    def write(self, cf, object_id):
        # my $self = shift;
        # my ($cf, $object_id) = **kwargs;
        if not self.level():
            if self.version() > 79:
                if self.version() > 94:
                    cf.w_chunk(0, pack("v", object_id))
                    cf.w_chunk_open(1)
                else:
                    cf.w_chunk_open(0)

                cf.w_chunk_open(0)
                self.write_m_spawn(cf, object_id)
                cf.w_chunk_close()

                cf.w_chunk_open(1)
                self.write_m_update(cf)
                cf.w_chunk_close()

                cf.w_chunk_close()
                if self.version() <= 94:
                    cf.w_chunk(1, pack("v", object_id))

            else:
                self.write_m_spawn(cf, object_id)
                self.write_m_update(cf)

        else:
            object_id = 0xFFFF
            if self.cse_object.section_name == "graph_point":
                object_id = 0xCCCC

            self.write_m_spawn(cf, object_id)

    def write_m_spawn(self, cf, object_id):
        # my $self = shift;
        # my ($cf, $object_id) = **kwargs;
        obj_packet = data_packet(b"")
        self.cse_object.state_write(self.cse_object, obj_packet, None, None)
        abs_packet = data_packet(b"")
        cse_abstract.state_write(
            self.cse_object,
            abs_packet,
            object_id,
            perl_utils.length(obj_packet.data) + 2,
        )
        if not self.level():
            cf.w_chunk_data(
                pack(
                    "v",
                    perl_utils.length(abs_packet.data)
                    + perl_utils.length(obj_packet.data),
                ),
            )
        cf.w_chunk_data(abs_packet.data)
        cf.w_chunk_data(obj_packet.data)

    def write_m_update(self, cf):
        # my $self = shift;
        # my ($cf) = **kwargs;
        obj_upd_packet = data_packet()
        if hasattr(self.cse_object, "update_write"):
            # do {$self.cse_object.update_write($obj_upd_packet);};
            self.cse_object.update_write(self.cse_object, obj_upd_packet)
        abs_upd_packet = data_packet()
        cse_abstract.update_write(self.cse_object, abs_upd_packet)
        cf.w_chunk_data(
            pack(
                "v",
                perl_utils.length(abs_upd_packet.data)
                + perl_utils.length(obj_upd_packet.data),
            ),
        )
        cf.w_chunk_data(abs_upd_packet.data)
        cf.w_chunk_data(obj_upd_packet.data)

    def import_ltx(self, _if, section, import_type=FULL_IMPORT):
        # my $self = shift;
        # my ($if, $section, $import_type) = **kwargs;
        self.init_abstract()
        cse_abstract.state_import(self.cse_object, _if, section, import_type)
        sName = lc(self.cse_object.section_name)
        # my $class_name;
        class_name = None
        if self.cse_object.user_ini is not None:
            if self.cse_object.user_ini is not None:
                class_name = self.cse_object.user_ini.value("sections", f"'{sName}'")
        if self.cse_object.ini is not None and class_name is None:
            class_name = self.cse_object.ini.value("sections", f"'{sName}'")
        if class_name is None:
            class_name = scan.get_class(sName)
        if class_name is None:
            fail("unknown class for section " + self.cse_object.section_name)
        # bless self.cse_object, class_name;
        self.cse_object = perl_utils.bless(self.cse_object, class_name, globals())
        if not hasattr(self.cse_object, "state_import"):
            fail(
                "unknown clsid "
                + class_name
                + " for section "
                + self.cse_object.section_name,
            )
        if self.cse_object.version < 122:
            if class_name == "se_sim_faction":
                self.cse_object = cse_alife_space_restrictor()
            # bless self.cse_object, 'cse_alife_space_restrictor'

        if self.cse_object.version == 118 and self.cse_object.script_version > 5:
            if "ak74u" in sName or "vintore" in sName:
                # self.cse_object = cse_alife_item_weapon_magazined()
                self.cse_object = perl_utils.bless(
                    self.cse_object,
                    "cse_alife_item_weapon_magazined",
                    globals(),
                )

        self.init_object()
        self.cse_object.state_import(self.cse_object, _if, section, import_type)
        if hasattr(self.cse_object, "update_import"):
            if not self.level():
                self.cse_object.update_import(self.cse_object, _if, section)

    # do {$self.cse_object.update_import($if, $section)}

    def export_ltx(self, _if, id):
        # my $self = shift;
        # my ($if, $id) = **kwargs;

        fh = _if.fh
        fh.write(f"[{id}]\n")
        cse_abstract.state_export(self.cse_object, _if)
        self.cse_object.state_export(self.cse_object, _if)
        if hasattr(self.cse_object, "update_export"):
            if not self.level():
                self.cse_object.update_export(self.cse_object, _if)
        # and do {$self.cse_object.update_export($if)} if !$self.level();
        fh.write(
            "\n;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n\n",
        )

    @classmethod
    def init_properties(cls, self, args):
        # my $self = shift;
        for p in args:
            prop_exists = (
                p["name"]
                in self
                # (isinstance(self, dict) and p["name"] in self)
                # or hasattr(self, p["name"])
            )
            if prop_exists:
                continue
            # next if defined $self.{$p.name};
            if p.get("default", None) is not None:
                setattr(self, p["name"], p["default"])

    def version(self):
        return self.cse_object.version

    def level(self):
        if self.cse_object.flags & self.FL_LEVEL_SPAWN:
            return 1

        return 0

    def error(self, *args):
        # my $self = shift;
        if not (self.cse_object.flags & self.FL_NO_FATAL):
            fail(*args)
        else:
            warning(*args)


################


class base_entity(universal_dict_object):
    @classmethod
    def init(cls, obj):
        pass

    @classmethod
    def state_read(cls, self, packet: data_packet):
        pass

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        pass

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        pass

    @classmethod
    def state_export(cls, self, _if: ini_file):
        pass

    @classmethod
    def update_read(cls, self, packet: data_packet):
        pass

    @classmethod
    def update_write(cls, self, packet: data_packet):
        pass

    @classmethod
    def update_import(cls, self, _if, section):
        pass

    @classmethod
    def update_export(cls, self, _if):
        pass


#######################################################


class client_data:
    def __init__(self, packet: data_packet | None = None, size=None):
        super().__init__()
        # my $class = shift;
        # my ($packet, $size) = **kwargs;
        # my $self = universal_dict_object();
        self.pstor = []
        self.weather_manager = universal_dict_object()
        self.treasure_manager = universal_dict_object()
        self.task_manager = universal_dict_object()
        self.psy_antenna = universal_dict_object()
        self.data = ""
        if packet:

            self.data = substr(packet.data(), packet.pos(), size)
            packet.pos(packet.pos() + size)

    # if ($#_ == 1) {
    # 	$self.data = \substr($packet.data(), $packet.pos(), $size);
    # 	$packet.pos($packet.pos() + $size);
    # }
    # bless $self, $class;
    # return $self;

    # def data(self):
    # 	return $_[0].data if $#_ == 0;
    # 	$_[0].data = $_[1];

    def read(self):
        # my $self = shift;
        return  # temporarily

    # my $packet = data_packet($self.data());
    #
    # #биндер
    # $self.read_object_binder($packet);
    #
    # #сложность игры
    # $self.game_difficulty = $packet.unpack('C', 1);
    # my $load_treasure_manager = 0;
    # if ($self.game_difficulty >= 128) {
    # 	$self.game_difficulty -= 128;
    # 	$load_treasure_manager = 1;
    # }
    # #время
    # $self.stored_input_time = $packet.unpack('C', 1);
    # if ($self.stored_input_time == 1) {
    # 	$self.disable_input_time = $packet.unpack_ctime();
    # }
    # #пстор
    # $self.read_pstor($packet);
    #
    # #погода
    # ($self.weather_manager.update_level, $self.weather_manager.update_time) = $packet.unpack('Z*V');
    #
    # #пси-антенна
    # $self.read_psy_antenna($packet);
    #
    # #менеджер тайников
    # if ($load_treasure_manager == 1) {
    # 	$self.read_treasure_manager($packet);
    # }
    #
    # #менеджер заданий
    # $self.read_task_manager($packet);
    #
    # #детектор
    # my ($dflag) = $packet.unpack('C', 1);
    # if ($dflag == 1) {
    # 	$self.detector{init_time} = $packet.unpack_ctime();
    # 	$self.detector{last_update_time} = $packet.unpack_ctime();
    # }

    def read_object_binder(self, packet):
        # my $self = shift;
        # my ($packet) = **kwargs;
        binder = self.object_binder
        # CEntityAlive
        binder.st_enable_state = packet.unpack("C", 1)
        # ???
        # CInventoryOwner
        binder.m_tmp_active_slot_num = packet.unpack("C", 1)
        binder.start_dialog = packet.unpack("Z*")
        binder.m_game_name = packet.unpack("Z*")
        binder.money = packet.unpack("V", 4)
        # CActor
        binder.m_pPhysics_support = packet.unpack("C", 1)

    def read_pstor(self, packet):
        # my $self = shift;
        # my ($packet) = **kwargs;
        (size,) = packet.unpack("V", 4)
        while size > 0:
            size -= 1
            # my $var = universal_dict_object();
            (var_name, var_type) = packet.unpack("Z*C")
            if var_type == 0:
                (var_value,) = packet.unpack("V")
            elif var_type == 1:
                (var_value,) = packet.unpack("Z*")
            elif var_type == 2:
                (var_value,) = packet.unpack("C")
            else:
                raise ValueError(f"Unknown type {var_type=}")
            var = object()
            var.type = var_type
            var.name = var_name
            var.value = var_value
            self.pstor.append(var)

    def read_psy_antenna(self, packet):
        # my $self = shift;
        # my ($packet) = **kwargs;
        (flag,) = packet.unpack("C", 1)
        if flag == 1:
            ant = self.psy_antenna
            (
                ant.hit_intensity,
                ant.sound_intensity,
                ant.sound_intensity_base,
                ant.mute_sound_threshold,
                ant.postprocess_count,
            ) = packet.unpack("ffffC", 13)
            for i in range(ant.postprocess_count):
                pp = universal_dict_object()
                (pp.k, pp.ii, pp.ib, pp.idx) = packet.unpack("Z*ffV")
                ant.postprocesses.append(pp)

    def read_treasure_manager(self, packet):
        # my $self = shift;
        # my ($packet) = **kwargs;

        (count,) = packet.unpack("v", 2)
        while count > 0:
            count -= 1
            tr = universal_dict_object()
            (tr.target, tr.active, tr.done) = packet.unpack("VCC", 4)
            self.treasure_manager.append(tr)

    def read_task_manager(self, packet):
        # my $self = shift;
        # my ($packet) = **kwargs;
        (task_count,) = packet.unpack("C", 1)
        for i in range(task_count):
            task = universal_dict_object()
            (
                task.id,
                task.enabled,
                task.enabled_props,
                task.status,
                task.selected_target,
            ) = packet.unpack("Z*CCZ*l")
            task.last_task_time = packet.unpack_ctime()
            self.task_manager["full"].append(task)

        (active_task_count,) = packet.unpack("C", 1)
        for i in range(active_task_count):
            task = universal_dict_object()
            (task.type, task.active_task_by_type) = packet.unpack("Z*Z*")
            self.task_manager["active"].push(task)

    def prepare(self, packet):
        # my $self = shift;
        # my ($packet) = **kwargs;
        return  # temporarily

    # $self.write_pstor($packet);

    def write(self, packet):
        # my $self = shift;
        # my ($packet) = **kwargs;
        self.prepare(packet)
        packet.data(packet.data()[self.data])

    def _import(self, client_data_path, id, name):
        # my ($self, $client_data_path, $id, $name) = **kwargs;
        fpath = str(client_data_path) + "/" + str(id) + "_" + str(name) + ".bin"
        if not os.path.exists(fpath):
            return
        fh = open(fpath, "rb")  # or return;
        # binmode $fh;
        data = ""
        data = fh.read()
        self.data = data
        fh.close()

    def export(self, client_data_path, id, name):
        # my ($self, $client_data_path, $id, $name) = **kwargs;
        fh = open(
            str(client_data_path) + "/" + str(id) + "_" + str(name) + ".bin",
            "wb",
        )
        # binmode $fh;
        fh.write(self.data)  # , length(${$self.data}));
        fh.close()

    def write_pstor(self, packet):
        # my $self = shift;
        # my ($packet) = **kwargs;
        packet.pack("V", len(self.pstor))
        for pstor in self.pstor:
            packet.pack("Z*C", pstor.name, pstor.type)
            if pstor.type == 0:
                packet.pack("V", pstor.value)
            elif pstor.type == 1:
                packet.pack("Z*", pstor.value)
            elif pstor.type == 2:
                packet.pack("C", pstor.value)


#####################################
# class cse_abstract(base_entity):
class cse_abstract(base_entity):
    FL_SAVE = 0x40
    #
    #
    ####	enum s_gameid
    # use constant	GAME_ANY		=> 0;
    # use constant	GAME_SINGLE		=> 0x01;
    # use constant	GAME_DEATHMATCH	=> 0x02;
    # use constant	GAME_CTF		=> 0x03;
    # use constant	GAME_ASSAULT	=> 0x04;
    # use constant	GAME_CS			=> 0x05;
    # use constant	GAME_TEAMDEATHMATCH	=> 0x06;
    # use constant	GAME_ARTEFACTHUNT	=> 0x07;
    # use constant	GAME_LASTSTANDING	=> 0x64;
    # use constant	GAME_DUMMY		=> 0xFF;
    ####	enum s_flags
    FL_SPAWN_ENABLED = 0x01
    FL_SPAWN_ON_SURGE_ONLY = 0x02
    FL_SPAWN_SINGLE_ITEM_ONLY = 0x04
    FL_SPAWN_IF_DESTROYED_ONLY = 0x08
    FL_SPAWN_INFINITE_COUNT = 0x10
    FL_SPAWN_DESTROY_ON_SPAWN = 0x20

    FULL_IMPORT = 0x0
    NO_VERTEX_IMPORT = 0x1

    properties_info = (
        {"name": "dummy16", "type": "h16", "default": 0x0001},
        {"name": "section_name", "type": "sz", "default": ""},
        {"name": "name", "type": "sz", "default": ""},
        {"name": "s_gameid", "type": "h8", "default": 0},
        {"name": "s_rp", "type": "h8", "default": 0xFE},
        {"name": "position", "type": "f32v3", "default": []},
        {"name": "direction", "type": "f32v3", "default": []},
        {"name": "respawn_time", "type": "h16", "default": 0},
        {"name": "id", "type": "u16", "default": 0},
        {"name": "parent_id", "type": "u16", "default": 65535},
        {"name": "phantom_id", "type": "u16", "default": 65535},
        {"name": "s_flags", "type": "h16", "default": 0x21},
        {"name": "version", "type": "u16", "default": 0},
        {"name": "cse_abstract__unk1_u16", "type": "h16", "default": 0xFFFF},
        {"name": "script_version", "type": "u16", "default": 0},
        {"name": "spawn_probability", "type": "f32", "default": 1.00},
        {"name": "spawn_flags", "type": "u32", "default": 31},
        {"name": "spawn_control", "type": "sz", "default": ""},
        {"name": "max_spawn_count", "type": "u32", "default": 1},
        {"name": "spawn_count", "type": "u32", "default": 0},
        {
            "name": "last_spawn_time_old",
            "type": "u8v8",
            "default": [0, 0, 0, 0, 0, 0, 0, 0],
        },
        {
            "name": "min_spawn_interval",
            "type": "u8v8",
            "default": [0, 0, 0, 0, 0, 0, 0, 0],
        },
        {
            "name": "max_spawn_interval",
            "type": "u8v8",
            "default": [0, 0, 0, 0, 0, 0, 0, 0],
        },
        {"name": "spawn_id", "type": "u16", "default": 0xFFFF},
    )

    @classmethod
    def init(cls, obj):
        entity.init_properties(obj, cse_abstract.properties_info)

    @classmethod
    def state_read(cls, self: universal_dict_object, packet):
        # my $self = shift;
        # my ($packet) = **kwargs;
        packet.unpack_properties(self, cse_abstract.properties_info[0])
        if self.dummy16 != 1:
            fail("cannot open M_SPAWN!")  # if $self.{'dummy16'} != 1;
        packet.unpack_properties(self, *(cse_abstract.properties_info[1 : 11 + 1]))
        if self.s_flags & cls.FL_SPAWN_DESTROY_ON_SPAWN:
            packet.unpack_properties(self, cse_abstract.properties_info[12])

        if self.version > 120:
            packet.unpack_properties(self, cse_abstract.properties_info[13])

        if self.version > 69:
            packet.unpack_properties(self, cse_abstract.properties_info[14])

        client_data_size = None
        if self.version > 93:
            (client_data_size,) = packet.unpack("v", 2)
        elif self.version > 70:
            (client_data_size,) = packet.unpack("C", 1)

        if client_data_size is not None and client_data_size != 0:
            self.client_data = client_data(packet, client_data_size)
            self.client_data.read()

        if self.version > 79:
            packet.unpack_properties(self, cse_abstract.properties_info[23])

        if self.version < 112:
            if self.version > 82:
                packet.unpack_properties(self, cse_abstract.properties_info[15])

            if self.version > 83:
                packet.unpack_properties(
                    self,
                    cse_abstract.properties_info[16 : 20 + 1],
                )

            if self.version > 84:
                packet.unpack_properties(
                    self,
                    cse_abstract.properties_info[21 : 22 + 1],
                )

        extended_size = packet.unpack("v", 2)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        # my $self = shift;
        # my ($packet, $spawn_id, $extended_size) = **kwargs;
        packet.pack_properties(self, cse_abstract.properties_info[0 : 11 + 1])
        if self.s_flags & cse_abstract.FL_SPAWN_DESTROY_ON_SPAWN:
            packet.pack_properties(self, cse_abstract.properties_info[12])

        if self.version > 120:
            packet.pack_properties(self, cse_abstract.properties_info[13])

        if self.version > 69:
            packet.pack_properties(self, cse_abstract.properties_info[14])

        _len = 0
        if (
            self.client_data is not None
            and self.client_data.data is not None
            and self.client_data.data != ""
        ):
            _len = len(self.client_data.data())
        # $len = 0 if !defined $len;
        if self.version > 93:
            packet.pack("v", _len)
        elif self.version > 70:
            packet.pack("C", _len)
        if (
            self.client_data is not None
            and self.client_data.data is not None
            and self.client_data.data != ""
        ):
            self.client_data.write(
                packet,
            )  # if (defined $self.client_data.data and $self.client_data.data ne '');
        if self.version > 79:
            if self.flags & cse_abstract.FL_SAVE:
                packet.pack_properties(self, cse_abstract.properties_info[23])
            else:
                packet.pack("v", spawn_id)

        if self.version < 112:
            if self.version > 82:
                packet.pack_properties(self, cse_abstract.properties_info[15])

            if self.version > 83:
                packet.pack_properties(self, cse_abstract.properties_info[16 : 20 + 1])

            if self.version > 84:
                packet.pack_properties(self, cse_abstract.properties_info[21 : 22 + 1])

        packet.pack("v", extended_size)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        (size,) = packet.unpack("v", 2)
        if size != 0:
            fail("cannot open M_UPDATE!")  # unless $size == 0;

    @classmethod
    def update_write(cls, self, packet: data_packet):
        packet.pack("v", 0)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, arg3=FULL_IMPORT):
        _if.import_properties(section, self, cse_abstract.properties_info[0 : 11 + 1])
        if (self.s_flags & cse_abstract.FL_SPAWN_DESTROY_ON_SPAWN) and (
            arg3 == cse_abstract.FULL_IMPORT
        ):
            _if.import_properties(section, self, cse_abstract.properties_info[12])

        if self.version > 120:
            _if.import_properties(section, self, cse_abstract.properties_info[13])

        if (self.version > 69) and (arg3 == cse_abstract.FULL_IMPORT):
            _if.import_properties(section, self, cse_abstract.properties_info[14])

        if self.version < 112:
            if self.version > 82:
                _if.import_properties(section, self, cse_abstract.properties_info[15])

            if self.version > 83:
                _if.import_properties(
                    section,
                    self,
                    cse_abstract.properties_info[16 : 20 + 1],
                )

            if self.version > 84:
                _if.import_properties(
                    section,
                    self,
                    cse_abstract.properties_info[21 : 22 + 1],
                )

        if self.version > 79:
            _if.import_properties(section, self, cse_abstract.properties_info[23])

        self.client_data = client_data()
        self.client_data._import(self.client_data_path, self.id, self.name)

    @classmethod
    def state_export(cls, self, _if: ini_file, arg2=None):
        _if.export_properties(
            cse_abstract.__name__,
            self,
            cse_abstract.properties_info[0 : 11 + 1],
        )
        if self.s_flags & cse_abstract.FL_SPAWN_DESTROY_ON_SPAWN:
            _if.export_properties(None, self, cse_abstract.properties_info[12])

        if self.version > 120:
            _if.export_properties(None, self, cse_abstract.properties_info[13])

        if self.version > 69:
            _if.export_properties(None, self, cse_abstract.properties_info[14])

        if self.version < 112:
            if self.version > 82:
                _if.export_properties(None, self, cse_abstract.properties_info[15])

            if self.version > 83:
                _if.export_properties(
                    None,
                    self,
                    cse_abstract.properties_info[16 : 20 + 1],
                )

            if self.version > 84:
                _if.export_properties(
                    None,
                    self,
                    cse_abstract.properties_info[21 : 22 + 1],
                )

        if self.version > 79:
            _if.export_properties(arg2, self, cse_abstract.properties_info[23])

        if self.client_data is not None and self.client_data.data != "":
            self.client_data.export(self.client_data_path, self.id, self.name)


#######################################################################
class cse_alife_graph_point(base_entity):
    properties_info = (
        {"name": "connection_point_name", "type": "sz", "default": ""},
        {"name": "connection_level_id", "type": "s32", "default": -1},
        {"name": "connection_level_name", "type": "sz", "default": ""},
        {"name": "location0", "type": "u8", "default": 0},
        {"name": "location1", "type": "u8", "default": 0},
        {"name": "location2", "type": "u8", "default": 0},
        {"name": "location3", "type": "u8", "default": 0},
    )

    @classmethod
    def init(cls, self):
        entity.init_properties(self, cse_alife_graph_point.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        packet.unpack_properties(self, cse_alife_graph_point.properties_info[0])
        if self.version > 33:
            packet.unpack_properties(self, cse_alife_graph_point.properties_info[2])
        else:
            packet.unpack_properties(self, cse_alife_graph_point.properties_info[1])

        packet.unpack_properties(self, cse_alife_graph_point.properties_info[3 : 6 + 1])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        packet.pack_properties(self, cse_alife_graph_point.properties_info[0])
        if self.version > 33:
            packet.pack_properties(self, cse_alife_graph_point.properties_info[2])
        else:
            packet.pack_properties(self, cse_alife_graph_point.properties_info[1])

        packet.pack_properties(self, cse_alife_graph_point.properties_info[3 : 6 + 1])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        _if.import_properties(section, self, cse_alife_graph_point.properties_info[0])
        if self.version > 33:
            _if.import_properties(
                section,
                self,
                cse_alife_graph_point.properties_info[2],
            )
        else:
            _if.import_properties(
                section,
                self,
                cse_alife_graph_point.properties_info[1],
            )

        _if.import_properties(
            section,
            self,
            cse_alife_graph_point.properties_info[3 : 6 + 1],
        )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        _if.export_properties(
            cse_alife_graph_point.__name__,
            self,
            cse_alife_graph_point.properties_info[0],
        )
        if self.version > 33:
            _if.export_properties(None, self, cse_alife_graph_point.properties_info[2])
        else:
            _if.export_properties(None, self, cse_alife_graph_point.properties_info[1])

        _if.export_properties(
            None,
            self,
            cse_alife_graph_point.properties_info[3 : 6 + 1],
        )


#######################################################################
class cse_shape(base_entity):
    properties_info = ({"name": "shapes", "type": "shape", "default": {}},)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        packet.unpack_properties(self, cse_shape.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        packet.pack_properties(self, cse_shape.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        _if.import_properties(section, self, cse_shape.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        _if.export_properties(cse_shape.__name__, self, cse_shape.properties_info)


#######################################################################
class cse_visual(base_entity):
    flObstacle = 0x01
    properties_info = (
        {"name": "visual_name", "type": "sz", "default": ""},
        {"name": "visual_flags", "type": "h8", "default": 0},
    )

    @classmethod
    def init(cls, self):
        entity.init_properties(self, cse_visual.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        packet.unpack_properties(self, cse_visual.properties_info[0])
        if self.version >= 104:
            packet.unpack_properties(self, cse_visual.properties_info[1])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        packet.pack_properties(self, cse_visual.properties_info[0])
        if self.version >= 104:
            packet.pack_properties(self, cse_visual.properties_info[1])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        _if.import_properties(section, self, cse_visual.properties_info[0])
        if self.version >= 104:
            _if.import_properties(section, self, cse_visual.properties_info[1])

    @classmethod
    def state_export(cls, self, _if: ini_file):
        _if.export_properties(cse_visual.__name__, self, cse_visual.properties_info[0])
        if self.version >= 104:
            _if.export_properties(None, self, cse_visual.properties_info[1])


#######################################################################
class cse_alife_object_dummy(base_entity):
    properties_info = (
        {"name": "cse_alife_object_dummy__unk1_u8", "type": "u8", "default": 0},
    )

    @classmethod
    def init(cls, self, **kwargs):
        entity.init_properties(self, cse_alife_object_dummy.properties_info)
        cse_visual.init(**kwargs)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        packet.unpack_properties(self, cse_alife_object_dummy.properties_info)
        cse_visual.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        packet.pack_properties(self, cse_alife_object_dummy.properties_info)
        cse_visual.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        _if.import_properties(section, self, cse_alife_object_dummy.properties_info)
        cse_visual.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        _if.export_properties(
            cse_alife_object_dummy.__name__,
            self,
            cse_alife_object_dummy.properties_info,
        )
        cse_visual.state_export(self, _if)


#######################################################################
class cse_motion(base_entity):
    properties_info = ({"name": "motion_name", "type": "sz", "default": ""},)

    @classmethod
    def init(cls, self):
        entity.init_properties(self, cse_motion.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        packet.unpack_properties(self, cse_motion.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        packet.pack_properties(self, cse_motion.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        _if.import_properties(section, self, cse_motion.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        _if.export_properties(cse_motion.__name__, self, cse_motion.properties_info)


#######################################################################
class cse_turret_mgun(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object_visual.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object_visual.state_write(
            self,
            packet,
            spawn_id,
            extended_size,
        )

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object_visual.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object_visual.state_export(self, _if)


#######################################################################
class cse_ph_skeleton(base_entity):
    properties_info = (
        {"name": "skeleton_name", "type": "sz", "default": "$editor"},
        {"name": "skeleton_flags", "type": "u8", "default": 0},
        {"name": "source_id", "type": "h16", "default": 0xFFFF},
        {"name": "skeleton", "type": "skeleton"},
    )

    @classmethod
    def init(cls, self):
        entity.init_properties(self, cse_ph_skeleton.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        packet.unpack_properties(self, cse_ph_skeleton.properties_info[0 : 2 + 1])
        if (self.skeleton_flags & 0x4) != 0:
            packet.unpack_properties(self, cse_ph_skeleton.properties_info[3])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        packet.pack_properties(self, cse_ph_skeleton.properties_info[0 : 2 + 1])
        if (self.skeleton_flags & 0x4) != 0:
            packet.pack_properties(self, cse_ph_skeleton.properties_info[3])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        _if.import_properties(section, self, cse_ph_skeleton.properties_info[0 : 2 + 1])
        if (self.skeleton_flags & 0x4) != 0:
            _if.import_properties(section, self, cse_ph_skeleton.properties_info[3])

    @classmethod
    def state_export(cls, self, _if: ini_file):
        _if.export_properties(
            cse_ph_skeleton.__name__,
            self,
            cse_ph_skeleton.properties_info[0 : 2 + 1],
        )
        if (self.skeleton_flags & 0x4) != 0:
            _if.export_properties(None, self, cse_ph_skeleton.properties_info[3])


#######################################################################
class cse_target_cs_cask(base_entity):
    properties_info = (
        {"name": "cse_target_cs_cask__unk1_u8", "type": "u8", "default": 0},
    )

    @classmethod
    def init(cls, self):
        entity.init_properties(self, cse_target_cs_cask.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        packet.unpack_properties(self, cse_target_cs_cask.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        packet.pack_properties(self, cse_target_cs_cask.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        _if.import_properties(section, self, cse_target_cs_cask.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        _if.export_properties(
            cse_target_cs_cask.__name__,
            self,
            cse_target_cs_cask.properties_info,
        )


#######################################################################
class cse_target_cs_base(base_entity):
    properties_info = (
        {"name": "cse_target_cs_base__unk1_f32", "type": "f32", "default": 0},
        {"name": "team_id", "type": "u8"},
    )

    @classmethod
    def init(cls, self):
        entity.init_properties(self, cse_target_cs_base.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        packet.unpack_properties(self, cse_target_cs_base.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        packet.pack_properties(self, cse_target_cs_base.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        _if.import_properties(section, self, cse_target_cs_base.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        _if.export_properties(
            cse_target_cs_base.__name__,
            self,
            cse_target_cs_base.properties_info,
        )


#######################################################################
class cse_alife_spawn_group(base_entity):
    properties_info = ({"name": "group_probability", "type": "f32", "default": 1.0},)

    @classmethod
    def init(cls, self):
        entity.init_properties(self, cse_alife_spawn_group.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if self.version <= 79:
            packet.unpack_properties(self, cse_alife_spawn_group.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if self.version <= 79:
            packet.pack_properties(self, cse_alife_spawn_group.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if self.version <= 79:
            _if.import_properties(section, self, cse_alife_spawn_group.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if self.version <= 79:
            _if.export_properties(
                cse_alife_spawn_group.__name__,
                self,
                cse_alife_spawn_group.properties_info,
            )


#######################################################################
class cse_alife_object(base_entity):
    flUseSwitches = 0x00000001
    flSwitchOnline = 0x00000002
    flSwitchOffline = 0x00000004
    flInteractive = 0x00000008
    flVisibleForAI = 0x00000010
    flUsefulForAI = 0x00000020
    flOfflineNoMove = 0x00000040
    flUsedAI_Locations = 0x00000080
    flUseGroupBehaviour = 0x00000100
    flCanSave = 0x00000200
    flVisibleForMap = 0x00000400
    flUseSmartTerrains = 0x00000800
    flCheckForSeparator = 0x00001000
    flCorpseRemoval = 0x00002000
    properties_info = (
        {"name": "cse_alife_object__unk1_u8", "type": "u8", "default": 0},
        {"name": "spawn_probability", "type": "f32", "default": 1.00},
        {"name": "spawn_id", "type": "s32", "default": -1},
        {"name": "cse_alife_object__unk2_u16", "type": "u16", "default": 0},
        {"name": "game_vertex_id", "type": "u16", "default": 0xFFFF},
        {"name": "distance", "type": "f32", "default": 0.0},
        {"name": "direct_control", "type": "u32", "default": 1},
        {"name": "level_vertex_id", "type": "u32", "default": 0xFFFFFFFF},
        {"name": "cse_alife_object__unk3_u16", "type": "u16", "default": 0},
        {"name": "spawn_control", "type": "sz", "default": ""},
        {"name": "object_flags", "type": "h32", "default": 0},
        {"name": "custom_data", "type": "sz", "default": ""},
        {"name": "story_id", "type": "s32", "default": -1},
        {"name": "spawn_story_id", "type": "s32", "default": -1},
    )

    @classmethod
    def init(cls, self):
        entity.init_properties(self, cse_alife_object.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if self.version <= 24:
            packet.unpack_properties(self, cse_alife_object.properties_info[0])
        elif (self.version > 24) and (self.version < 83):
            packet.unpack_properties(self, cse_alife_object.properties_info[1])

        if self.version < 83:
            packet.unpack_properties(self, cse_alife_object.properties_info[2])

        if self.version < 4:
            packet.unpack_properties(self, cse_alife_object.properties_info[3])

        packet.unpack_properties(self, cse_alife_object.properties_info[4 : 5 + 1])
        if self.version >= 4:
            packet.unpack_properties(self, cse_alife_object.properties_info[6])

        if self.version >= 8:
            packet.unpack_properties(self, cse_alife_object.properties_info[7])

        if (self.version > 22) and (self.version <= 79):
            packet.unpack_properties(self, cse_alife_object.properties_info[8])

        if (self.version > 23) and (self.version <= 84):
            packet.unpack_properties(self, cse_alife_object.properties_info[9])

        if self.version > 49:
            packet.unpack_properties(self, cse_alife_object.properties_info[10])

        if self.version > 57:
            packet.unpack_properties(self, cse_alife_object.properties_info[11])

        if self.version > 61:
            packet.unpack_properties(self, cse_alife_object.properties_info[12])

        if self.version > 111:
            packet.unpack_properties(self, cse_alife_object.properties_info[13])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if self.version <= 24:
            packet.pack_properties(self, cse_alife_object.properties_info[0])
        elif (self.version > 24) and (self.version < 83):
            packet.pack_properties(self, cse_alife_object.properties_info[1])

        if self.version < 83:
            packet.pack_properties(self, cse_alife_object.properties_info[2])

        if self.version < 4:
            packet.pack_properties(self, cse_alife_object.properties_info[3])

        packet.pack_properties(self, cse_alife_object.properties_info[4 : 5 + 1])
        if self.version >= 4:
            packet.pack_properties(self, cse_alife_object.properties_info[6])

        if self.version >= 8:
            packet.pack_properties(self, cse_alife_object.properties_info[7])

        if (self.version > 22) and (self.version <= 79):
            packet.pack_properties(self, cse_alife_object.properties_info[8])

        if (self.version > 23) and (self.version <= 84):
            packet.pack_properties(self, cse_alife_object.properties_info[9])

        if self.version > 49:
            packet.pack_properties(self, cse_alife_object.properties_info[10])

        if self.version > 57:
            packet.pack_properties(self, cse_alife_object.properties_info[11])

        if self.version > 61:
            packet.pack_properties(self, cse_alife_object.properties_info[12])

        if self.version > 111:
            packet.pack_properties(self, cse_alife_object.properties_info[13])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if self.version <= 24:
            _if.import_properties(section, self, cse_alife_object.properties_info[0])
        elif (self.version > 24) and (self.version < 83):
            _if.import_properties(section, self, cse_alife_object.properties_info[1])

        if self.version < 83:
            _if.import_properties(section, self, cse_alife_object.properties_info[2])

        if self.version < 4:
            _if.import_properties(section, self, cse_alife_object.properties_info[3])

        _if.import_properties(
            section,
            self,
            cse_alife_object.properties_info[4 : 5 + 1],
        )
        if self.version >= 4:
            _if.import_properties(section, self, cse_alife_object.properties_info[6])

        if self.version >= 8:
            _if.import_properties(section, self, cse_alife_object.properties_info[7])

        if (self.version > 22) and (self.version <= 79):
            _if.import_properties(section, self, cse_alife_object.properties_info[8])

        if (self.version > 23) and (self.version <= 84):
            _if.import_properties(section, self, cse_alife_object.properties_info[9])

        if self.version > 49:
            _if.import_properties(section, self, cse_alife_object.properties_info[10])

        if self.version > 57:
            _if.import_properties(section, self, cse_alife_object.properties_info[11])

        if self.version > 61:
            _if.import_properties(section, self, cse_alife_object.properties_info[12])

        if self.version > 111:
            _if.import_properties(section, self, cse_alife_object.properties_info[13])

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if self.version <= 24:
            _if.export_properties(
                cse_alife_object.__name__,
                self,
                cse_alife_object.properties_info[0],
            )
        elif (self.version > 24) and (self.version < 83):
            _if.export_properties(
                cse_alife_object.__name__,
                self,
                cse_alife_object.properties_info[1],
            )

        if self.version < 83:
            _if.export_properties(None, self, cse_alife_object.properties_info[2])

        if self.version < 4:
            _if.export_properties(None, self, cse_alife_object.properties_info[3])

        # my $pack;
        if self.version >= 83:
            pack = cse_alife_object.__name__
        else:
            pack = None

        _if.export_properties(pack, self, cse_alife_object.properties_info[4 : 5 + 1])
        if self.version >= 4:
            _if.export_properties(None, self, cse_alife_object.properties_info[6])

        if self.version >= 8:
            _if.export_properties(None, self, cse_alife_object.properties_info[7])

        if (self.version > 22) and (self.version <= 79):
            _if.export_properties(None, self, cse_alife_object.properties_info[8])

        if (self.version > 23) and (self.version <= 84):
            _if.export_properties(None, self, cse_alife_object.properties_info[9])

        if self.version > 49:
            _if.export_properties(None, self, cse_alife_object.properties_info[10])

        if self.version > 57:
            _if.export_properties(None, self, cse_alife_object.properties_info[11])

        if self.version > 61:
            _if.export_properties(None, self, cse_alife_object.properties_info[12])

        if self.version > 111:
            _if.export_properties(None, self, cse_alife_object.properties_info[13])


#######################################################################
class cse_alife_dynamic_object(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_object.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_object.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_object.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_object.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_object.state_export(self, _if)


#######################################################################
class cse_alife_online_offline_group(base_entity):
    properties_info = ({"name": "members", "type": "l32u16v", "default": []},)

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object.init(self)
        entity.init_properties(self, cse_alife_online_offline_group.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object.state_read(self, packet)
        packet.unpack_properties(self, cse_alife_online_offline_group.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, cse_alife_online_offline_group.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object.state_import(self, _if, section, import_type)
        _if.import_properties(
            section,
            self,
            cse_alife_online_offline_group.properties_info,
        )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object.state_export(self, _if)
        _if.export_properties(
            cse_alife_online_offline_group.__name__,
            self,
            cse_alife_online_offline_group.properties_info,
        )


#######################################################################
class cse_alife_dynamic_object_visual(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_object.init(self)
        cse_visual.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_object.state_read(self, packet)
        if self.version > 31:
            cse_visual.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_object.state_write(self, packet, spawn_id, extended_size)
        if self.version > 31:
            cse_visual.state_write(
                self,
                packet,
                spawn_id,
                extended_size,
            )  # if (self.version > 31);

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_object.state_import(self, _if, section, import_type)
        if self.version > 31:
            cse_visual.state_import(
                self,
                _if,
                section,
                import_type,
            )  # if (self.version > 31);

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_object.state_export(self, _if)
        if self.version > 31:
            cse_visual.state_export(self, _if)  # if (self.version > 31);


#######################################################################
class cse_alife_object_climable(base_entity):
    properties_info = (
        {"name": "game_material", "type": "sz", "default": "materials\\fake_ladders"},
    )

    @classmethod
    def init(cls, self):
        cse_alife_object.init(self)
        entity.init_properties(self, cse_alife_object_climable.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if self.version > 99:
            cse_alife_object.state_read(self, packet)
        cse_shape.state_read(self, packet)
        if self.version >= 128:
            packet.unpack_properties(self, cse_alife_object_climable.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if self.version > 99:
            cse_alife_object.state_write(self, packet, spawn_id, extended_size)
        cse_shape.state_write(self, packet, spawn_id, extended_size)
        if self.version >= 128:
            packet.pack_properties(self, cse_alife_object_climable.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if self.version > 99:
            cse_alife_object.state_import(self, _if, section, import_type)
        cse_shape.state_import(self, _if, section, import_type)
        if self.version >= 128:
            _if.import_properties(
                section,
                self,
                cse_alife_object_climable.properties_info,
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if self.version > 99:
            cse_alife_object.state_export(self, _if)
        cse_shape.state_export(self, _if)
        if self.version >= 128:
            _if.export_properties(
                cse_alife_object_climable.__name__,
                self,
                cse_alife_object_climable.properties_info,
            )


#######################################################################
class cse_alife_object_physic(base_entity):
    properties_info = (
        {"name": "physic_type", "type": "h32", "default": 0},
        {"name": "mass", "type": "f32", "default": 0.0},
        {"name": "fixed_bones", "type": "sz", "default": ""},
        {"name": "startup_animation", "type": "sz", "default": ""},
        {"name": "skeleton_flags", "type": "u8", "default": 0},
        {"name": "source_id", "type": "u16", "default": 65535},
    )
    upd_properties_info = (
        {"name": "upd:num_items", "type": "h8", "default": 0},
        {"name": "upd:ph_force", "type": "f32v3", "default": [0.0, 0.0, 0.0]},
        {"name": "upd:ph_torque", "type": "f32v3", "default": [0.0, 0.0, 0.0]},
        {"name": "upd:ph_position", "type": "f32v3", "default": [0.0, 0.0, 0.0]},
        {"name": "upd:ph_rotation", "type": "f32v4", "default": [0.0, 0.0, 0.0, 0.0]},
        {
            "name": "upd:ph_angular_velosity",
            "type": "f32v3",
            "default": [0.0, 0.0, 0.0],
        },
        {"name": "upd:ph_linear_velosity", "type": "f32v3", "default": [0.0, 0.0, 0.0]},
        {"name": "upd:enabled", "type": "u8", "default": 1},
    )

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)
        cse_ph_skeleton.init(self)
        entity.init_properties(self, cse_alife_object_physic.properties_info)
        entity.init_properties(self, cse_alife_object_physic.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if self.version >= 14:
            if self.version < 16:
                cse_alife_dynamic_object.state_read(self, packet)
            else:
                cse_alife_dynamic_object_visual.state_read(self, packet)

            if self.version < 32:
                cse_visual.state_read(self, packet)

        if self.version >= 64:
            cse_ph_skeleton.state_read(self, packet)

        packet.unpack_properties(
            self,
            cse_alife_object_physic.properties_info[0 : 1 + 1],
        )
        if self.version > 9:
            packet.unpack_properties(self, cse_alife_object_physic.properties_info[2])

        if (self.version > 28) and (self.version < 65):
            packet.unpack_properties(self, cse_alife_object_physic.properties_info[3])

        if self.version < 64:
            if self.version > 39:
                packet.unpack_properties(
                    self,
                    cse_alife_object_physic.properties_info[4],
                )

            if self.version > 56:
                packet.unpack_properties(
                    self,
                    cse_alife_object_physic.properties_info[5],
                )

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if self.version >= 14:
            if self.version < 16:
                cse_alife_dynamic_object.state_write(
                    self,
                    packet,
                    spawn_id,
                    extended_size,
                )
            else:
                cse_alife_dynamic_object_visual.state_write(
                    self,
                    packet,
                    spawn_id,
                    extended_size,
                )

            if self.version < 32:
                cse_visual.state_write(self, packet, spawn_id, extended_size)

        if self.version >= 64:
            cse_ph_skeleton.state_write(self, packet, spawn_id, extended_size)

        packet.pack_properties(self, cse_alife_object_physic.properties_info[0 : 1 + 1])
        if self.version > 9:
            packet.pack_properties(self, cse_alife_object_physic.properties_info[2])

        if (self.version > 28) and (self.version < 65):
            packet.pack_properties(self, cse_alife_object_physic.properties_info[3])

        if self.version < 64:
            if self.version > 39:
                packet.pack_properties(self, cse_alife_object_physic.properties_info[4])

            if self.version > 56:
                packet.pack_properties(self, cse_alife_object_physic.properties_info[5])

    @classmethod
    def update_read(cls, self, packet: data_packet):
        entity.init_properties(self, cse_alife_object_physic.upd_properties_info)
        if (self.version >= 122) and (self.version <= 128):
            packet.unpack_properties(
                self,
                cse_alife_object_physic.upd_properties_info[0],
            )
            if getattr(self, "upd:num_items") != 0:
                packet.unpack_properties(
                    self,
                    cse_alife_object_physic.upd_properties_info[1 : 4 + 1],
                )
                flags = getattr(self, "upd:num_items") >> 5
                if (flags & 0x2) == 0:
                    packet.unpack_properties(
                        self,
                        cse_alife_object_physic.upd_properties_info[5],
                    )

                if (flags & 0x4) == 0:
                    packet.unpack_properties(
                        self,
                        cse_alife_object_physic.upd_properties_info[6],
                    )

                packet.unpack_properties(
                    self,
                    cse_alife_object_physic.upd_properties_info[7],
                )  # actually bool. Dunno how to make better yet.

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        if (self.version >= 122) and (self.version <= 128):
            _if.import_properties(
                section,
                self,
                cse_alife_object_physic.upd_properties_info[0],
            )
            if getattr(self, "upd:num_items") != 0:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_physic.upd_properties_info[1 : 4 + 1],
                )
                flags = getattr(self, "upd:num_items") >> 5
                if (flags & 0x2) == 0:
                    _if.import_properties(
                        section,
                        self,
                        cse_alife_object_physic.upd_properties_info[5],
                    )

                if (flags & 0x4) == 0:
                    _if.import_properties(
                        section,
                        self,
                        cse_alife_object_physic.upd_properties_info[6],
                    )

                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_physic.upd_properties_info[7],
                )  # actually bool. Dunno how to make better yet.

    @classmethod
    def update_export(cls, self, _if: ini_file):
        if (self.version >= 122) and (self.version <= 128):
            _if.export_properties(
                None,
                self,
                cse_alife_object_physic.upd_properties_info[0],
            )
            if getattr(self, "upd:num_items") != 0:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_physic.upd_properties_info[1 : 4 + 1],
                )
                flags = getattr(self, "upd:num_items") >> 5
                if (flags & 0x2) == 0:
                    _if.export_properties(
                        None,
                        self,
                        cse_alife_object_physic.upd_properties_info[5],
                    )

                if (flags & 0x4) == 0:
                    _if.export_properties(
                        None,
                        self,
                        cse_alife_object_physic.upd_properties_info[6],
                    )

                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_physic.upd_properties_info[7],
                )

    @classmethod
    def update_write(cls, self, packet: data_packet):
        if (self.version >= 122) and (self.version <= 128):
            packet.pack_properties(self, cse_alife_object_physic.upd_properties_info[0])
            if getattr(self, "upd:num_items") != 0:
                packet.pack_properties(
                    self,
                    cse_alife_object_physic.upd_properties_info[1 : 4 + 1],
                )
                flags = getattr(self, "upd:num_items") >> 5
                if (flags & 0x2) == 0:
                    packet.pack_properties(
                        self,
                        cse_alife_object_physic.upd_properties_info[5],
                    )

                if (flags & 0x4) == 0:
                    packet.pack_properties(
                        self,
                        cse_alife_object_physic.upd_properties_info[6],
                    )

                packet.pack_properties(
                    self,
                    cse_alife_object_physic.upd_properties_info[7],
                )  # actually bool. Dunno how to make better yet.

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if self.version >= 14:
            if self.version < 16:
                cse_alife_dynamic_object.state_import(self, _if, section, import_type)
            else:
                cse_alife_dynamic_object_visual.state_import(
                    self,
                    _if,
                    section,
                    import_type,
                )

            if self.version < 32:
                cse_visual.state_import(self, _if, section, import_type)

        if self.version >= 64:
            cse_ph_skeleton.state_import(self, _if, section, import_type)

        _if.import_properties(
            section,
            self,
            cse_alife_object_physic.properties_info[0 : 1 + 1],
        )
        if self.version > 9:
            _if.import_properties(
                section,
                self,
                cse_alife_object_physic.properties_info[2],
            )

        if (self.version > 28) and (self.version < 65):
            _if.import_properties(
                section,
                self,
                cse_alife_object_physic.properties_info[3],
            )

        if self.version < 64:
            if self.version > 39:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_physic.properties_info[4],
                )

            if self.version > 56:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_physic.properties_info[5],
                )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if self.version >= 14:
            if self.version < 16:
                cse_alife_dynamic_object.state_export(self, _if)
            else:
                cse_alife_dynamic_object_visual.state_export(self, _if)

            if self.version < 32:
                cse_visual.state_export(self, _if)

        if self.version >= 64:
            cse_ph_skeleton.state_export(self, _if)

        _if.export_properties(
            cse_alife_object_physic.__name__,
            self,
            cse_alife_object_physic.properties_info[0 : 1 + 1],
        )
        if self.version > 9:
            _if.export_properties(
                None,
                self,
                cse_alife_object_physic.properties_info[2],
            )

        if (self.version > 28) and (self.version < 65):
            _if.export_properties(
                None,
                self,
                cse_alife_object_physic.properties_info[3],
            )

        if self.version < 64:
            if self.version > 39:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_physic.properties_info[4],
                )

            if self.version > 56:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_physic.properties_info[5],
                )


#######################################################################
class cse_alife_object_hanging_lamp(base_entity):
    flPhysic = 0x0001
    flCastShadow = 0x0002
    flR1 = 0x0004
    flR2 = 0x0008
    flTypeSpot = 0x0010
    flPointAmbient = 0x0020
    properties_info = (
        {"name": "main_color", "type": "h32", "default": 0x00FFFFFF},
        {"name": "main_brightness", "type": "f32", "default": 0.0},
        {"name": "main_color_animator", "type": "sz", "default": ""},
        {"name": "cse_alife_object_hanging_lamp__unk1_sz", "type": "sz", "default": ""},
        {"name": "cse_alife_object_hanging_lamp__unk2_sz", "type": "sz", "default": ""},
        {"name": "main_range", "type": "f32", "default": 0.0},
        {"name": "light_flags", "type": "h16", "default": 0},
        {
            "name": "cse_alife_object_hanging_lamp__unk3_f32",
            "type": "f32",
            "default": 0,
        },
        {"name": "animation", "type": "sz", "default": "$editor"},
        {"name": "cse_alife_object_hanging_lamp__unk4_sz", "type": "sz", "default": ""},
        {
            "name": "cse_alife_object_hanging_lamp__unk5_f32",
            "type": "f32",
            "default": 0,
        },
        {"name": "lamp_fixed_bones", "type": "sz", "default": ""},
        {"name": "health", "type": "f32", "default": 1.0},
        {"name": "main_virtual_size", "type": "f32", "default": 0.0},
        {"name": "ambient_radius", "type": "f32", "default": 0.0},
        {"name": "ambient_power", "type": "f32", "default": 0.0},
        {"name": "ambient_texture", "type": "sz", "default": ""},
        {"name": "main_texture", "type": "sz", "default": ""},
        {"name": "main_bone", "type": "sz", "default": ""},
        {"name": "main_cone_angle", "type": "f32", "default": 0.0},
        {"name": "glow_texture", "type": "sz", "default": ""},
        {"name": "glow_radius", "type": "f32", "default": 0.0},
        {"name": "ambient_bone", "type": "sz", "default": ""},
        {
            "name": "cse_alife_object_hanging_lamp__unk6_f32",
            "type": "f32",
            "default": 0.0,
        },
        {
            "name": "cse_alife_object_hanging_lamp__unk7_f32",
            "type": "f32",
            "default": 0.0,
        },
        {
            "name": "cse_alife_object_hanging_lamp__unk8_f32",
            "type": "f32",
            "default": 0.0,
        },
        {"name": "main_cone_angle_old_format", "type": "q8", "default": 0.0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)
        cse_ph_skeleton.init(self)
        entity.init_properties(self, cse_alife_object_hanging_lamp.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if self.version > 20:
            cse_alife_dynamic_object_visual.state_read(self, packet)

        if self.version >= 69:
            cse_ph_skeleton.state_read(self, packet)

        if self.version < 32:
            cse_visual.state_read(self, packet)

        if self.version < 49:
            packet.unpack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[0],
            )
            packet.unpack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[2 : 5 + 1],
            )
            packet.unpack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[26],
            )
            if self.version > 10:
                packet.unpack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[1],
                )

            if self.version > 11:
                packet.unpack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[6],
                )

            if self.version > 12:
                packet.unpack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[7],
                )

            if self.version > 17:
                packet.unpack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[8],
                )

            if self.version > 42:
                packet.unpack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[9 : 10 + 1],
                )

            if self.version > 43:
                packet.unpack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[11],
                )

            if self.version > 44:
                packet.unpack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[12],
                )

        else:
            packet.unpack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[0 : 2 + 1],
            )
            packet.unpack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[5 : 6 + 1],
            )
            packet.unpack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[8],
            )
            packet.unpack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[11 : 12 + 1],
            )

        if self.version > 55:
            packet.unpack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[13 : 21 + 1],
            )

        if self.version > 96:
            packet.unpack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[22],
            )

        if self.version > 118:
            packet.unpack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[23 : 25 + 1],
            )

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if self.version > 20:
            cse_alife_dynamic_object_visual.state_write(
                self,
                packet,
                spawn_id,
                extended_size,
            )

        if self.version >= 69:
            cse_ph_skeleton.state_write(self, packet, spawn_id, extended_size)

        if self.version < 32:
            cse_visual.state_write(self, packet, spawn_id, extended_size)

        if self.version < 49:
            packet.pack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[0],
            )
            packet.pack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[2 : 5 + 1],
            )
            packet.pack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[26],
            )
            if self.version > 10:
                packet.pack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[1],
                )

            if self.version > 11:
                packet.pack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[6],
                )

            if self.version > 12:
                packet.pack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[7],
                )

            if self.version > 17:
                packet.pack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[8],
                )

            if self.version > 42:
                packet.pack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[9 : 10 + 1],
                )

            if self.version > 43:
                packet.pack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[11],
                )

            if self.version > 44:
                packet.pack_properties(
                    self,
                    cse_alife_object_hanging_lamp.properties_info[12],
                )

        else:
            packet.pack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[0 : 2 + 1],
            )
            packet.pack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[5 : 6 + 1],
            )
            packet.pack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[8],
            )
            packet.pack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[11 : 12 + 1],
            )

        if self.version > 55:
            packet.pack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[13 : 21 + 1],
            )

        if self.version > 96:
            packet.pack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[22],
            )

        if self.version > 118:
            packet.pack_properties(
                self,
                cse_alife_object_hanging_lamp.properties_info[23 : 25 + 1],
            )

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if self.version > 20:
            cse_alife_dynamic_object_visual.state_import(
                self,
                _if,
                section,
                import_type,
            )

        if self.version >= 69:
            cse_ph_skeleton.state_import(self, _if, section, import_type)

        if self.version < 32:
            cse_visual.state_import(self, _if, section, import_type)

        if self.version < 49:
            _if.import_properties(
                section,
                self,
                cse_alife_object_hanging_lamp.properties_info[0],
            )
            _if.import_properties(
                section,
                self,
                cse_alife_object_hanging_lamp.properties_info[2 : 5 + 1],
            )
            _if.import_properties(
                section,
                self,
                cse_alife_object_hanging_lamp.properties_info[26],
            )
            if self.version > 10:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[1],
                )

            if self.version > 11:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[6],
                )

            if self.version > 12:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[7],
                )

            if self.version > 17:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[8],
                )

            if self.version > 42:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[9 : 10 + 1],
                )

            if self.version > 43:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[11],
                )

            if self.version > 44:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[12],
                )

        else:
            _if.import_properties(
                section,
                self,
                cse_alife_object_hanging_lamp.properties_info[0 : 2 + 1],
            )
            _if.import_properties(
                section,
                self,
                cse_alife_object_hanging_lamp.properties_info[5 : 6 + 1],
            )
            _if.import_properties(
                section,
                self,
                cse_alife_object_hanging_lamp.properties_info[8],
            )
            _if.import_properties(
                section,
                self,
                cse_alife_object_hanging_lamp.properties_info[11 : 12 + 1],
            )

        if self.version > 55:
            _if.import_properties(
                section,
                self,
                cse_alife_object_hanging_lamp.properties_info[13 : 21 + 1],
            )

        if self.version > 96:
            _if.import_properties(
                section,
                self,
                cse_alife_object_hanging_lamp.properties_info[22],
            )

        if self.version > 118:
            _if.import_properties(
                section,
                self,
                cse_alife_object_hanging_lamp.properties_info[23 : 25 + 1],
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if self.version > 20:
            cse_alife_dynamic_object_visual.state_export(self, _if)

        if self.version >= 69:
            cse_ph_skeleton.state_export(self, _if)

        if self.version < 32:
            cse_visual.state_export(self, _if)

        if self.version < 49:
            _if.export_properties(
                cse_alife_object_hanging_lamp.__name__,
                self,
                cse_alife_object_hanging_lamp.properties_info[0],
            )
            _if.export_properties(
                None,
                self,
                cse_alife_object_hanging_lamp.properties_info[2 : 5 + 1],
            )
            _if.export_properties(
                None,
                self,
                cse_alife_object_hanging_lamp.properties_info[26],
            )
            if self.version > 10:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[1],
                )

            if self.version > 11:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[6],
                )

            if self.version > 12:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[7],
                )

            if self.version > 17:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[8],
                )

            if self.version > 42:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[9 : 10 + 1],
                )

            if self.version > 43:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[11],
                )

            if self.version > 44:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_hanging_lamp.properties_info[12],
                )

        else:
            _if.export_properties(
                cse_alife_object_hanging_lamp.__name__,
                self,
                cse_alife_object_hanging_lamp.properties_info[0 : 2 + 1],
            )
            _if.export_properties(
                None,
                self,
                cse_alife_object_hanging_lamp.properties_info[5 : 6 + 1],
            )
            _if.export_properties(
                None,
                self,
                cse_alife_object_hanging_lamp.properties_info[8],
            )
            _if.export_properties(
                None,
                self,
                cse_alife_object_hanging_lamp.properties_info[11 : 12 + 1],
            )

        if self.version > 55:
            _if.export_properties(
                None,
                self,
                cse_alife_object_hanging_lamp.properties_info[13 : 21 + 1],
            )

        if self.version > 96:
            _if.export_properties(
                None,
                self,
                cse_alife_object_hanging_lamp.properties_info[22],
            )

        if self.version > 118:
            _if.export_properties(
                None,
                self,
                cse_alife_object_hanging_lamp.properties_info[23 : 25 + 1],
            )


#######################################################################
class cse_alife_object_projector(base_entity):
    properties_info = (
        {"name": "main_color", "type": "h32", "default": 0x00FFFFFF},
        {"name": "main_color_animator", "type": "sz", "default": ""},
        {"name": "animation", "type": "sz", "default": "$editor"},
        {"name": "ambient_radius", "type": "f32", "default": 0.0},
        {"name": "main_cone_angle", "type": "q8", "default": 0.0},
        {"name": "main_virtual_size", "type": "f32", "default": 0.0},
        {"name": "glow_texture", "type": "sz", "default": ""},
        {"name": "glow_radius", "type": "f32", "default": 0.0},
        {"name": "cse_alife_object_hanging_lamp__unk3_u8", "type": "u16", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)
        entity.init_properties(self, cse_alife_object_projector.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object_visual.state_read(self, packet)
        if self.version < 48:
            packet.unpack_properties(
                self,
                cse_alife_object_projector.properties_info[0 : 5 + 1],
            )
            if self.version > 40:
                packet.unpack_properties(
                    self,
                    cse_alife_object_projector.properties_info[6 : 7 + 1],
                )

            if self.version > 45:
                packet.unpack_properties(
                    self,
                    cse_alife_object_projector.properties_info[8],
                )

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object_visual.state_write(
            self,
            packet,
            spawn_id,
            extended_size,
        )
        if self.version < 48:
            packet.pack_properties(
                self,
                cse_alife_object_projector.properties_info[0 : 5 + 1],
            )
            if self.version > 40:
                packet.pack_properties(
                    self,
                    cse_alife_object_projector.properties_info[6 : 7 + 1],
                )

            if self.version > 45:
                packet.pack_properties(
                    self,
                    cse_alife_object_projector.properties_info[8],
                )

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object_visual.state_import(self, _if, section, import_type)
        if self.version < 48:
            _if.import_properties(
                section,
                self,
                cse_alife_object_projector.properties_info[0 : 5 + 1],
            )
            if self.version > 40:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_projector.properties_info[6 : 7 + 1],
                )

            if self.version > 45:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_object_projector.properties_info[8],
                )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object_visual.state_export(self, _if)
        if self.version < 48:
            _if.export_properties(
                cse_alife_object_projector.__name__,
                self,
                cse_alife_object_projector.properties_info[0 : 5 + 1],
            )
            if self.version > 40:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_projector.properties_info[6 : 7 + 1],
                )

            if self.version > 45:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_object_projector.properties_info[8],
                )


#######################################################################
class cse_alife_inventory_box(base_entity):
    properties_info = (
        {"name": "cse_alive_inventory_box__unk1_u8", "type": "u8", "default": 1},
        {"name": "cse_alive_inventory_box__unk2_u8", "type": "u8", "default": 0},
        {"name": "tip", "type": "sz", "default": ""},
    )

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)
        entity.init_properties(self, cse_alife_inventory_box.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object_visual.state_read(self, packet)
        if self.version >= 128:
            packet.unpack_properties(self, cse_alife_inventory_box.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object_visual.state_write(
            self,
            packet,
            spawn_id,
            extended_size,
        )
        if self.version >= 128:
            packet.pack_properties(self, cse_alife_inventory_box.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object_visual.state_import(self, _if, section, import_type)
        if self.version >= 128:
            _if.import_properties(
                section,
                self,
                cse_alife_inventory_box.properties_info,
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object_visual.state_export(self, _if)
        if self.version >= 128:
            _if.export_properties(
                cse_alife_inventory_box.__name__,
                self,
                cse_alife_inventory_box.properties_info,
            )


#######################################################################
class cse_alife_object_breakable(base_entity):
    properties_info = ({"name": "health", "type": "f32", "default": 1.0},)

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)
        entity.init_properties(self, cse_alife_object_breakable.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object_visual.state_read(self, packet)
        packet.unpack_properties(self, cse_alife_object_breakable.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object_visual.state_write(
            self,
            packet,
            spawn_id,
            extended_size,
        )
        packet.pack_properties(self, cse_alife_object_breakable.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object_visual.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, cse_alife_object_breakable.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object_visual.state_export(self, _if)
        _if.export_properties(
            cse_alife_object_breakable.__name__,
            self,
            cse_alife_object_breakable.properties_info,
        )


#######################################################################
class cse_alife_mounted_weapon(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object_visual.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object_visual.state_write(
            self,
            packet,
            spawn_id,
            extended_size,
        )

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object_visual.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object_visual.state_export(self, _if)


#######################################################################
class cse_alife_stationary_mgun(base_entity):
    upd_properties_info = (
        {"name": "upd:working", "type": "u8", "default": 0},
        {
            "name": "upd:dest_enemy_direction",
            "type": "f32v3",
            "default": [0.0, 0.0, 0.0],
        },
    )

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)
        entity.init_properties(self, cse_alife_stationary_mgun.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object_visual.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object_visual.state_write(
            self,
            packet,
            spawn_id,
            extended_size,
        )

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object_visual.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object_visual.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        packet.unpack_properties(self, cse_alife_stationary_mgun.upd_properties_info)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        packet.pack_properties(self, cse_alife_stationary_mgun.upd_properties_info)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        _if.import_properties(
            section,
            self,
            cse_alife_stationary_mgun.upd_properties_info,
        )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        _if.export_properties(None, self, cse_alife_stationary_mgun.upd_properties_info)


#######################################################################
class cse_alife_ph_skeleton_object(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)
        cse_ph_skeleton.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object_visual.state_read(self, packet)
        if self.version >= 64:
            cse_ph_skeleton.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object_visual.state_write(
            self,
            packet,
            spawn_id,
            extended_size,
        )
        if self.version >= 64:
            cse_ph_skeleton.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object_visual.state_import(self, _if, section, import_type)
        if self.version >= 64:
            cse_ph_skeleton.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object_visual.state_export(self, _if)
        if self.version >= 64:
            cse_ph_skeleton.state_export(self, _if)


#######################################################################
class cse_alife_car(base_entity):
    properties_info = (
        {"name": "cse_alife_car__unk1_f32", "type": "f32", "default": 1.0},
        {"name": "health", "type": "f32", "default": 1.0},
        {"name": "g_team", "type": "u8", "default": 0},
        {"name": "g_squad", "type": "u8", "default": 0},
        {"name": "g_group", "type": "u8", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)
        cse_ph_skeleton.init(self)
        entity.init_properties(self, cse_alife_car.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if (self.version < 8) or (self.version > 16):
            cse_alife_dynamic_object_visual.state_read(self, packet)

        if self.version < 8:
            packet.unpack_properties(self, cse_alife_car.properties_info[2 : 4 + 1])

        if self.version > 65:
            cse_ph_skeleton.state_read(self, packet)

        if (self.version > 52) and (self.version < 55):
            packet.unpack_properties(self, cse_alife_car.properties_info[0])

        if self.version > 92:
            packet.unpack_properties(self, cse_alife_car.properties_info[1])

    # 	if (self.health > 1.0) {
    # 		self.health *= 0.01;
    # 	}

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if (self.version < 8) or (self.version > 16):
            cse_alife_dynamic_object_visual.state_write(
                self,
                packet,
                spawn_id,
                extended_size,
            )

        if self.version < 8:
            packet.pack_properties(self, cse_alife_car.properties_info[2 : 4 + 1])

        if self.version > 65:
            cse_ph_skeleton.state_write(self, packet, spawn_id, extended_size)

        if (self.version > 52) and (self.version < 55):
            packet.pack_properties(self, cse_alife_car.properties_info[0])

        if self.version > 92:
            packet.pack_properties(self, cse_alife_car.properties_info[1])

    # 	if (self.health > 1.0) {
    # 		self.health *= 0.01;
    # 	}

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if (self.version < 8) or (self.version > 16):
            cse_alife_dynamic_object_visual.state_import(
                self,
                _if,
                section,
                import_type,
            )

        if self.version < 8:
            _if.import_properties(
                section,
                self,
                cse_alife_car.properties_info[2 : 4 + 1],
            )

        if self.version > 65:
            cse_ph_skeleton.state_import(self, _if, section, import_type)

        if (self.version > 52) and (self.version < 55):
            _if.import_properties(section, self, cse_alife_car.properties_info[0])

        if self.version > 92:
            _if.import_properties(section, self, cse_alife_car.properties_info[1])

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if (self.version < 8) or (self.version > 16):
            cse_alife_dynamic_object_visual.state_export(self, _if)

        if self.version < 8:
            _if.export_properties(
                cse_alife_car.__name__,
                self,
                cse_alife_car.properties_info[2 : 4 + 1],
            )

        if self.version > 65:
            cse_ph_skeleton.state_export(self, _if)

        if (self.version > 52) and (self.version < 55):
            _if.export_properties(
                cse_alife_car.__name__,
                self,
                cse_alife_car.properties_info[0],
            )

        if self.version > 92:
            _if.export_properties(None, self, cse_alife_car.properties_info[1])


#######################################################################
class cse_alife_helicopter(base_entity):
    properties_info = (
        {"name": "cse_alife_helicopter__unk1_sz", "type": "sz", "default": ""},
        {"name": "engine_sound", "type": "sz", "default": ""},
    )

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)
        cse_ph_skeleton.init(self)
        cse_motion.init(self)
        entity.init_properties(self, cse_alife_helicopter.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object_visual.state_read(self, packet)
        cse_motion.state_read(self, packet)
        if self.version >= 69:
            cse_ph_skeleton.state_read(self, packet)

        packet.unpack_properties(self, cse_alife_helicopter.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object_visual.state_write(
            self,
            packet,
            spawn_id,
            extended_size,
        )
        cse_motion.state_write(self, packet, spawn_id, extended_size)
        if self.version >= 69:
            cse_ph_skeleton.state_write(self, packet, spawn_id, extended_size)

        packet.pack_properties(self, cse_alife_helicopter.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object_visual.state_import(self, _if, section, import_type)
        cse_motion.state_import(self, _if, section, import_type)
        if self.version >= 69:
            cse_ph_skeleton.state_import(self, _if, section, import_type)

        _if.import_properties(section, self, cse_alife_helicopter.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object_visual.state_export(self, _if)
        cse_motion.state_export(self, _if)
        if self.version >= 69:
            cse_ph_skeleton.state_export(self, _if)

        _if.export_properties(
            cse_alife_helicopter.__name__,
            self,
            cse_alife_helicopter.properties_info,
        )


#######################################################################
class cse_alife_creature_abstract(base_entity):
    FL_IS_25XX = 0x08
    properties_info = (
        {"name": "g_team", "type": "u8", "default": 0xFF},
        {"name": "g_squad", "type": "u8", "default": 0xFF},
        {"name": "g_group", "type": "u8", "default": 0xFF},
        {"name": "health", "type": "f32", "default": 1.0},
        {"name": "dynamic_out_restrictions", "type": "l32u16v", "default": []},
        {"name": "dynamic_in_restrictions", "type": "l32u16v", "default": []},
        {"name": "killer_id", "type": "h16", "default": 0xFFFF},
        {
            "name": "game_death_time",
            "type": "u8v8",
            "default": [0, 0, 0, 0, 0, 0, 0, 0],
        },
    )
    upd_properties_info = (
        {"name": "upd:health", "type": "f32", "default": -1},
        {"name": "upd:timestamp", "type": "h32", "default": 0xFFFF},
        {"name": "upd:creature_flags", "type": "h8", "default": 0xFF},
        {"name": "upd:position", "type": "f32v3", "default": []},
        {"name": "upd:o_model", "type": "f32", "default": 0},
        {"name": "upd:o_torso", "type": "f32v3", "default": [0.0, 0.0, 0.0]},
        {"name": "upd:o_model", "type": "q8", "default": 0},
        {"name": "upd:o_torso", "type": "q8v3", "default": [0, 0, 0]},
        {"name": "upd:g_team", "type": "u8", "default": 0},
        {"name": "upd:g_squad", "type": "u8", "default": 0},
        {"name": "upd:g_group", "type": "u8", "default": 0},
        {"name": "upd:health", "type": "q16", "default": 0},
        {"name": "upd:health", "type": "q16_old", "default": 0},
        {
            "name": "upd:cse_alife_creature_abstract__unk1_f32v3",
            "type": "f32v3",
            "default": [0.0, 0.0, 0.0],
        },
    )

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)
        entity.init_properties(self, cse_alife_creature_abstract.properties_info)
        entity.init_properties(self, cse_alife_creature_abstract.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object_visual.state_read(self, packet)
        packet.unpack_properties(
            self,
            cse_alife_creature_abstract.properties_info[0 : 2 + 1],
        )
        if self.version > 18:
            packet.unpack_properties(
                self,
                cse_alife_creature_abstract.properties_info[3],
            )

        if self.version < 32:
            cse_visual.state_read(self, packet)

        if self.version > 87:
            packet.unpack_properties(
                self,
                cse_alife_creature_abstract.properties_info[4 : 5 + 1],
            )

        if self.version > 94:
            packet.unpack_properties(
                self,
                cse_alife_creature_abstract.properties_info[6],
            )

        if self.version > 115:
            packet.unpack_properties(
                self,
                cse_alife_creature_abstract.properties_info[7],
            )

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object_visual.state_write(
            self,
            packet,
            spawn_id,
            extended_size,
        )
        packet.pack_properties(
            self,
            cse_alife_creature_abstract.properties_info[0 : 2 + 1],
        )
        if self.version > 18:
            packet.pack_properties(self, cse_alife_creature_abstract.properties_info[3])

        if self.version < 32:
            cse_visual.state_write(self, packet, spawn_id, extended_size)

        if self.version > 87:
            packet.pack_properties(
                self,
                cse_alife_creature_abstract.properties_info[4 : 5 + 1],
            )

        if self.version > 94:
            packet.pack_properties(self, cse_alife_creature_abstract.properties_info[6])

        if self.version > 115:
            packet.pack_properties(self, cse_alife_creature_abstract.properties_info[7])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object_visual.state_import(self, _if, section, import_type)
        _if.import_properties(
            section,
            self,
            cse_alife_creature_abstract.properties_info[0 : 2 + 1],
        )
        if self.version > 18:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_abstract.properties_info[3],
            )

        if self.version < 32:
            cse_visual.state_import(self, _if, section, import_type)

        if self.version > 87:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_abstract.properties_info[4 : 5 + 1],
            )

        if self.version > 94:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_abstract.properties_info[6],
            )

        if self.version > 115:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_abstract.properties_info[7],
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object_visual.state_export(self, _if)
        _if.export_properties(
            cse_alife_creature_abstract.__name__,
            self,
            cse_alife_creature_abstract.properties_info[0 : 2 + 1],
        )
        if self.version > 18:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_abstract.properties_info[3],
            )

        if self.version < 32:
            cse_visual.state_export(self, _if)

        if self.version > 87:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_abstract.properties_info[4 : 5 + 1],
            )

        if self.version > 94:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_abstract.properties_info[6],
            )

        if self.version > 115:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_abstract.properties_info[7],
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        if self.version > 109:
            packet.unpack_properties(
                self,
                cse_alife_creature_abstract.upd_properties_info[0],
            )
        elif self.version > 40:
            packet.unpack_properties(
                self,
                cse_alife_creature_abstract.upd_properties_info[11],
            )
        else:
            packet.unpack_properties(
                self,
                cse_alife_creature_abstract.upd_properties_info[12],
            )

        if (self.version < 17) and (ref(self) == "se_actor"):
            packet.unpack_properties(
                self,
                cse_alife_creature_abstract.upd_properties_info[13],
            )

        packet.unpack_properties(
            self,
            cse_alife_creature_abstract.upd_properties_info[1 : 3 + 1],
        )
        if (self.version > 117) and (not cse_alife_creature_abstract.is_2588(self)):
            packet.unpack_properties(
                self,
                cse_alife_creature_abstract.upd_properties_info[4 : 5 + 1],
            )
        else:
            if self.version > 85:
                packet.unpack_properties(
                    self,
                    cse_alife_creature_abstract.upd_properties_info[6],
                )

            if self.version > 63:
                packet.unpack_properties(
                    self,
                    cse_alife_creature_abstract.upd_properties_info[7],
                )

        packet.unpack_properties(
            self,
            cse_alife_creature_abstract.upd_properties_info[8 : 10 + 1],
        )

    @classmethod
    def update_write(cls, self, packet: data_packet):
        if self.version > 109:
            packet.pack_properties(
                self,
                cse_alife_creature_abstract.upd_properties_info[0],
            )
        elif self.version > 40:
            packet.pack_properties(
                self,
                cse_alife_creature_abstract.upd_properties_info[11],
            )
        else:
            packet.pack_properties(
                self,
                cse_alife_creature_abstract.upd_properties_info[12],
            )

        if (self.version < 17) and (ref(self) == "se_actor"):
            packet.pack_properties(
                self,
                cse_alife_creature_abstract.upd_properties_info[13],
            )

        packet.pack_properties(
            self,
            cse_alife_creature_abstract.upd_properties_info[1 : 3 + 1],
        )
        if (self.version > 117) and (not cse_alife_creature_abstract.is_2588(self)):
            packet.pack_properties(
                self,
                cse_alife_creature_abstract.upd_properties_info[4 : 5 + 1],
            )
        else:
            if self.version > 85:
                packet.pack_properties(
                    self,
                    cse_alife_creature_abstract.upd_properties_info[6],
                )

            if self.version > 63:
                packet.pack_properties(
                    self,
                    cse_alife_creature_abstract.upd_properties_info[7],
                )

        packet.pack_properties(
            self,
            cse_alife_creature_abstract.upd_properties_info[8 : 10 + 1],
        )

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        if self.version > 109:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_abstract.upd_properties_info[0],
            )
        elif self.version > 40:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_abstract.upd_properties_info[11],
            )
        else:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_abstract.upd_properties_info[12],
            )

        if (self.version < 17) and (ref(self) == "se_actor"):
            _if.import_properties(
                section,
                self,
                cse_alife_creature_abstract.upd_properties_info[13],
            )

        _if.import_properties(
            section,
            self,
            cse_alife_creature_abstract.upd_properties_info[1 : 3 + 1],
        )
        if (self.version > 117) and (not cse_alife_creature_abstract.is_2588(self)):
            _if.import_properties(
                section,
                self,
                cse_alife_creature_abstract.upd_properties_info[4 : 5 + 1],
            )
        else:
            if self.version > 85:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_creature_abstract.upd_properties_info[6],
                )

            if self.version > 63:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_creature_abstract.upd_properties_info[7],
                )

        _if.import_properties(
            section,
            self,
            cse_alife_creature_abstract.upd_properties_info[8 : 10 + 1],
        )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        if self.version > 109:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_abstract.upd_properties_info[0],
            )
        elif self.version > 40:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_abstract.upd_properties_info[11],
            )
        else:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_abstract.upd_properties_info[12],
            )

        if (self.version < 17) and (ref(self) == "se_actor"):
            _if.export_properties(
                None,
                self,
                cse_alife_creature_abstract.upd_properties_info[13],
            )

        _if.export_properties(
            None,
            self,
            cse_alife_creature_abstract.upd_properties_info[1 : 3 + 1],
        )
        if (self.version > 117) and (not cse_alife_creature_abstract.is_2588(self)):
            _if.export_properties(
                None,
                self,
                cse_alife_creature_abstract.upd_properties_info[4 : 5 + 1],
            )
        else:
            if self.version > 85:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_creature_abstract.upd_properties_info[6],
                )

            if self.version > 63:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_creature_abstract.upd_properties_info[7],
                )

        _if.export_properties(
            None,
            self,
            cse_alife_creature_abstract.upd_properties_info[8 : 10 + 1],
        )

    @classmethod
    def is_2588(cls, self):
        return self.flags & cse_alife_creature_abstract.FL_IS_25XX


#######################################################################
class cse_alife_creature_crow(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_creature_abstract.init(self)
        cse_visual.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if self.version > 20:
            cse_alife_creature_abstract.state_read(self, packet)
            if self.version < 32:
                cse_visual.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if self.version > 20:
            cse_alife_creature_abstract.state_write(
                self,
                packet,
                spawn_id,
                extended_size,
            )
            if self.version < 32:
                cse_visual.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if self.version > 20:
            cse_alife_creature_abstract.state_import(self, _if, section, import_type)
            if self.version < 32:
                cse_visual.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if self.version > 20:
            cse_alife_creature_abstract.state_export(self, _if)
            if self.version < 32:
                cse_visual.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_creature_abstract.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_creature_abstract.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_creature_abstract.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_creature_abstract.update_export(self, _if)


#######################################################################
class cse_alife_creature_phantom(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_creature_abstract.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_creature_abstract.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_creature_abstract.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_creature_abstract.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_creature_abstract.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_creature_abstract.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_creature_abstract.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_creature_abstract.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_creature_abstract.update_export(self, _if)


#######################################################################
class cse_alife_monster_abstract(base_entity):
    properties_info = (
        {"name": "base_out_restrictors", "type": "sz", "default": ""},
        {"name": "base_in_restrictors", "type": "sz", "default": ""},
        {"name": "smart_terrain_id", "type": "u16", "default": 65535},
        {"name": "smart_terrain_task_active", "type": "u8", "default": 0},
    )
    upd_properties_info = (
        {"name": "upd:next_game_vertex_id", "type": "u16", "default": 0xFFFF},
        {"name": "upd:prev_game_vertex_id", "type": "u16", "default": 0xFFFF},
        {"name": "upd:distance_from_point", "type": "f32", "default": 0},
        {"name": "upd:distance_to_point", "type": "f32", "default": 0},
        {
            "name": "upd:cse_alife_monster_abstract__unk1_u32",
            "type": "u32",
            "default": 0,
        },
        {
            "name": "upd:cse_alife_monster_abstract__unk2_u32",
            "type": "u32",
            "default": 0,
        },
    )

    @classmethod
    def init(cls, self):
        cse_alife_creature_abstract.init(self)
        entity.init_properties(self, cse_alife_monster_abstract.properties_info)
        entity.init_properties(self, cse_alife_monster_abstract.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet):
        cse_alife_creature_abstract.state_read(self, packet)
        if self.version > 72:
            packet.unpack_properties(
                self,
                cse_alife_monster_abstract.properties_info[0],
            )

        if self.version > 73:
            packet.unpack_properties(
                self,
                cse_alife_monster_abstract.properties_info[1],
            )

        if self.version > 111:
            packet.unpack_properties(
                self,
                cse_alife_monster_abstract.properties_info[2],
            )

        if self.version > 113:
            packet.unpack_properties(
                self,
                cse_alife_monster_abstract.properties_info[3],
            )

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_creature_abstract.state_write(self, packet, spawn_id, extended_size)
        if self.version > 72:
            packet.pack_properties(self, cse_alife_monster_abstract.properties_info[0])

        if self.version > 73:
            packet.pack_properties(self, cse_alife_monster_abstract.properties_info[1])

        if self.version > 111:
            packet.pack_properties(self, cse_alife_monster_abstract.properties_info[2])

        if self.version > 113:
            packet.pack_properties(self, cse_alife_monster_abstract.properties_info[3])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_creature_abstract.state_import(self, _if, section, import_type)
        if self.version > 72:
            _if.import_properties(
                section,
                self,
                cse_alife_monster_abstract.properties_info[0],
            )

        if self.version > 73:
            _if.import_properties(
                section,
                self,
                cse_alife_monster_abstract.properties_info[1],
            )

        if self.version > 111:
            _if.import_properties(
                section,
                self,
                cse_alife_monster_abstract.properties_info[2],
            )

        if self.version > 113:
            _if.import_properties(
                section,
                self,
                cse_alife_monster_abstract.properties_info[3],
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_creature_abstract.state_export(self, _if)
        if self.version > 72:
            _if.export_properties(
                cse_alife_monster_abstract.__name__,
                self,
                cse_alife_monster_abstract.properties_info[0],
            )

        if self.version > 73:
            _if.export_properties(
                None,
                self,
                cse_alife_monster_abstract.properties_info[1],
            )

        if self.version > 111:
            _if.export_properties(
                None,
                self,
                cse_alife_monster_abstract.properties_info[2],
            )

        if self.version > 113:
            _if.export_properties(
                None,
                self,
                cse_alife_monster_abstract.properties_info[3],
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_creature_abstract.update_read(self, packet)
        packet.unpack_properties(
            self,
            cse_alife_monster_abstract.upd_properties_info[0 : 3 + 1],
        )
        if self.version <= 79:
            packet.unpack_properties(
                self,
                cse_alife_monster_abstract.upd_properties_info[4 : 5 + 1],
            )

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_creature_abstract.update_write(self, packet)
        packet.pack_properties(
            self,
            cse_alife_monster_abstract.upd_properties_info[0 : 3 + 1],
        )
        if self.version <= 79:
            packet.pack_properties(
                self,
                cse_alife_monster_abstract.upd_properties_info[4 : 5 + 1],
            )

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_creature_abstract.update_import(self, _if, section)
        _if.import_properties(
            section,
            self,
            cse_alife_monster_abstract.upd_properties_info[0 : 3 + 1],
        )
        if self.version <= 79:
            _if.import_properties(
                section,
                self,
                cse_alife_monster_abstract.upd_properties_info[4 : 5 + 1],
            )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        # my $pack;
        if self.version <= 72:
            pack = cse_alife_monster_abstract.__name__
        else:
            pack = None

        cse_alife_creature_abstract.update_export(self, _if)
        _if.export_properties(
            pack,
            self,
            cse_alife_monster_abstract.upd_properties_info[0 : 3 + 1],
        )
        if self.version <= 79:
            _if.export_properties(
                None,
                self,
                cse_alife_monster_abstract.upd_properties_info[4 : 5 + 1],
            )


#######################################################################
class cse_alife_psy_dog_phantom(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_monster_base.init(self)

    @classmethod
    def state_read(cls, self, packet):
        cse_alife_monster_base.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_monster_base.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_monster_base.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_monster_base.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_monster_base.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_monster_base.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_monster_base.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_monster_base.update_export(self, _if)


#######################################################################
class cse_alife_monster_rat(base_entity):
    properties_info = (
        {"name": "field_of_view", "type": "f32", "default": 120.0},
        {"name": "eye_range", "type": "f32", "default": 10.0},
        {"name": "minimum_speed", "type": "f32", "default": 0.5},
        {"name": "maximum_speed", "type": "f32", "default": 1.5},
        {"name": "attack_speed", "type": "f32", "default": 4.0},
        {"name": "pursiut_distance", "type": "f32", "default": 100.0},
        {"name": "home_distance", "type": "f32", "default": 10.0},
        {"name": "success_attack_quant", "type": "f32", "default": 20.0},
        {"name": "death_quant", "type": "f32", "default": -10.0},
        {"name": "fear_quant", "type": "f32", "default": -20.0},
        {"name": "restore_quant", "type": "f32", "default": 10.0},
        {"name": "restore_time_interval", "type": "u16", "default": 3000},
        {"name": "minimum_value", "type": "f32", "default": 0.0},
        {"name": "maximum_value", "type": "f32", "default": 100.0},
        {"name": "normal_value", "type": "f32", "default": 66.0},
        {"name": "hit_power", "type": "f32", "default": 10.0},
        {"name": "hit_interval", "type": "u16", "default": 1500},
        {"name": "distance", "type": "f32", "default": 0.7},
        {"name": "maximum_angle", "type": "f32", "default": 45.0},
        {"name": "success_probability", "type": "f32", "default": 0.5},
        {"name": "cse_alife_monster_rat__unk1_f32", "type": "f32", "default": 5.0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_monster_abstract.init(self)
        cse_alife_inventory_item.init(self)
        entity.init_properties(self, cse_alife_monster_rat.properties_info)

    @classmethod
    def state_read(cls, self, packet):
        cse_alife_monster_abstract.state_read(self, packet)
        packet.unpack_properties(self, cse_alife_monster_rat.properties_info[0 : 1 + 1])
        if self.version < 7:
            packet.unpack_properties(self, cse_alife_monster_rat.properties_info[20])

        packet.unpack_properties(
            self,
            cse_alife_monster_rat.properties_info[2 : 19 + 1],
        )
        if self.version > 39:
            cse_alife_inventory_item.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_monster_abstract.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, cse_alife_monster_rat.properties_info[0 : 1 + 1])
        if self.version < 7:
            packet.pack_properties(self, cse_alife_monster_rat.properties_info[20])

        packet.pack_properties(self, cse_alife_monster_rat.properties_info[2 : 19 + 1])
        if self.version > 39:
            cse_alife_inventory_item.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_monster_abstract.state_import(self, _if, section, import_type)
        _if.import_properties(
            section,
            self,
            cse_alife_monster_rat.properties_info[0 : 1 + 1],
        )
        if self.version < 7:
            _if.import_properties(
                section,
                self,
                cse_alife_monster_rat.properties_info[20],
            )

        _if.import_properties(
            section,
            self,
            cse_alife_monster_rat.properties_info[2 : 19 + 1],
        )
        if self.version > 39:
            cse_alife_inventory_item.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_monster_abstract.state_export(self, _if)
        _if.export_properties(
            cse_alife_monster_rat.__name__,
            self,
            cse_alife_monster_rat.properties_info[0 : 1 + 1],
        )
        if self.version < 7:
            _if.export_properties(None, self, cse_alife_monster_rat.properties_info[20])

        _if.export_properties(
            None,
            self,
            cse_alife_monster_rat.properties_info[2 : 19 + 1],
        )
        if self.version > 39:
            cse_alife_inventory_item.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_monster_abstract.update_read(self, packet)
        if self.version > 39:
            cse_alife_inventory_item.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_monster_abstract.update_write(self, packet)
        if self.version > 39:
            cse_alife_inventory_item.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_monster_abstract.update_import(self, _if, section)
        if self.version > 39:
            cse_alife_inventory_item.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_monster_abstract.update_export(self, _if)
        if self.version > 39:
            cse_alife_inventory_item.update_export(self, _if)


#######################################################################
class cse_alife_rat_group(base_entity):
    properties_info = (
        {"name": "cse_alife_rat_group__unk_1_u32", "type": "u32", "default": 1},
        {"name": "alife_count", "type": "u16", "default": 5},
        {
            "name": "cse_alife_rat_group__unk_2_l32u16v",
            "type": "l32u16v",
            "default": [],
        },
    )
    upd_properties_info = ({"name": "upd:alife_count", "type": "u32", "default": 1},)

    @classmethod
    def init(cls, self):
        cse_alife_monster_rat.init(self)
        entity.init_properties(self, cse_alife_rat_group.properties_info)
        entity.init_properties(self, cse_alife_rat_group.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet):
        cse_alife_monster_rat.state_read(cls, packet)
        packet.unpack_properties(self, cse_alife_rat_group.properties_info[0 : 1 + 1])
        if self.version > 16:
            packet.unpack_properties(self, cse_alife_rat_group.properties_info[2])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_monster_rat.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, cse_alife_rat_group.properties_info[0 : 1 + 1])
        if self.version > 16:
            packet.pack_properties(self, cse_alife_rat_group.properties_info[2])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_monster_rat.state_import(self, _if, section, import_type)
        _if.import_properties(
            section,
            self,
            cse_alife_rat_group.properties_info[0 : 1 + 1],
        )
        if self.version > 16:
            _if.import_properties(section, self, cse_alife_rat_group.properties_info[2])

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_monster_rat.state_export(self, _if)
        _if.export_properties(
            cse_alife_rat_group.__name__,
            self,
            cse_alife_rat_group.properties_info[0 : 1 + 1],
        )
        if self.version > 16:
            _if.export_properties(None, self, cse_alife_rat_group.properties_info[2])

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_monster_rat.update_read(self, packet)
        packet.unpack_properties(self, cse_alife_rat_group.upd_properties_info)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_monster_rat.update_write(self, packet)
        packet.pack_properties(self, cse_alife_rat_group.upd_properties_info)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_monster_rat.update_import(self, _if, section)
        _if.import_properties(section, self, cse_alife_rat_group.upd_properties_info)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_monster_rat.update_export(self, _if)
        _if.export_properties(None, self, cse_alife_rat_group.upd_properties_info)


#######################################################################
class cse_alife_monster_base(base_entity):
    properties_info = ({"name": "spec_object_id", "type": "u16", "default": 65535},)

    @classmethod
    def init(cls, self):
        cse_alife_monster_abstract.init(self)
        cse_ph_skeleton.init(self)
        entity.init_properties(self, cse_alife_monster_base.properties_info)

    @classmethod
    def state_read(cls, self, packet):
        cse_alife_monster_abstract.state_read(self, packet)
        if self.version >= 68:
            cse_ph_skeleton.state_read(self, packet)

        if self.version >= 109:
            packet.unpack_properties(self, cse_alife_monster_base.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_monster_abstract.state_write(self, packet, spawn_id, extended_size)
        if self.version >= 68:
            cse_ph_skeleton.state_write(self, packet, spawn_id, extended_size)

        if self.version >= 109:
            packet.pack_properties(self, cse_alife_monster_base.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_monster_abstract.state_import(self, _if, section, import_type)
        if self.version >= 68:
            cse_ph_skeleton.state_import(self, _if, section, import_type)

        if self.version >= 109:
            _if.import_properties(section, self, cse_alife_monster_base.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_monster_abstract.state_export(self, _if)
        if self.version >= 68:
            cse_ph_skeleton.state_export(self, _if)

        if self.version >= 109:
            _if.export_properties(
                cse_alife_monster_base.__name__,
                self,
                cse_alife_monster_base.properties_info,
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_monster_abstract.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_monster_abstract.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_monster_abstract.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_monster_abstract.update_export(self, _if)


#######################################################################
class cse_alife_monster_zombie(base_entity):
    properties_info = (
        {"name": "field_of_view", "type": "f32", "default": 0.0},
        {"name": "eye_range", "type": "f32", "default": 0.0},
        {"name": "health", "type": "f32", "default": 1.0},
        {"name": "minimum_speed", "type": "f32", "default": 0.0},
        {"name": "maximum_speed", "type": "f32", "default": 0.0},
        {"name": "attack_speed", "type": "f32", "default": 0.0},
        {"name": "pursuit_distance", "type": "f32", "default": 0.0},
        {"name": "home_distance", "type": "f32", "default": 0.0},
        {"name": "hit_power", "type": "f32", "default": 0.0},
        {"name": "hit_interval", "type": "u16", "default": 0},
        {"name": "distance", "type": "f32", "default": 0.0},
        {"name": "maximum_angle", "type": "f32", "default": 0.0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_monster_abstract.init(self)
        entity.init_properties(self, cse_alife_monster_zombie.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_monster_abstract.state_read(self, packet)
        packet.unpack_properties(
            self,
            cse_alife_monster_zombie.properties_info[0 : 1 + 1],
        )
        if self.version <= 5:
            packet.unpack_properties(self, cse_alife_monster_zombie.properties_info[2])

        packet.unpack_properties(
            self,
            cse_alife_monster_zombie.properties_info[3 : 11 + 1],
        )

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_monster_abstract.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(
            self,
            cse_alife_monster_zombie.properties_info[0 : 1 + 1],
        )
        if self.version <= 5:
            packet.pack_properties(self, cse_alife_monster_zombie.properties_info[2])

        packet.pack_properties(
            self,
            cse_alife_monster_zombie.properties_info[3 : 11 + 1],
        )

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_monster_abstract.state_import(self, _if, section, import_type)
        _if.import_properties(
            section,
            self,
            cse_alife_monster_zombie.properties_info[0 : 1 + 1],
        )
        if self.version <= 5:
            _if.import_properties(
                section,
                self,
                cse_alife_monster_zombie.properties_info[2],
            )

        _if.import_properties(
            section,
            self,
            cse_alife_monster_zombie.properties_info[3 : 11 + 1],
        )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_monster_abstract.state_export(self, _if)
        _if.export_properties(
            cse_alife_monster_zombie.__name__,
            self,
            cse_alife_monster_zombie.properties_info[0 : 1 + 1],
        )
        if self.version <= 5:
            _if.export_properties(
                None,
                self,
                cse_alife_monster_zombie.properties_info[2],
            )

        _if.export_properties(
            None,
            self,
            cse_alife_monster_zombie.properties_info[3 : 11 + 1],
        )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_monster_abstract.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_monster_abstract.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_monster_abstract.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_monster_abstract.update_export(self, _if)


#######################################################################
class cse_alife_flesh_group(base_entity):
    properties_info = (
        {"name": "cse_alife_flash_group__unk_1_u32", "type": "u32", "default": 0},
        {"name": "alife_count", "type": "u16", "default": 0},
        {
            "name": "cse_alife_flash_group__unk_2_l32u16v",
            "type": "l32u16v",
            "default": [],
        },
    )
    upd_properties_info = ({"name": "upd:alife_count", "type": "u32", "default": 1},)

    @classmethod
    def init(cls, self):
        cse_alife_monster_base.init(self)
        entity.init_properties(self, cse_alife_flesh_group.properties_info)
        entity.init_properties(self, cse_alife_flesh_group.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_monster_base.state_read(self, packet)
        packet.unpack_properties(self, cse_alife_flesh_group.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_monster_base.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, cse_alife_flesh_group.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_monster_base.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, cse_alife_flesh_group.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_monster_base.state_export(self, _if)
        _if.export_properties(
            cse_alife_flesh_group.__name__,
            self,
            cse_alife_flesh_group.properties_info,
        )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_monster_base.update_read(self, packet)
        packet.unpack_properties(self, cse_alife_flesh_group.upd_properties_info)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_monster_base.update_write(self, packet)
        packet.pack_properties(self, cse_alife_flesh_group.upd_properties_info)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_monster_base.update_import(self, _if, section)
        _if.import_properties(section, self, cse_alife_flesh_group.upd_properties_info)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_monster_base.update_export(self, _if)
        _if.export_properties(None, self, cse_alife_flesh_group.upd_properties_info)


#######################################################################
class cse_alife_trader_abstract(base_entity):
    eTraderFlagInfiniteAmmo = 0x00000001
    eTraderFlagDummy = 0x00000000  # really???
    properties_info = (
        {"name": "cse_alife_trader_abstract__unk1_u32", "type": "u32", "default": 0},
        {"name": "money", "type": "u32", "default": 0},
        {"name": "specific_character", "type": "sz", "default": ""},
        {"name": "trader_flags", "type": "h32", "default": 0x1},
        {"name": "character_profile", "type": "sz", "default": ""},
        {"name": "community_index", "type": "u32", "default": 4294967295},
        {"name": "rank", "type": "u32", "default": 2147483649},
        {"name": "reputation", "type": "u32", "default": 2147483649},
        {"name": "character_name", "type": "sz", "default": ""},
        {"name": "cse_alife_trader_abstract__unk2_u8", "type": "u8", "default": 0},
        {"name": "cse_alife_trader_abstract__unk3_u8", "type": "u8", "default": 0},
        {"name": "cse_alife_trader_abstract__unk4_u32", "type": "u32", "default": 0},
        {"name": "cse_alife_trader_abstract__unk5_u32", "type": "u32", "default": 0},
        {"name": "cse_alife_trader_abstract__unk6_u32", "type": "u32", "default": 0},
    )
    upd_properties_info = (
        {
            "name": "upd:cse_alife_trader_abstract__unk1_u32",
            "type": "u32",
            "default": 0,
        },
        {"name": "upd:money", "type": "u32", "default": 0},
        {"name": "upd:cse_trader_abstract__unk2_u32", "type": "u32", "default": 1},
    )

    @classmethod
    def init(cls, self):
        entity.init_properties(self, cse_alife_trader_abstract.properties_info)
        entity.init_properties(self, cse_alife_trader_abstract.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if self.version > 19:
            if self.version < 108:
                packet.unpack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[0],
                )

            if self.version < 36:
                packet.unpack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[13],
                )

            if self.version > 62:
                packet.unpack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[1],
                )

            if self.version > 95:
                packet.unpack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[2],
                )

            if (self.version > 75) and (self.version <= 95):
                packet.unpack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[11],
                )
                if self.version > 79:
                    packet.unpack_properties(
                        self,
                        cse_alife_trader_abstract.properties_info[12],
                    )

            if self.version > 77:
                packet.unpack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[3],
                )

            if self.version > 95:
                packet.unpack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[4],
                )

            if self.version > 85:
                packet.unpack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[5],
                )

            if self.version > 86:
                packet.unpack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[6 : 7 + 1],
                )

            if self.version > 104:
                packet.unpack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[8],
                )

            if self.version >= 128:
                packet.unpack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[9 : 10 + 1],
                )

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if self.version > 19:
            if self.version < 108:
                packet.pack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[0],
                )

            if self.version < 36:
                packet.pack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[13],
                )

            if self.version > 62:
                packet.pack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[1],
                )

            if self.version > 94:
                packet.pack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[2],
                )

            if (self.version > 75) and (self.version <= 95):
                packet.pack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[11],
                )
                if self.version > 79:
                    packet.pack_properties(
                        self,
                        cse_alife_trader_abstract.properties_info[12],
                    )

            if self.version > 77:
                packet.pack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[3],
                )

            if self.version > 95:
                packet.pack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[4],
                )

            if self.version > 85:
                packet.pack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[5],
                )

            if self.version > 86:
                packet.pack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[6 : 7 + 1],
                )

            if self.version > 104:
                packet.pack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[8],
                )

            if self.version >= 128:
                packet.pack_properties(
                    self,
                    cse_alife_trader_abstract.properties_info[9 : 10 + 1],
                )

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if self.version > 19:
            if self.version < 108:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader_abstract.properties_info[0],
                )

            if self.version < 36:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader_abstract.properties_info[13],
                )

            if self.version > 62:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader_abstract.properties_info[1],
                )

            if self.version > 95:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader_abstract.properties_info[2],
                )

            if (self.version > 75) and (self.version <= 95):
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader_abstract.properties_info[11],
                )
                if self.version > 79:
                    _if.import_properties(
                        section,
                        self,
                        cse_alife_trader_abstract.properties_info[12],
                    )

            if self.version > 77:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader_abstract.properties_info[3],
                )

            if self.version > 95:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader_abstract.properties_info[4],
                )

            if self.version > 85:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader_abstract.properties_info[5],
                )

            if self.version > 86:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader_abstract.properties_info[6 : 7 + 1],
                )

            if self.version > 104:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader_abstract.properties_info[8],
                )

            if self.version >= 128:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader_abstract.properties_info[9 : 10 + 1],
                )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if self.version > 19:
            if self.version < 108:
                _if.export_properties(
                    cse_alife_trader_abstract.__name__,
                    self,
                    cse_alife_trader_abstract.properties_info[0],
                )

            if self.version < 36:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_trader_abstract.properties_info[13],
                )

            if self.version > 62:
                pack = None
                if self.version > 108:
                    pack = cse_alife_trader_abstract.__name__

                _if.export_properties(
                    pack,
                    self,
                    cse_alife_trader_abstract.properties_info[1],
                )

            if self.version > 95:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_trader_abstract.properties_info[2],
                )

            if (self.version > 75) and (self.version <= 95):
                _if.export_properties(
                    None,
                    self,
                    cse_alife_trader_abstract.properties_info[11],
                )
                if self.version > 79:
                    _if.export_properties(
                        None,
                        self,
                        cse_alife_trader_abstract.properties_info[12],
                    )

            if self.version > 77:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_trader_abstract.properties_info[3],
                )

            if self.version > 95:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_trader_abstract.properties_info[4],
                )

            if self.version > 85:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_trader_abstract.properties_info[5],
                )

            if self.version > 86:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_trader_abstract.properties_info[6 : 7 + 1],
                )

            if self.version > 104:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_trader_abstract.properties_info[8],
                )

            if self.version >= 128:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_trader_abstract.properties_info[9 : 10 + 1],
                )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        if (self.version > 19) and (self.version < 102):
            packet.unpack_properties(
                self,
                cse_alife_trader_abstract.upd_properties_info[0 : 1 + 1],
            )
            if self.version < 86:
                packet.unpack_properties(
                    self,
                    cse_alife_trader_abstract.upd_properties_info[2],
                )

    @classmethod
    def update_write(cls, self, packet: data_packet):
        if (self.version > 19) and (self.version < 102):
            packet.pack_properties(
                self,
                cse_alife_trader_abstract.upd_properties_info[0 : 1 + 1],
            )
            if self.version < 86:
                packet.pack_properties(
                    self,
                    cse_alife_trader_abstract.upd_properties_info[2],
                )

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        if (self.version > 19) and (self.version < 102):
            _if.import_properties(
                section,
                self,
                cse_alife_trader_abstract.upd_properties_info[0 : 1 + 1],
            )
            if self.version < 86:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader_abstract.upd_properties_info[2],
                )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        if (self.version > 19) and (self.version < 102):
            _if.export_properties(
                None,
                self,
                cse_alife_trader_abstract.upd_properties_info[0 : 1 + 1],
            )
            if self.version < 86:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_trader_abstract.upd_properties_info[2],
                )


#######################################################################
class cse_alife_trader(base_entity):
    properties_info = (
        {"name": "organization_id", "type": "u32", "default": 1},
        {"name": "ordered_artefacts", "type": "ordaf", "default": []},
        {"name": "supplies", "type": "supplies", "default": []},
    )

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)
        cse_alife_trader_abstract.init(self)
        entity.init_properties(self, cse_alife_trader.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object_visual.state_read(self, packet)
        cse_alife_trader_abstract.state_read(self, packet)
        if self.version < 118:
            if self.version > 35:
                packet.unpack_properties(self, cse_alife_trader.properties_info[0])

            if self.version > 29:
                packet.unpack_properties(self, cse_alife_trader.properties_info[1])

            if self.version > 30:
                packet.unpack_properties(self, cse_alife_trader.properties_info[2])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object_visual.state_write(
            self,
            packet,
            spawn_id,
            extended_size,
        )
        cse_alife_trader_abstract.state_write(self, packet, spawn_id, extended_size)
        if self.version < 118:
            if self.version > 35:
                packet.pack_properties(self, cse_alife_trader.properties_info[0])

            if self.version > 29:
                packet.pack_properties(self, cse_alife_trader.properties_info[1])

            if self.version > 30:
                packet.pack_properties(self, cse_alife_trader.properties_info[2])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object_visual.state_import(self, _if, section, import_type)
        cse_alife_trader_abstract.state_import(self, _if, section, import_type)
        if self.version < 118:
            if self.version > 35:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader.properties_info[0],
                )

            if self.version > 29:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader.properties_info[1],
                )

            if self.version > 30:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_trader.properties_info[2],
                )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object_visual.state_export(self, _if)
        cse_alife_trader_abstract.state_export(self, _if)
        if self.version < 118:
            if self.version > 35:
                _if.export_properties(
                    cse_alife_trader.__name__,
                    self,
                    cse_alife_trader.properties_info[0],
                )

            if self.version > 29:
                pack = None
                if self.version <= 35:
                    pack = cse_alife_trader.__name__

                _if.export_properties(pack, self, cse_alife_trader.properties_info[1])

            if self.version > 30:
                _if.export_properties(None, self, cse_alife_trader.properties_info[2])

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_trader_abstract.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_trader_abstract.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_trader_abstract.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_trader_abstract.update_export(self, _if)


#######################################################################
class cse_alife_human_abstract(base_entity):
    properties_info = (
        {"name": "path", "type": "l32u32v", "default": []},
        {"name": "visited_vertices", "type": "u32", "default": 0},
        {"name": "known_customers_sz", "type": "sz", "default": ""},
        {"name": "known_customers", "type": "l32u32v", "default": []},
        {"name": "equipment_preferences", "type": "l32u8v", "default": []},
        {"name": "main_weapon_preferences", "type": "l32u8v", "default": []},
        {"name": "smart_terrain_id", "type": "u16", "default": 0},
        {"name": "cse_alife_human_abstract__unk1_u32", "type": "ha1", "default": []},
        {"name": "cse_alife_human_abstract__unk2_u32", "type": "ha2", "default": []},
        {"name": "cse_alife_human_abstract__unk3_u32", "type": "u32", "default": 0},
    )
    upd_properties_info = (
        {"name": "upd:cse_alife_human_abstract__unk3_u32", "type": "u32", "default": 0},
        {
            "name": "upd:cse_alife_human_abstract__unk4_u32",
            "type": "u32",
            "default": 0xFFFFFFFF,
        },
        {
            "name": "upd:cse_alife_human_abstract__unk5_u32",
            "type": "u32",
            "default": 0xFFFFFFFF,
        },
    )

    @classmethod
    def init(cls, self):
        cse_alife_monster_abstract.init(self)
        cse_alife_trader_abstract.init(self)
        entity.init_properties(self, cse_alife_human_abstract.properties_info)
        entity.init_properties(self, cse_alife_human_abstract.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_trader_abstract.state_read(self, packet)
        cse_alife_monster_abstract.state_read(self, packet)
        if self.version > 19:
            if self.version < 110:
                packet.unpack_properties(
                    self,
                    cse_alife_human_abstract.properties_info[0 : 1 + 1],
                )

            if self.version > 35:
                if self.version < 110:
                    packet.unpack_properties(
                        self,
                        cse_alife_human_abstract.properties_info[2],
                    )

                if self.version < 118:
                    packet.unpack_properties(
                        self,
                        cse_alife_human_abstract.properties_info[3],
                    )

            else:
                packet.unpack_properties(
                    self,
                    cse_alife_human_abstract.properties_info[9],
                )

            if self.version > 63:
                packet.unpack_properties(
                    self,
                    cse_alife_human_abstract.properties_info[4 : 5 + 1],
                )
            elif (self.version > 37) and (self.version <= 63):
                packet.unpack_properties(
                    self,
                    cse_alife_human_abstract.properties_info[7 : 8 + 1],
                )

        if (self.version >= 110) and (self.version < 112):
            packet.unpack_properties(self, cse_alife_human_abstract.properties_info[6])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_trader_abstract.state_write(self, packet, spawn_id, extended_size)
        cse_alife_monster_abstract.state_write(self, packet, spawn_id, extended_size)
        if self.version > 19:
            if self.version < 110:
                packet.pack_properties(
                    self,
                    cse_alife_human_abstract.properties_info[0 : 1 + 1],
                )

            if self.version > 35:
                if self.version < 110:
                    packet.pack_properties(
                        self,
                        cse_alife_human_abstract.properties_info[2],
                    )

                if self.version < 118:
                    packet.pack_properties(
                        self,
                        cse_alife_human_abstract.properties_info[3],
                    )

            else:
                packet.pack_properties(
                    self,
                    cse_alife_human_abstract.properties_info[9],
                )

            if self.version > 63:
                packet.pack_properties(
                    self,
                    cse_alife_human_abstract.properties_info[4 : 5 + 1],
                )
            elif (self.version > 37) and (self.version <= 63):
                packet.pack_properties(
                    self,
                    cse_alife_human_abstract.properties_info[7 : 8 + 1],
                )

        if (self.version >= 110) and (self.version < 112):
            packet.pack_properties(self, cse_alife_human_abstract.properties_info[6])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_trader_abstract.state_import(self, _if, section, import_type)
        cse_alife_monster_abstract.state_import(self, _if, section, import_type)
        if self.version > 19:
            if self.version < 110:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_human_abstract.properties_info[0 : 1 + 1],
                )

            if self.version > 35:
                if self.version < 110:
                    _if.import_properties(
                        section,
                        self,
                        cse_alife_human_abstract.properties_info[2],
                    )

                if self.version < 118:
                    _if.import_properties(
                        section,
                        self,
                        cse_alife_human_abstract.properties_info[3],
                    )

            else:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_human_abstract.properties_info[9],
                )

            if self.version > 63:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_human_abstract.properties_info[4 : 5 + 1],
                )
            elif (self.version > 37) and (self.version <= 63):
                _if.import_properties(
                    section,
                    self,
                    cse_alife_human_abstract.properties_info[7 : 8 + 1],
                )

        if (self.version >= 110) and (self.version < 112):
            _if.import_properties(
                section,
                self,
                cse_alife_human_abstract.properties_info[6],
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_trader_abstract.state_export(self, _if)
        cse_alife_monster_abstract.state_export(self, _if)
        if self.version > 19:
            if self.version < 110:
                _if.export_properties(
                    cse_alife_human_abstract.__name__,
                    self,
                    cse_alife_human_abstract.properties_info[0 : 1 + 1],
                )

            if self.version > 35:
                if self.version < 110:
                    _if.export_properties(
                        None,
                        self,
                        cse_alife_human_abstract.properties_info[2],
                    )

                if self.version < 118:
                    _if.export_properties(
                        None,
                        self,
                        cse_alife_human_abstract.properties_info[3],
                    )

            if self.version > 63:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_human_abstract.properties_info[4 : 5 + 1],
                )
            elif (self.version > 37) and (self.version <= 63):
                _if.export_properties(
                    None,
                    self,
                    cse_alife_human_abstract.properties_info[7 : 8 + 1],
                )
            else:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_human_abstract.properties_info[9],
                )

        if (self.version >= 110) and (self.version < 112):
            _if.export_properties(
                None,
                self,
                cse_alife_human_abstract.properties_info[6],
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_trader_abstract.update_read(self, packet)
        cse_alife_monster_abstract.update_read(self, packet)
        if self.version <= 109:
            packet.unpack_properties(self, cse_alife_human_abstract.upd_properties_info)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_trader_abstract.update_write(self, packet)
        cse_alife_monster_abstract.update_write(self, packet)
        if self.version <= 109:
            packet.pack_properties(self, cse_alife_human_abstract.upd_properties_info)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_trader_abstract.update_import(self, _if, section)
        cse_alife_monster_abstract.update_import(self, _if, section)
        if self.version <= 109:
            _if.import_properties(
                section,
                self,
                cse_alife_human_abstract.upd_properties_info,
            )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_trader_abstract.update_export(self, _if)
        cse_alife_monster_abstract.update_export(self, _if)
        if self.version <= 109:
            _if.export_properties(
                None,
                self,
                cse_alife_human_abstract.upd_properties_info,
            )


#######################################################################
class cse_alife_object_idol(base_entity):
    properties_info = (
        {"name": "cse_alife_object_idol__unk1_sz", "type": "sz", "default": ""},
        {"name": "cse_alife_object_idol__unk2_u32", "type": "u32", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_human_abstract.init(self)
        entity.init_properties(self, cse_alife_object_idol.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_human_abstract.state_read(self, packet)
        packet.unpack_properties(self, cse_alife_object_idol.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_human_abstract.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, cse_alife_object_idol.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_human_abstract.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, cse_alife_object_idol.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_human_abstract.state_export(self, _if)
        _if.export_properties(
            cse_alife_object_idol.__name__,
            self,
            cse_alife_object_idol.properties_info,
        )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_human_abstract.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_human_abstract.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_human_abstract.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_human_abstract.update_export(self, _if)


#######################################################################
class cse_alife_human_stalker(base_entity):
    properties_info = (
        {"name": "cse_alife_human_stalker__unk1_bool", "type": "u8", "default": 0},
    )
    upd_properties_info = ({"name": "upd:start_dialog", "type": "sz"},)

    @classmethod
    def init(cls, self):
        cse_alife_human_abstract.init(self)
        cse_ph_skeleton.init(self)
        entity.init_properties(self, cse_alife_human_stalker.properties_info)
        entity.init_properties(self, cse_alife_human_stalker.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_human_abstract.state_read(self, packet)
        if self.version > 67:
            cse_ph_skeleton.state_read(self, packet)

        if (self.version > 90) and (self.version < 111):
            packet.unpack_properties(self, cse_alife_human_stalker.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_human_abstract.state_write(self, packet, spawn_id, extended_size)
        if self.version > 67:
            cse_ph_skeleton.state_write(self, packet, spawn_id, extended_size)

        if (self.version > 90) and (self.version < 111):
            packet.pack_properties(self, cse_alife_human_stalker.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_human_abstract.state_import(self, _if, section, import_type)
        if self.version > 67:
            cse_ph_skeleton.state_import(self, _if, section, import_type)

        if (self.version > 90) and (self.version < 111):
            _if.import_properties(
                section,
                self,
                cse_alife_human_stalker.properties_info,
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_human_abstract.state_export(self, _if)
        if self.version > 67:
            cse_ph_skeleton.state_export(self, _if)

        if (self.version > 90) and (self.version < 111):
            _if.export_properties(
                cse_alife_human_stalker.__name__,
                self,
                cse_alife_human_stalker.properties_info,
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_human_abstract.update_read(self, packet)
        if self.version > 94:
            packet.unpack_properties(self, cse_alife_human_stalker.upd_properties_info)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_human_abstract.update_write(self, packet)
        if self.version > 94:
            packet.pack_properties(self, cse_alife_human_stalker.upd_properties_info)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_human_abstract.update_import(self, _if, section)
        if self.version > 94:
            _if.import_properties(
                section,
                self,
                cse_alife_human_stalker.upd_properties_info,
            )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_human_abstract.update_export(self, _if)
        if self.version > 94:
            _if.export_properties(
                cse_alife_human_stalker.__name__,
                self,
                cse_alife_human_stalker.upd_properties_info,
            )


#######################################################################
class cse_alife_creature_actor(base_entity):
    FL_HANDLED = 0x20

    properties_info = ({"name": "holder_id", "type": "h16", "default": 0xFFFF},)
    upd_properties_info = (
        {"name": "upd:actor_state", "type": "h16", "default": 0},
        {"name": "upd:actor_accel", "type": "sdir", "default": []},
        {"name": "upd:actor_velocity", "type": "sdir", "default": []},
        {"name": "upd:actor_radiation", "type": "f32", "default": 0},
        {"name": "upd:actor_radiation", "type": "q16", "default": 0},
        {"name": "upd:cse_alife_creature_actor_unk1_q16", "type": "q16", "default": 0},
        {"name": "upd:actor_weapon", "type": "u8", "default": 0},
        {"name": "upd:num_items", "type": "u16", "default": 0},
        {"name": "upd:actor_radiation", "type": "q16_old", "default": 0},
        # m_AliveState
        {"name": "upd:alive_state_enabled", "type": "u8", "default": 0},
        {"name": "upd:alive_state_angular_vel", "type": "f32v3", "default": []},
        {"name": "upd:alive_state_linear_vel", "type": "f32v3", "default": []},
        {"name": "upd:alive_state_force", "type": "f32v3", "default": []},
        {"name": "upd:alive_state_torque", "type": "f32v3", "default": []},
        {"name": "upd:alive_state_position", "type": "f32v3", "default": []},
        {"name": "upd:alive_state_quaternion", "type": "f32v4", "default": []},
        # m_DeadBodyData
        {"name": "upd:bone_data_size", "type": "u8", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_creature_abstract.init(self)
        cse_alife_trader_abstract.init(self)
        cse_ph_skeleton.init(self)
        entity.init_properties(self, cse_alife_creature_actor.properties_info)
        entity.init_properties(self, cse_alife_creature_actor.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_creature_abstract.state_read(self, packet)
        cse_alife_trader_abstract.state_read(self, packet)
        if self.version > 91:
            cse_ph_skeleton.state_read(self, packet)

        if self.version > 88:
            packet.unpack_properties(self, cse_alife_creature_actor.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_creature_abstract.state_write(self, packet, spawn_id, extended_size)
        cse_alife_trader_abstract.state_write(self, packet, spawn_id, extended_size)
        if self.version > 91:
            cse_ph_skeleton.state_write(self, packet, spawn_id, extended_size)

        if self.version > 88:
            packet.pack_properties(self, cse_alife_creature_actor.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_creature_abstract.state_import(self, _if, section, import_type)
        cse_alife_trader_abstract.state_import(self, _if, section, import_type)
        if self.version > 91:
            cse_ph_skeleton.state_import(self, _if, section, import_type)

        if self.version > 88:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_actor.properties_info,
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_creature_abstract.state_export(self, _if)
        cse_alife_trader_abstract.state_export(self, _if)
        if self.version > 91:
            cse_ph_skeleton.state_export(self, _if)

        if self.version > 88:
            _if.export_properties(
                cse_alife_creature_actor.__name__,
                self,
                cse_alife_creature_actor.properties_info,
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_creature_abstract.update_read(self, packet)
        cse_alife_trader_abstract.update_read(self, packet)
        packet.unpack_properties(
            self,
            cse_alife_creature_actor.upd_properties_info[0 : 2 + 1],
        )
        if getattr(self, "is_handled", None) is not None and self.is_handled():
            return
        if self.version > 109:
            packet.unpack_properties(
                self,
                cse_alife_creature_actor.upd_properties_info[3],
            )
        elif self.version > 40:
            packet.unpack_properties(
                self,
                cse_alife_creature_actor.upd_properties_info[4],
            )
        else:
            packet.unpack_properties(
                self,
                cse_alife_creature_actor.upd_properties_info[8],
            )

        if (self.version > 101) and (self.version <= 104):
            packet.unpack_properties(
                self,
                cse_alife_creature_actor.upd_properties_info[5],
            )

        packet.unpack_properties(self, cse_alife_creature_actor.upd_properties_info[6])
        if self.version > 39:
            packet.unpack_properties(
                self,
                cse_alife_creature_actor.upd_properties_info[7],
            )

        if getattr(self, "upd:num_items", None) is not None:
            if getattr(self, "upd:num_items") == 0:
                return
            if getattr(self, "upd:num_items") == 1:
                packet.unpack_properties(
                    self,
                    cse_alife_creature_actor.upd_properties_info[9 : 15 + 1],
                )
            else:
                packet.unpack_properties(
                    self,
                    cse_alife_creature_actor.upd_properties_info[16],
                )
                length = (
                    getattr(self, "upd:num_items") * getattr(self, "upd:bone_data_size")
                    + 24
                )
                setattr(
                    self,
                    "upd:dead_body_data",
                    packet.unpack(f"a[{length}]", length),
                )

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_creature_abstract.update_write(self, packet)
        cse_alife_trader_abstract.update_write(self, packet)
        packet.pack_properties(
            self,
            cse_alife_creature_actor.upd_properties_info[0 : 2 + 1],
        )
        if self.version > 109:
            packet.pack_properties(
                self,
                cse_alife_creature_actor.upd_properties_info[3],
            )
        elif self.version > 40:
            packet.pack_properties(
                self,
                cse_alife_creature_actor.upd_properties_info[4],
            )
        else:
            packet.pack_properties(
                self,
                cse_alife_creature_actor.upd_properties_info[8],
            )

        if (self.version > 101) and (self.version <= 104):
            packet.pack_properties(
                self,
                cse_alife_creature_actor.upd_properties_info[5],
            )

        packet.pack_properties(self, cse_alife_creature_actor.upd_properties_info[6])
        if self.version > 39:
            packet.pack_properties(
                self,
                cse_alife_creature_actor.upd_properties_info[7],
            )

        if getattr(self, "upd:num_items") == 0:
            return
        if getattr(self, "upd:num_items") == 1:
            packet.pack_properties(
                self,
                cse_alife_creature_actor.upd_properties_info[9 : 15 + 1],
            )
        else:
            packet.pack_properties(
                self,
                cse_alife_creature_actor.upd_properties_info[16],
            )
            length = (
                getattr(self, "upd:num_items") * getattr(self, "upd:bone_data_size")
                + 24
            )
            setattr(self, "upd:dead_body_data", packet.pack(f"a[{length}]"))

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_creature_abstract.update_import(self, _if, section)
        cse_alife_trader_abstract.update_import(self, _if, section)
        _if.import_properties(
            section,
            self,
            cse_alife_creature_actor.upd_properties_info[0 : 2 + 1],
        )
        if self.version > 109:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_actor.upd_properties_info[3],
            )
        elif self.version > 40:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_actor.upd_properties_info[4],
            )
        else:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_actor.upd_properties_info[8],
            )

        if (self.version > 101) and (self.version <= 104):
            _if.import_properties(
                section,
                self,
                cse_alife_creature_actor.upd_properties_info[5],
            )

        _if.import_properties(
            section,
            self,
            cse_alife_creature_actor.upd_properties_info[6],
        )
        if self.version > 39:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_actor.upd_properties_info[7],
            )

        if getattr(self, "upd:num_items") == 0:
            return
        if getattr(self, "upd:num_items") == 1:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_actor.upd_properties_info[9 : 15 + 1],
            )
        else:
            _if.import_properties(
                section,
                self,
                cse_alife_creature_actor.upd_properties_info[16],
            )
            setattr(
                self,
                "upd:dead_body_data",
                _if.value(section, "upd:dead_body_data"),
            )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_creature_abstract.update_export(self, _if)
        cse_alife_trader_abstract.update_export(self, _if)
        pack = None
        if (self.version >= 21) and (self.version <= 88):
            pack = cse_alife_creature_actor.__name__

        _if.export_properties(
            pack,
            self,
            cse_alife_creature_actor.upd_properties_info[0 : 2 + 1],
        )
        if self.version > 109:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_actor.upd_properties_info[3],
            )
        elif self.version > 40:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_actor.upd_properties_info[4],
            )
        else:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_actor.upd_properties_info[8],
            )

        if (self.version > 101) and (self.version <= 104):
            _if.export_properties(
                None,
                self,
                cse_alife_creature_actor.upd_properties_info[5],
            )

        _if.export_properties(
            None,
            self,
            cse_alife_creature_actor.upd_properties_info[6],
        )
        if self.version > 39:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_actor.upd_properties_info[7],
            )

        if getattr(self, "upd:num_items") == 0:
            return
        if getattr(self, "upd:num_items") == 1:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_actor.upd_properties_info[9 : 15 + 1],
            )
        else:
            _if.export_properties(
                None,
                self,
                cse_alife_creature_actor.upd_properties_info[16],
            )
            fh = _if.fh
            fh.write("upd:dead_body_data = self.{'upd:dead_body_data'}\n")

    # print $fh "upd:dead_body_data = self.{'upd:dead_body_data'}\n";

    def is_handled(self):
        return self.flags & self.FL_HANDLED


#######################################################################
class cse_smart_cover(base_entity):
    properties_info = (
        {"name": "description", "type": "sz", "default": ""},
        {"name": "hold_position_time", "type": "f32", "default": 0.0},
        {"name": "enter_min_enemy_distance", "type": "f32", "default": 0.0},
        {"name": "exit_min_enemy_distance", "type": "f32", "default": 0.0},
        {"name": "is_combat_cover", "type": "u8", "default": 0},
        {"name": "MP_respawn", "type": "u8", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object.init(self)
        entity.init_properties(self, cse_smart_cover.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object.state_read(self, packet)
        cse_shape.state_read(self, packet)
        packet.unpack_properties(self, cse_smart_cover.properties_info[0 : 1 + 1])
        if self.version >= 120:
            packet.unpack_properties(self, cse_smart_cover.properties_info[2 : 3 + 1])

        if self.version >= 122:
            packet.unpack_properties(self, cse_smart_cover.properties_info[4])

        if self.version >= 128:
            packet.unpack_properties(self, cse_smart_cover.properties_info[5])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object.state_write(self, packet, spawn_id, extended_size)
        cse_shape.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, cse_smart_cover.properties_info[0 : 1 + 1])
        if self.version >= 120:
            packet.pack_properties(self, cse_smart_cover.properties_info[2 : 3 + 1])

        if self.version >= 122:
            packet.pack_properties(self, cse_smart_cover.properties_info[4])

        if self.version >= 128:
            packet.pack_properties(self, cse_smart_cover.properties_info[5])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object.state_import(self, _if, section, import_type)
        cse_shape.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, cse_smart_cover.properties_info[0 : 1 + 1])
        if self.version >= 120:
            _if.import_properties(
                section,
                self,
                cse_smart_cover.properties_info[2 : 3 + 1],
            )

        if self.version >= 122:
            _if.import_properties(section, self, cse_smart_cover.properties_info[4])

        if self.version >= 128:
            _if.import_properties(section, self, cse_smart_cover.properties_info[5])

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object.state_export(self, _if)
        cse_shape.state_export(self, _if)
        _if.export_properties(
            cse_smart_cover.__name__,
            self,
            cse_smart_cover.properties_info[0 : 1 + 1],
        )
        if self.version >= 120:
            _if.export_properties(
                None,
                self,
                cse_smart_cover.properties_info[2 : 3 + 1],
            )

        if self.version >= 122:
            _if.export_properties(None, self, cse_smart_cover.properties_info[4])

        if self.version >= 128:
            _if.export_properties(None, self, cse_smart_cover.properties_info[5])


#######################################################################
class cse_alife_space_restrictor(base_entity):
    eDefaultRestrictorTypeNone = 0x00
    eDefaultRestrictorTypeOut = 0x01
    eDefaultRestrictorTypeIn = 0x02
    eRestrictorTypeNone = 0x03
    eRestrictorTypeIn = 0x04
    eRestrictorTypeOut = 0x05

    properties_info = ({"name": "restrictor_type", "type": "u8", "default": 0xFF},)

    @classmethod
    def init(cls, self):
        cse_alife_object.init(self)
        entity.init_properties(self, cse_alife_space_restrictor.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if self.version > 14:
            cse_alife_object.state_read(self, packet)

        cse_shape.state_read(self, packet)
        if self.version > 74:
            packet.unpack_properties(self, cse_alife_space_restrictor.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if self.version > 14:
            cse_alife_object.state_write(self, packet, spawn_id, extended_size)

        cse_shape.state_write(self, packet, spawn_id, extended_size)
        if self.version > 74:
            packet.pack_properties(self, cse_alife_space_restrictor.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if self.version > 14:
            cse_alife_object.state_import(self, _if, section, import_type)

        cse_shape.state_import(self, _if, section, import_type)
        if self.version > 74:
            _if.import_properties(
                section,
                self,
                cse_alife_space_restrictor.properties_info,
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if self.version > 14:
            cse_alife_object.state_export(self, _if)

        cse_shape.state_export(self, _if)
        if self.version > 74:
            _if.export_properties(
                cse_alife_space_restrictor.__name__,
                self,
                cse_alife_space_restrictor.properties_info,
            )


#######################################################################
class cse_alife_team_base_zone(base_entity):
    properties_info = ({"name": "team", "type": "u8", "default": 0},)

    @classmethod
    def init(cls, self):
        cse_alife_space_restrictor.init(self)
        entity.init_properties(self, cse_alife_team_base_zone.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_space_restrictor.state_read(self, packet)
        packet.unpack_properties(self, cse_alife_team_base_zone.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_space_restrictor.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, cse_alife_team_base_zone.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_space_restrictor.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, cse_alife_team_base_zone.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_space_restrictor.state_export(self, _if)
        _if.export_properties(
            cse_alife_team_base_zone.__name__,
            self,
            cse_alife_team_base_zone.properties_info,
        )


#######################################################################
class cse_alife_level_changer(base_entity):
    properties_info = (
        {"name": "cse_alife_level_changer__unk1_s32", "type": "s32", "default": -1},
        {"name": "cse_alife_level_changer__unk2_s32", "type": "s32", "default": -1},
        {"name": "dest_game_vertex_id", "type": "u16", "default": 0},
        {"name": "dest_level_vertex_id", "type": "u32", "default": 0},
        {"name": "dest_position", "type": "f32v3", "default": [0, 0, 0]},
        {"name": "dest_direction", "type": "f32v3", "default": [0, 0, 0]},
        {"name": "angle_y", "type": "f32", "default": 0.0},
        {"name": "dest_level_name", "type": "sz", "default": ""},
        {"name": "dest_graph_point", "type": "sz", "default": ""},
        {
            "name": "silent_mode",
            "type": "u8",
            "default": 0,
        },
    )

    @classmethod
    def init(cls, self):
        cse_alife_space_restrictor.init(self)
        entity.init_properties(self, cse_alife_level_changer.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_space_restrictor.state_read(self, packet)
        if self.version < 34:
            packet.unpack_properties(
                self,
                cse_alife_level_changer.properties_info[0 : 1 + 1],
            )
        else:
            packet.unpack_properties(
                self,
                cse_alife_level_changer.properties_info[2 : 4 + 1],
            )
            if self.version > 53:
                packet.unpack_properties(
                    self,
                    cse_alife_level_changer.properties_info[5],
                )
            else:
                packet.unpack_properties(
                    self,
                    cse_alife_level_changer.properties_info[6],
                )

        packet.unpack_properties(
            self,
            cse_alife_level_changer.properties_info[7 : 8 + 1],
        )
        if self.version > 116:
            packet.unpack_properties(self, cse_alife_level_changer.properties_info[9])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_space_restrictor.state_write(self, packet, spawn_id, extended_size)
        if self.version < 34:
            packet.pack_properties(
                self,
                cse_alife_level_changer.properties_info[0 : 1 + 1],
            )
        else:
            packet.pack_properties(
                self,
                cse_alife_level_changer.properties_info[2 : 4 + 1],
            )
            if self.version > 53:
                packet.pack_properties(self, cse_alife_level_changer.properties_info[5])
            else:
                packet.pack_properties(self, cse_alife_level_changer.properties_info[6])

        packet.pack_properties(self, cse_alife_level_changer.properties_info[7 : 8 + 1])
        if self.version > 116:
            packet.pack_properties(self, cse_alife_level_changer.properties_info[9])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_space_restrictor.state_import(self, _if, section, import_type)
        if self.version < 34:
            _if.import_properties(
                section,
                self,
                cse_alife_level_changer.properties_info[0 : 1 + 1],
            )
        else:
            _if.import_properties(
                section,
                self,
                cse_alife_level_changer.properties_info[2 : 4 + 1],
            )
            if self.version > 53:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_level_changer.properties_info[5],
                )
            else:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_level_changer.properties_info[6],
                )

        _if.import_properties(
            section,
            self,
            cse_alife_level_changer.properties_info[7 : 8 + 1],
        )
        if self.version > 116:
            _if.import_properties(
                section,
                self,
                cse_alife_level_changer.properties_info[9],
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_space_restrictor.state_export(self, _if)
        if self.version < 34:
            _if.export_properties(
                cse_alife_level_changer.__name__,
                self,
                cse_alife_level_changer.properties_info[0 : 1 + 1],
            )
        else:
            _if.export_properties(
                cse_alife_level_changer.__name__,
                self,
                cse_alife_level_changer.properties_info[2 : 4 + 1],
            )
            if self.version > 53:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_level_changer.properties_info[5],
                )
            else:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_level_changer.properties_info[6],
                )

        _if.export_properties(
            None,
            self,
            cse_alife_level_changer.properties_info[7 : 8 + 1],
        )
        if self.version > 116:
            _if.export_properties(
                None,
                self,
                cse_alife_level_changer.properties_info[9],
            )


#######################################################################
class cse_alife_smart_zone(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_space_restrictor.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_space_restrictor.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_space_restrictor.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_space_restrictor.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_space_restrictor.state_export(self, _if)


#######################################################################
class cse_alife_custom_zone(base_entity):
    FL_HANDLED = 0x20
    properties_info = (
        {"name": "max_power", "type": "f32", "default": 0.0},
        {"name": "attenuation", "type": "f32", "default": 0.0},
        {"name": "period", "type": "u32", "default": 0},
        {"name": "owner_id", "type": "h32", "default": 0xFFFFFFFF},
        {"name": "enabled_time", "type": "u32", "default": 0},
        {"name": "disabled_time", "type": "u32", "default": 0},
        {"name": "start_time_shift", "type": "u32", "default": 0},
    )
    upd_properties_info = (
        {
            "name": "upd:cse_alife_custom_zone__unk1_h32",
            "type": "h32",
            "default": 0xFFFFFFFF,
        },
    )

    @classmethod
    def init(cls, self):
        cse_alife_space_restrictor.init(self)
        entity.init_properties(self, cse_alife_custom_zone.properties_info)
        entity.init_properties(self, cse_alife_custom_zone.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_space_restrictor.state_read(self, packet)
        packet.unpack_properties(self, cse_alife_custom_zone.properties_info[0])
        if self.version < 113:
            packet.unpack_properties(
                self,
                cse_alife_custom_zone.properties_info[1 : 2 + 1],
            )

        if (self.version > 66) and (self.version < 118):
            packet.unpack_properties(self, cse_alife_custom_zone.properties_info[1])

        if self.version > 102:
            packet.unpack_properties(self, cse_alife_custom_zone.properties_info[3])

        if self.version > 105:
            packet.unpack_properties(
                self,
                cse_alife_custom_zone.properties_info[4 : 5 + 1],
            )

        if self.version > 106:
            packet.unpack_properties(self, cse_alife_custom_zone.properties_info[6])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_space_restrictor.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, cse_alife_custom_zone.properties_info[0])
        if self.version < 113:
            packet.pack_properties(
                self,
                cse_alife_custom_zone.properties_info[1 : 2 + 1],
            )

        if (self.version > 66) and (self.version < 118):
            packet.pack_properties(self, cse_alife_custom_zone.properties_info[1])

        if self.version > 102:
            packet.pack_properties(self, cse_alife_custom_zone.properties_info[3])

        if self.version > 105:
            packet.pack_properties(
                self,
                cse_alife_custom_zone.properties_info[4 : 5 + 1],
            )

        if self.version > 106:
            packet.pack_properties(self, cse_alife_custom_zone.properties_info[6])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_space_restrictor.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, cse_alife_custom_zone.properties_info[0])
        if self.version < 113:
            _if.import_properties(
                section,
                self,
                cse_alife_custom_zone.properties_info[1 : 2 + 1],
            )

        if (self.version > 66) and (self.version < 118):
            _if.import_properties(
                section,
                self,
                cse_alife_custom_zone.properties_info[1],
            )

        if self.version > 102:
            _if.import_properties(
                section,
                self,
                cse_alife_custom_zone.properties_info[3],
            )

        if self.version > 105:
            _if.import_properties(
                section,
                self,
                cse_alife_custom_zone.properties_info[4 : 5 + 1],
            )

        if self.version > 106:
            _if.import_properties(
                section,
                self,
                cse_alife_custom_zone.properties_info[6],
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_space_restrictor.state_export(self, _if)
        _if.export_properties(
            cse_alife_custom_zone.__name__,
            self,
            cse_alife_custom_zone.properties_info[0],
        )
        if self.version < 113:
            _if.export_properties(
                None,
                self,
                cse_alife_custom_zone.properties_info[1 : 2 + 1],
            )

        if (self.version > 66) and (self.version < 118):
            _if.export_properties(None, self, cse_alife_custom_zone.properties_info[1])

        if self.version > 102:
            _if.export_properties(None, self, cse_alife_custom_zone.properties_info[3])

        if self.version > 105:
            _if.export_properties(
                None,
                self,
                cse_alife_custom_zone.properties_info[4 : 5 + 1],
            )

        if self.version > 106:
            _if.export_properties(None, self, cse_alife_custom_zone.properties_info[6])

    @classmethod
    def update_read(cls, self, packet: data_packet):
        if (
            (self.version > 101)
            and (self.version <= 118)
            and (self.script_version <= 5)
        ):
            packet.unpack_properties(self, cse_alife_custom_zone.upd_properties_info)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        if (
            (self.version > 101)
            and (self.version <= 118)
            and (self.script_version <= 5)
        ):
            packet.pack_properties(self, cse_alife_custom_zone.upd_properties_info)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        if (
            (self.version > 101)
            and (self.version <= 118)
            and (self.script_version <= 5)
        ):
            _if.import_properties(
                section,
                self,
                cse_alife_custom_zone.upd_properties_info,
            )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        if (
            (self.version > 101)
            and (self.version <= 118)
            and (self.script_version <= 5)
        ):
            _if.export_properties(None, self, cse_alife_custom_zone.upd_properties_info)

    def is_handled(self):
        return self.flags & self.FL_HANDLED


######################################################################
class cse_alife_anomalous_zone(base_entity):
    FL_HANDLED = 0x20
    properties_info = (
        {"name": "offline_interactive_radius", "type": "f32", "default": 0.0},
        {"name": "artefact_birth_probability", "type": "f32", "default": 0.0},
        {"name": "artefact_spawns", "type": "afspawns_u32", "default": []},
        {"name": "artefact_spawns", "type": "afspawns", "default": []},
        {"name": "artefact_spawn_count", "type": "u16", "default": 0},
        {"name": "artefact_position_offset", "type": "h32", "default": 0},
        {"name": "start_time_shift", "type": "u32", "default": 0},
        {"name": "cse_alife_anomalous_zone__unk2_f32", "type": "f32", "default": 0.0},
        {"name": "min_start_power", "type": "f32", "default": 0.0},
        {"name": "max_start_power", "type": "f32", "default": 0.0},
        {"name": "power_artefact_factor", "type": "f32", "default": 0.0},
        {"name": "owner_id", "type": "h32", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_custom_zone.init(self)
        entity.init_properties(self, cse_alife_anomalous_zone.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_custom_zone.state_read(self, packet)
        if self.version > 21:
            packet.unpack_properties(self, cse_alife_anomalous_zone.properties_info[0])
            if ref(self) == "cse_alife_custom_zone":
                return  # some mod error handling
            if self.version < 113:
                packet.unpack_properties(
                    self,
                    cse_alife_anomalous_zone.properties_info[1],
                )
                if self.version < 26:
                    packet.unpack_properties(
                        self,
                        cse_alife_anomalous_zone.properties_info[2],
                    )
                else:
                    packet.unpack_properties(
                        self,
                        cse_alife_anomalous_zone.properties_info[3],
                    )

        if self.version > 25:
            packet.unpack_properties(
                self,
                cse_alife_anomalous_zone.properties_info[4 : 5 + 1],
            )

        if (self.version > 27) and (self.version < 67):
            packet.unpack_properties(self, cse_alife_anomalous_zone.properties_info[6])

        if (self.version > 38) and (self.version < 113):
            packet.unpack_properties(self, cse_alife_anomalous_zone.properties_info[7])

        if self.version > 78 and self.version < 113:
            packet.unpack_properties(
                self,
                cse_alife_anomalous_zone.properties_info[8 : 10 + 1],
            )

        if self.version == 102:
            packet.unpack_properties(self, cse_alife_anomalous_zone.properties_info[11])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_custom_zone.state_write(self, packet, spawn_id, extended_size)
        if self.version > 21:
            packet.pack_properties(self, cse_alife_anomalous_zone.properties_info[0])
            if self.version < 113:
                packet.pack_properties(
                    self,
                    cse_alife_anomalous_zone.properties_info[1],
                )
                if self.version < 26:
                    packet.pack_properties(
                        self,
                        cse_alife_anomalous_zone.properties_info[2],
                    )
                else:
                    packet.pack_properties(
                        self,
                        cse_alife_anomalous_zone.properties_info[3],
                    )

        if self.version > 25:
            packet.pack_properties(
                self,
                cse_alife_anomalous_zone.properties_info[4 : 5 + 1],
            )

        if (self.version > 27) and (self.version < 67):
            packet.pack_properties(self, cse_alife_anomalous_zone.properties_info[6])

        if (self.version > 38) and (self.version < 113):
            packet.pack_properties(self, cse_alife_anomalous_zone.properties_info[7])

        if self.version > 78 and self.version < 113:
            packet.pack_properties(
                self,
                cse_alife_anomalous_zone.properties_info[8 : 10 + 1],
            )

        if self.version == 102:
            packet.pack_properties(self, cse_alife_anomalous_zone.properties_info[11])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_custom_zone.state_import(self, _if, section, import_type)
        if self.version > 21:
            _if.import_properties(
                section,
                self,
                cse_alife_anomalous_zone.properties_info[0],
            )
            if self.version < 113:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_anomalous_zone.properties_info[1],
                )
                if self.version < 26:
                    _if.import_properties(
                        section,
                        self,
                        cse_alife_anomalous_zone.properties_info[2],
                    )
                else:
                    _if.import_properties(
                        section,
                        self,
                        cse_alife_anomalous_zone.properties_info[3],
                    )

        if self.version > 25:
            _if.import_properties(
                section,
                self,
                cse_alife_anomalous_zone.properties_info[4 : 5 + 1],
            )

        if (self.version > 27) and (self.version < 67):
            _if.import_properties(
                section,
                self,
                cse_alife_anomalous_zone.properties_info[6],
            )

        if (self.version > 38) and (self.version < 113):
            _if.import_properties(
                section,
                self,
                cse_alife_anomalous_zone.properties_info[7],
            )

        if self.version > 78 and self.version < 113:
            _if.import_properties(
                section,
                self,
                cse_alife_anomalous_zone.properties_info[8 : 10 + 1],
            )

        if self.version == 102:
            _if.import_properties(
                section,
                self,
                cse_alife_anomalous_zone.properties_info[11],
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_custom_zone.state_export(self, _if)
        if self.version > 21:
            _if.export_properties(
                cse_alife_anomalous_zone.__name__,
                self,
                cse_alife_anomalous_zone.properties_info[0],
            )
            if self.version < 113:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_anomalous_zone.properties_info[1],
                )
                if self.version < 26:
                    _if.export_properties(
                        None,
                        self,
                        cse_alife_anomalous_zone.properties_info[2],
                    )
                else:
                    _if.export_properties(
                        None,
                        self,
                        cse_alife_anomalous_zone.properties_info[3],
                    )

        if self.version > 25:
            _if.export_properties(
                None,
                self,
                cse_alife_anomalous_zone.properties_info[4 : 5 + 1],
            )

        if (self.version > 27) and (self.version < 67):
            _if.export_properties(
                None,
                self,
                cse_alife_anomalous_zone.properties_info[6],
            )

        if (self.version > 38) and (self.version < 113):
            _if.export_properties(
                None,
                self,
                cse_alife_anomalous_zone.properties_info[7],
            )

        if self.version > 78 and self.version < 113:
            _if.export_properties(
                None,
                self,
                cse_alife_anomalous_zone.properties_info[8 : 10 + 1],
            )

        if self.version == 102:
            _if.export_properties(
                None,
                self,
                cse_alife_anomalous_zone.properties_info[11],
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_custom_zone.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_custom_zone.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_custom_zone.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_custom_zone.update_export(self, _if)

    def is_handled(self):
        return self.flags & self.FL_HANDLED


#######################################################################
class cse_alife_zone_visual(base_entity):
    FL_HANDLED = 0x20
    properties_info = (
        {"name": "idle_animation", "type": "sz", "default": ""},
        {"name": "attack_animation", "type": "sz", "default": ""},
    )

    @classmethod
    def init(cls, self):
        cse_alife_anomalous_zone.init(self)
        cse_visual.init(self)
        entity.init_properties(self, cse_alife_zone_visual.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_anomalous_zone.state_read(self, packet)
        if (self.version > 104) or (self.section_name == "zone_burning_fuzz1"):
            cse_visual.state_read(self, packet)
            packet.unpack_properties(self, cse_alife_zone_visual.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_anomalous_zone.state_write(self, packet, spawn_id, extended_size)
        if (self.version > 104) or (self.section_name == "zone_burning_fuzz1"):
            cse_visual.state_write(self, packet, spawn_id, extended_size)
            packet.pack_properties(self, cse_alife_zone_visual.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_anomalous_zone.state_import(self, _if, section, import_type)
        if (self.version > 104) or (self.section_name == "zone_burning_fuzz1"):
            cse_visual.state_import(self, _if, section, import_type)
            _if.import_properties(section, self, cse_alife_zone_visual.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_anomalous_zone.state_export(self, _if)
        if (self.version > 104) or (self.section_name == "zone_burning_fuzz1"):
            cse_visual.state_export(self, _if)
            _if.export_properties(
                cse_alife_zone_visual.__name__,
                self,
                cse_alife_zone_visual.properties_info,
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_custom_zone.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_custom_zone.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_custom_zone.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_custom_zone.update_export(self, _if)

    def is_handled(self):
        return self.flags & self.FL_HANDLED


#######################################################################
class cse_alife_torrid_zone(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_custom_zone.init(self)
        cse_motion.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_custom_zone.state_read(self, packet)
        cse_motion.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_custom_zone.state_write(self, packet, spawn_id, extended_size)
        cse_motion.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_custom_zone.state_import(self, _if, section, import_type)
        cse_motion.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_custom_zone.state_export(self, _if)
        cse_motion.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_custom_zone.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_custom_zone.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_custom_zone.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_custom_zone.update_export(self, _if)


#######################################################################
class cse_alife_inventory_item(base_entity):
    FLAG_NO_POSITION = 0x8000
    FL_IS_2942 = 0x04
    properties_info = (
        {"name": "condition", "type": "f32", "default": 0.0},
        {"name": "upgrades", "type": "l32szv", "default": []},
    )
    upd_properties_info = (
        {"name": "upd:num_items", "type": "h8", "default": 0},
        {
            "name": "upd:force",
            "type": "f32v3",
            "default": [0.0, 0.0, 0.0],
        },  # junk in COP
        {
            "name": "upd:torque",
            "type": "f32v3",
            "default": [0.0, 0.0, 0.0],
        },  # junk in COP
        {"name": "upd:position", "type": "f32v3", "default": [0.0, 0.0, 0.0]},
        {"name": "upd:quaternion", "type": "f32v4", "default": [0.0, 0.0, 0.0, 0.0]},
        {"name": "upd:angular_velocity", "type": "f32v3", "default": [0.0, 0.0, 0.0]},
        {"name": "upd:linear_velocity", "type": "f32v3", "default": [0.0, 0.0, 0.0]},
        {"name": "upd:enabled", "type": "u8", "default": 0},
        {"name": "upd:quaternion", "type": "q8v4", "default": [0, 0, 0, 0]},  # SOC
        {"name": "upd:angular_velocity", "type": "q8v3", "default": [0, 0, 0]},  # SOC
        {"name": "upd:linear_velocity", "type": "q8v3", "default": [0, 0, 0]},  # SOC
        {"name": "upd:condition", "type": "f32", "default": 0},
        {"name": "upd:timestamp", "type": "u32", "default": 0},
        {"name": "upd:num_items", "type": "u16", "default": 0},  # old format
        {"name": "upd:cse_alife_inventory_item__unk1_u8", "type": "u8", "default": 0},
    )

    @classmethod
    def init(cls, self):
        entity.init_properties(self, cse_alife_inventory_item.properties_info)
        entity.init_properties(self, cse_alife_inventory_item.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if self.version > 52:
            packet.unpack_properties(self, cse_alife_inventory_item.properties_info[0])

        if self.version > 123:
            packet.unpack_properties(self, cse_alife_inventory_item.properties_info[1])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if self.version > 52:
            packet.pack_properties(self, cse_alife_inventory_item.properties_info[0])

        if self.version > 123:
            packet.pack_properties(self, cse_alife_inventory_item.properties_info[1])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if self.version > 52:
            _if.import_properties(
                section,
                self,
                cse_alife_inventory_item.properties_info[0],
            )

        if self.version > 123:
            _if.import_properties(
                section,
                self,
                cse_alife_inventory_item.properties_info[1],
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if self.version > 52:
            _if.export_properties(
                cse_alife_inventory_item.__name__,
                self,
                cse_alife_inventory_item.properties_info[0],
            )

        if self.version > 123:
            _if.export_properties(
                None,
                self,
                cse_alife_inventory_item.properties_info[1],
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        if (self.version >= 122) and (self.version <= 128):
            packet.unpack_properties(
                self,
                cse_alife_inventory_item.upd_properties_info[0],
            )
            if getattr(self, "upd:num_items") != 0:
                packet.unpack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[1 : 4 + 1],
                )
                flags = getattr(self, "upd:num_items") >> 5
                if (flags & 0x2) == 0:
                    packet.unpack_properties(
                        self,
                        cse_alife_inventory_item.upd_properties_info[5],
                    )

                if (flags & 0x4) == 0:
                    packet.unpack_properties(
                        self,
                        cse_alife_inventory_item.upd_properties_info[6],
                    )

                if packet.resid() != 0:
                    packet.unpack_properties(
                        self,
                        cse_alife_inventory_item.upd_properties_info[7],
                    )

        elif (self.version >= 118) and (self.script_version > 5):
            packet.unpack_properties(
                self,
                cse_alife_inventory_item.upd_properties_info[0],
            )
            if getattr(self, "upd:num_items") != 0:
                packet.unpack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[3],
                )
                packet.unpack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[8],
                )
                flags = getattr(self, "upd:num_items") >> 5
                if (flags & 0x02 or flags & 0x04) and packet.resid() == 6:
                    self.flags |= self.FL_IS_2942

                if cse_alife_inventory_item.first_patch(self) or ((flags & 0x02) == 0):
                    if not packet.resid() >= 3:
                        fail("unexpected size")  # unless
                    packet.unpack_properties(
                        self,
                        cse_alife_inventory_item.upd_properties_info[9],
                    )

                if cse_alife_inventory_item.first_patch(self) or ((flags & 0x04) == 0):
                    if not packet.resid() >= 3:
                        fail("unexpected size")  # unless
                    packet.unpack_properties(
                        self,
                        cse_alife_inventory_item.upd_properties_info[10],
                    )

        else:
            if (self.version > 59) and (self.version <= 63):
                packet.unpack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[14],
                )

            packet.unpack_properties(
                self,
                cse_alife_inventory_item.upd_properties_info[11 : 13 + 1],
            )
            flags = getattr(self, "upd:num_items")
            if flags != self.FLAG_NO_POSITION:
                packet.unpack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[3],
                )

            if flags & ~self.FLAG_NO_POSITION:
                packet.unpack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[7],
                )
                packet.unpack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[5 : 6 + 1],
                )
                packet.unpack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[1 : 2 + 1],
                )
                packet.unpack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[4],
                )

    @classmethod
    def update_write(cls, self, packet: data_packet):
        if (self.version >= 122) and (self.version <= 128):
            packet.pack_properties(
                self,
                cse_alife_inventory_item.upd_properties_info[0],
            )
            if getattr(self, "upd:num_items") != 0:
                packet.pack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[1 : 4 + 1],
                )
                flags = getattr(self, "upd:num_items") >> 5
                if (flags & 0x2) == 0:
                    packet.pack_properties(
                        self,
                        cse_alife_inventory_item.upd_properties_info[5],
                    )

                if (flags & 0x4) == 0:
                    packet.pack_properties(
                        self,
                        cse_alife_inventory_item.upd_properties_info[6],
                    )

                if packet.resid() != 0:
                    packet.pack_properties(
                        self,
                        cse_alife_inventory_item.upd_properties_info[7],
                    )

        elif (self.version >= 118) and (self.script_version > 5):
            flags = getattr(self, "upd:num_items")
            mask = flags >> 5
            packet.pack_properties(
                self,
                cse_alife_inventory_item.upd_properties_info[0],
            )
            if flags != 0:
                packet.pack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[3],
                )
                packet.pack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[8],
                )
                if cse_alife_inventory_item.first_patch(self) or ((mask & 0x02) == 0):
                    packet.pack_properties(
                        self,
                        cse_alife_inventory_item.upd_properties_info[9],
                    )

                if cse_alife_inventory_item.first_patch(self) or ((mask & 0x04) == 0):
                    packet.pack_properties(
                        self,
                        cse_alife_inventory_item.upd_properties_info[10],
                    )

        else:
            if (self.version > 59) and (self.version <= 63):
                packet.pack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[14],
                )

            packet.pack_properties(
                self,
                cse_alife_inventory_item.upd_properties_info[11 : 13 + 1],
            )
            flags = getattr(self, "upd:num_items")
            if flags != 0x8000:
                packet.pack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[3],
                )

            if flags & ~0x8000:
                packet.pack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[7],
                )
                packet.pack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[5 : 6 + 1],
                )
                packet.pack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[1 : 2 + 1],
                )
                packet.pack_properties(
                    self,
                    cse_alife_inventory_item.upd_properties_info[4],
                )

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        if (self.version >= 122) and (self.version <= 128):
            _if.import_properties(
                section,
                self,
                cse_alife_inventory_item.upd_properties_info[0],
            )
            if getattr(self, "upd:num_items") != 0:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_inventory_item.upd_properties_info[1 : 4 + 1],
                )
                flags = getattr(self, "upd:num_items") >> 5
                if (flags & 0x2) == 0:
                    _if.import_properties(
                        section,
                        self,
                        cse_alife_inventory_item.upd_properties_info[5],
                    )

                if (flags & 0x4) == 0:
                    _if.import_properties(
                        section,
                        self,
                        cse_alife_inventory_item.upd_properties_info[6],
                    )

                if _if.value(section, "upd:enabled") is not None:
                    _if.import_properties(
                        section,
                        self,
                        cse_alife_inventory_item.upd_properties_info[7],
                    )

        elif (self.version >= 118) and (self.script_version > 5):
            _if.import_properties(
                section,
                self,
                cse_alife_inventory_item.upd_properties_info[0],
            )
            if getattr(self, "upd:num_items") != 0:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_inventory_item.upd_properties_info[3],
                )
                _if.import_properties(
                    section,
                    self,
                    cse_alife_inventory_item.upd_properties_info[8],
                )
                flags = getattr(self, "upd:num_items") >> 5
                if (
                    (flags & 0x02 or flags & 0x04)
                    and (_if.value(section, "upd:angular_velocity") is not None)
                    and (_if.value(section, "upd:linear_velocity") is not None)
                ):
                    self.flags |= self.FL_IS_2942

                if cse_alife_inventory_item.first_patch(self) or ((flags & 0x02) == 0):
                    _if.import_properties(
                        section,
                        self,
                        cse_alife_inventory_item.upd_properties_info[9],
                    )

                if cse_alife_inventory_item.first_patch(self) or ((flags & 0x04) == 0):
                    _if.import_properties(
                        section,
                        self,
                        cse_alife_inventory_item.upd_properties_info[10],
                    )

        else:
            if (self.version > 59) and (self.version <= 63):
                _if.import_properties(
                    section,
                    self,
                    cse_alife_inventory_item.upd_properties_info[14],
                )

            _if.import_properties(
                section,
                self,
                cse_alife_inventory_item.upd_properties_info[11 : 13 + 1],
            )
            flags = getattr(self, "upd:num_items")
            if flags != 0x8000:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_inventory_item.upd_properties_info[3],
                )

            if flags & ~0x8000:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_inventory_item.upd_properties_info[7],
                )
                _if.import_properties(
                    section,
                    self,
                    cse_alife_inventory_item.upd_properties_info[5 : 6 + 1],
                )
                _if.import_properties(
                    section,
                    self,
                    cse_alife_inventory_item.upd_properties_info[1 : 2 + 1],
                )
                _if.import_properties(
                    section,
                    self,
                    cse_alife_inventory_item.upd_properties_info[4],
                )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        if (self.version >= 122) and (self.version <= 128):
            _if.export_properties(
                None,
                self,
                cse_alife_inventory_item.upd_properties_info[0],
            )
            if getattr(self, "upd:num_items") != 0:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_inventory_item.upd_properties_info[1 : 4 + 1],
                )
                flags = getattr(self, "upd:num_items") >> 5
                if (flags & 0x2) == 0:
                    _if.export_properties(
                        None,
                        self,
                        cse_alife_inventory_item.upd_properties_info[5],
                    )

                if (flags & 0x4) == 0:
                    _if.export_properties(
                        None,
                        self,
                        cse_alife_inventory_item.upd_properties_info[6],
                    )

                if (
                    getattr(self, "upd:enabled") == 0
                    or getattr(self, "upd:enabled") == 1
                ):
                    _if.export_properties(
                        None,
                        self,
                        cse_alife_inventory_item.upd_properties_info[7],
                    )

        elif (self.version >= 118) and (self.script_version > 5):
            _if.export_properties(
                None,
                self,
                cse_alife_inventory_item.upd_properties_info[0],
            )
            if getattr(self, "upd:num_items") != 0:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_inventory_item.upd_properties_info[3],
                )
                _if.export_properties(
                    None,
                    self,
                    cse_alife_inventory_item.upd_properties_info[8],
                )
                flags = getattr(self, "upd:num_items") >> 5
                if cse_alife_inventory_item.first_patch(self) or ((flags & 0x02) == 0):
                    _if.export_properties(
                        None,
                        self,
                        cse_alife_inventory_item.upd_properties_info[9],
                    )

                if cse_alife_inventory_item.first_patch(self) or ((flags & 0x04) == 0):
                    _if.export_properties(
                        None,
                        self,
                        cse_alife_inventory_item.upd_properties_info[10],
                    )

        else:
            if (self.version > 59) and (self.version <= 63):
                _if.export_properties(
                    None,
                    self,
                    cse_alife_inventory_item.upd_properties_info[14],
                )

            _if.export_properties(
                None,
                self,
                cse_alife_inventory_item.upd_properties_info[11 : 13 + 1],
            )
            flags = getattr(self, "upd:num_items")
            if flags != 0x8000:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_inventory_item.upd_properties_info[3],
                )

            if flags & ~0x8000:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_inventory_item.upd_properties_info[7],
                )
                _if.export_properties(
                    None,
                    self,
                    cse_alife_inventory_item.upd_properties_info[5 : 6 + 1],
                )
                _if.export_properties(
                    None,
                    self,
                    cse_alife_inventory_item.upd_properties_info[1 : 2 + 1],
                )
                _if.export_properties(
                    None,
                    self,
                    cse_alife_inventory_item.upd_properties_info[4],
                )

    @classmethod
    def first_patch(cls, self):
        return self.flags & cse_alife_inventory_item.FL_IS_2942


#######################################################################
class cse_alife_item(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object_visual.init(self)
        cse_alife_inventory_item.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object_visual.state_read(self, packet)
        if self.version > 39:
            cse_alife_inventory_item.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object_visual.state_write(
            self,
            packet,
            spawn_id,
            extended_size,
        )
        if self.version > 39:
            cse_alife_inventory_item.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object_visual.state_import(self, _if, section, import_type)
        if self.version > 39:
            cse_alife_inventory_item.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object_visual.state_export(self, _if)
        if self.version > 39:
            cse_alife_inventory_item.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        if self.version > 39:
            cse_alife_inventory_item.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        if self.version > 39:
            cse_alife_inventory_item.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        if self.version > 39:
            cse_alife_inventory_item.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        if self.version > 39:
            cse_alife_inventory_item.update_export(self, _if)


#######################################################################
class cse_alife_item_binocular(base_entity):
    properties_info = (
        {"name": "cse_alife_item__unk1_s16", "type": "s16", "default": 0},
        {"name": "cse_alife_item__unk2_s16", "type": "s16", "default": 0},
        {"name": "cse_alife_item__unk3_s8", "type": "s8", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)
        entity.init_properties(self, cse_alife_item_binocular.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item.state_read(self, packet)
        if self.version < 37:
            packet.unpack_properties(self, cse_alife_item_binocular.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item.state_write(self, packet, spawn_id, extended_size)
        if self.version < 37:
            packet.pack_properties(self, cse_alife_item_binocular.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item.state_import(self, _if, section, import_type)
        if self.version < 37:
            _if.import_properties(
                section,
                self,
                cse_alife_item_binocular.properties_info,
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        # TODO WTF??
        cse_alife_item.state_write(self, packet, spawn_id, extended_size)
        if self.version < 37:
            _if.export_properties(None, self, cse_alife_item_binocular.properties_info)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item.update_export(self, _if)


#######################################################################
class cse_alife_item_torch(base_entity):
    flTorchActive = 0x01
    flTorchNightVisionActive = 0x02
    flTorchUnknown = 0x04
    properties_info = (
        {"name": "main_color", "type": "h32", "default": 0x00FFFFFF},
        {"name": "main_color_animator", "type": "sz", "default": ""},
        {"name": "animation", "type": "sz", "default": "$editor"},
        {"name": "ambient_radius", "type": "f32", "default": 0.0},
        {"name": "main_cone_angle", "type": "q8", "default": 0.0},
        {"name": "main_virtual_size", "type": "f32", "default": 0.0},
        {"name": "glow_texture", "type": "sz", "default": ""},
        {"name": "glow_radius", "type": "f32", "default": 0.0},
        {"name": "cse_alife_object_hanging_lamp__unk3_u8", "type": "u16", "default": 0},
    )
    upd_properties_info = ({"name": "upd:torch_flags", "type": "u8", "default": -1},)

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)
        entity.init_properties(self, cse_alife_item_torch.properties_info)
        entity.init_properties(self, cse_alife_item_torch.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if self.version > 20:
            cse_alife_item.state_read(self, packet)

        if self.version < 48:
            packet.unpack_properties(
                self,
                cse_alife_item_torch.properties_info[0 : 5 + 1],
            )
            if self.version > 40:
                packet.unpack_properties(
                    self,
                    cse_alife_item_torch.properties_info[6 : 7 + 1],
                )

            if self.version > 45:
                packet.unpack_properties(self, cse_alife_item_torch.properties_info[8])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if self.version > 20:
            cse_alife_item.state_write(self, packet, spawn_id, extended_size)

        if self.version < 48:
            packet.pack_properties(
                self,
                cse_alife_item_torch.properties_info[0 : 5 + 1],
            )
            if self.version > 40:
                packet.pack_properties(
                    self,
                    cse_alife_item_torch.properties_info[6 : 7 + 1],
                )

            if self.version > 45:
                packet.pack_properties(self, cse_alife_item_torch.properties_info[8])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if self.version > 20:
            cse_alife_item.state_import(self, _if, section, import_type)

        if self.version < 48:
            _if.import_properties(
                section,
                self,
                cse_alife_item_torch.properties_info[0 : 5 + 1],
            )
            if self.version > 40:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_item_torch.properties_info[6 : 7 + 1],
                )

            if self.version > 45:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_item_torch.properties_info[8],
                )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if self.version > 20:
            cse_alife_item.state_export(self, _if)

        if self.version < 48:
            _if.export_properties(
                cse_alife_item_torch.__name__,
                self,
                cse_alife_item_torch.properties_info[0 : 5 + 1],
            )
            if self.version > 40:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_item_torch.properties_info[6 : 7 + 1],
                )

            if self.version > 45:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_item_torch.properties_info[8],
                )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item.update_read(self, packet)
        packet.unpack_properties(self, cse_alife_item_torch.upd_properties_info)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item.update_write(self, packet)
        packet.pack_properties(self, cse_alife_item_torch.upd_properties_info)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item.update_import(self, _if, section)
        _if.import_properties(section, self, cse_alife_item_torch.upd_properties_info)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item.update_export(self, _if)
        _if.export_properties(None, self, cse_alife_item_torch.upd_properties_info)


#######################################################################
class cse_alife_item_detector(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if self.version > 20:
            cse_alife_item.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if self.version > 20:
            cse_alife_item.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if self.version > 20:
            cse_alife_item.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if self.version > 20:
            cse_alife_item.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        if self.version > 20:
            cse_alife_item.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        if self.version > 20:
            cse_alife_item.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        if self.version > 20:
            cse_alife_item.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        if self.version > 20:
            cse_alife_item.update_export(self, _if)


#######################################################################
class cse_alife_item_artefact(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item.update_export(self, _if)


#######################################################################
class cse_alife_item_grenade(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item.update_export(self, _if)


#######################################################################
class cse_alife_item_explosive(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item.update_export(self, _if)


#######################################################################
class cse_alife_item_bolt(base_entity):

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item.update_export(self, _if)


#######################################################################
class cse_alife_item_custom_outfit(base_entity):
    upd_properties_info = ({"name": "upd:condition", "type": "q8", "default": 0},)

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)
        entity.init_properties(self, cse_alife_item_custom_outfit.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item.update_read(self, packet)
        if (self.version >= 118) and (self.script_version > 5):
            packet.unpack_properties(
                self,
                cse_alife_item_custom_outfit.upd_properties_info,
            )

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item.update_write(self, packet)
        if (self.version >= 118) and (self.script_version > 5):
            packet.pack_properties(
                self,
                cse_alife_item_custom_outfit.upd_properties_info,
            )

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item.update_import(self, _if, section)
        if (self.version >= 118) and (self.script_version > 5):
            _if.import_properties(
                section,
                self,
                cse_alife_item_custom_outfit.upd_properties_info,
            )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item.update_export(self, _if)
        if (self.version >= 118) and (self.script_version > 5):
            _if.export_properties(
                None,
                self,
                cse_alife_item_custom_outfit.upd_properties_info,
            )


#######################################################################
class cse_alife_item_helmet(base_entity):
    upd_properties_info = ({"name": "upd:condition", "type": "q8", "default": 0},)

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)
        entity.init_properties(self, cse_alife_item_helmet.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item.update_read(self, packet)
        if (self.version >= 118) and (self.script_version > 5):
            packet.unpack_properties(self, cse_alife_item_helmet.upd_properties_info)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item.update_write(self, packet)
        if (self.version >= 118) and (self.script_version > 5):
            packet.pack_properties(self, cse_alife_item_helmet.upd_properties_info)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item.update_import(self, _if, section)
        if (self.version >= 118) and (self.script_version > 5):
            _if.import_properties(
                section,
                self,
                cse_alife_item_helmet.upd_properties_info,
            )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item.update_export(self, _if)
        if (self.version >= 118) and (self.script_version > 5):
            _if.export_properties(None, self, cse_alife_item_helmet.upd_properties_info)


#######################################################################
class cse_alife_item_pda(base_entity):
    properties_info = (
        {"name": "original_owner", "type": "u16", "default": 0},
        {"name": "specific_character", "type": "sz", "default": ""},
        {"name": "info_portion", "type": "sz", "default": ""},
        {"name": "cse_alife_item_pda__unk1_s32", "type": "s32", "default": -1},
        {"name": "cse_alife_item_pda__unk2_s32", "type": "s32", "default": -1},
    )

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)
        entity.init_properties(self, cse_alife_item_pda.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item.state_read(self, packet)
        if self.version > 58:
            packet.unpack_properties(self, cse_alife_item_pda.properties_info[0])

        if self.version > 89:
            if self.version < 98:
                packet.unpack_properties(
                    self,
                    cse_alife_item_pda.properties_info[3 : 4 + 1],
                )
            else:
                packet.unpack_properties(
                    self,
                    cse_alife_item_pda.properties_info[1 : 2 + 1],
                )

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item.state_write(self, packet, spawn_id, extended_size)
        if self.version > 58:
            packet.pack_properties(self, cse_alife_item_pda.properties_info[0])

        if self.version > 89:
            if self.version < 98:
                packet.pack_properties(
                    self,
                    cse_alife_item_pda.properties_info[3 : 4 + 1],
                )
            else:
                packet.pack_properties(
                    self,
                    cse_alife_item_pda.properties_info[1 : 2 + 1],
                )

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item.state_import(self, _if, section, import_type)
        if self.version > 58:
            _if.import_properties(section, self, cse_alife_item_pda.properties_info[0])

        if self.version > 89:
            if self.version < 98:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_item_pda.properties_info[3 : 4 + 1],
                )
            else:
                _if.import_properties(
                    section,
                    self,
                    cse_alife_item_pda.properties_info[1 : 2 + 1],
                )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item.state_export(self, _if)
        if self.version > 58:
            _if.export_properties(
                cse_alife_item_pda.__name__,
                self,
                cse_alife_item_pda.properties_info[0],
            )

        if self.version > 89:
            if self.version < 98:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_item_pda.properties_info[3 : 4 + 1],
                )
            else:
                _if.export_properties(
                    None,
                    self,
                    cse_alife_item_pda.properties_info[1 : 2 + 1],
                )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item.update_export(self, _if)


#######################################################################
class cse_alife_item_document(base_entity):
    properties_info = (
        {"name": "info_portion", "type": "sz", "default": ""},
        {"name": "info_id", "type": "u16", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)
        entity.init_properties(self, cse_alife_item_document.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item.state_read(self, packet)
        if self.version < 98:
            packet.unpack_properties(self, cse_alife_item_document.properties_info[1])
        else:
            packet.unpack_properties(self, cse_alife_item_document.properties_info[0])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item.state_write(self, packet, spawn_id, extended_size)
        if self.version < 98:
            packet.pack_properties(self, cse_alife_item_document.properties_info[1])
        else:
            packet.pack_properties(self, cse_alife_item_document.properties_info[0])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item.state_import(self, _if, section, import_type)
        if self.version < 98:
            _if.import_properties(
                section,
                self,
                cse_alife_item_document.properties_info[1],
            )
        else:
            _if.import_properties(
                section,
                self,
                cse_alife_item_document.properties_info[0],
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item.state_export(self, _if)
        if self.version < 98:
            _if.export_properties(
                cse_alife_item_document.__name__,
                self,
                cse_alife_item_document.properties_info[1],
            )
        else:
            _if.export_properties(
                cse_alife_item_document.__name__,
                self,
                cse_alife_item_document.properties_info[0],
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item.update_export(self, _if)


#######################################################################
class cse_alife_item_ammo(base_entity):
    properties_info = ({"name": "ammo_left", "type": "u16", "default": 0},)
    upd_properties_info = ({"name": "upd:ammo_left", "type": "u16", "default": 0},)

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)
        entity.init_properties(self, cse_alife_item_ammo.properties_info)
        entity.init_properties(self, cse_alife_item_ammo.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item.state_read(self, packet)
        packet.unpack_properties(self, cse_alife_item_ammo.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, cse_alife_item_ammo.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, cse_alife_item_ammo.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item.state_export(self, _if)
        _if.export_properties(
            cse_alife_item_ammo.__name__,
            self,
            cse_alife_item_ammo.properties_info,
        )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item.update_read(self, packet)
        packet.unpack_properties(self, cse_alife_item_ammo.upd_properties_info)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item.update_write(self, packet)
        packet.pack_properties(self, cse_alife_item_ammo.upd_properties_info)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item.update_import(self, _if, section)
        _if.import_properties(section, self, cse_alife_item_ammo.upd_properties_info)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item.update_export(self, _if)
        _if.export_properties(None, self, cse_alife_item_ammo.upd_properties_info)


#######################################################################
class cse_alife_item_weapon(base_entity):
    flAddonScope = 0x01
    flAddonLauncher = 0x02
    flAddonSilencer = 0x04
    FL_HANDLED = 0x20
    properties_info = (
        {"name": "ammo_current", "type": "u16", "default": 0},
        {"name": "ammo_elapsed", "type": "u16", "default": 0},
        {"name": "weapon_state", "type": "u8", "default": 0},
        {"name": "addon_flags", "type": "u8", "default": 0},
        {"name": "ammo_type", "type": "u8", "default": 0},
        {"name": "cse_alife_item_weapon__unk1_u8", "type": "u8", "default": 0},
    )
    upd_properties_info = (
        {"name": "upd:condition", "type": "q8", "default": 0},
        {"name": "upd:weapon_flags", "type": "u8", "default": 0},
        {"name": "upd:ammo_elapsed", "type": "u16", "default": 0},
        {"name": "upd:addon_flags", "type": "u8", "default": 0},
        {"name": "upd:ammo_type", "type": "u8", "default": 0},
        {"name": "upd:weapon_state", "type": "u8", "default": 0},
        {"name": "upd:weapon_zoom", "type": "u8", "default": 0},
        {"name": "upd:ammo_current", "type": "u16", "default": 0},
        {"name": "upd:position", "type": "f32v3", "default": [0, 0, 0]},
        {"name": "upd:timestamp", "type": "u32", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_item.init(self)
        entity.init_properties(self, cse_alife_item_weapon.properties_info)
        entity.init_properties(self, cse_alife_item_weapon.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item.state_read(self, packet)
        packet.unpack_properties(self, cse_alife_item_weapon.properties_info[0 : 2 + 1])
        if self.version >= 40:
            packet.unpack_properties(self, cse_alife_item_weapon.properties_info[3])

        if self.version > 46:
            packet.unpack_properties(self, cse_alife_item_weapon.properties_info[4])

        if self.version > 122:
            packet.unpack_properties(self, cse_alife_item_weapon.properties_info[5])

        if packet.resid() == 1:  ## LA
            packet.unpack_properties(self, cse_alife_item_weapon.properties_info[5])
            self.flags |= entity.FL_LA

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, cse_alife_item_weapon.properties_info[0 : 2 + 1])
        if self.version >= 40:
            packet.pack_properties(self, cse_alife_item_weapon.properties_info[3])

        if self.version > 46:
            packet.pack_properties(self, cse_alife_item_weapon.properties_info[4])

        if self.version > 122 or (self.flags & (entity.FL_LA == entity.FL_LA)):
            packet.pack_properties(self, cse_alife_item_weapon.properties_info[5])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item.state_import(self, _if, section, import_type)
        _if.import_properties(
            section,
            self,
            cse_alife_item_weapon.properties_info[0 : 2 + 1],
        )
        if self.version >= 40:
            _if.import_properties(
                section,
                self,
                cse_alife_item_weapon.properties_info[3],
            )

        if self.version > 46:
            _if.import_properties(
                section,
                self,
                cse_alife_item_weapon.properties_info[4],
            )

        if self.version > 122 or (self.flags & (entity.FL_LA == entity.FL_LA)):
            _if.import_properties(
                section,
                self,
                cse_alife_item_weapon.properties_info[5],
            )

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item.state_export(self, _if)
        _if.export_properties(
            cse_alife_item_weapon.__name__,
            self,
            cse_alife_item_weapon.properties_info[0 : 2 + 1],
        )
        if self.version >= 40:
            _if.export_properties(None, self, cse_alife_item_weapon.properties_info[3])

        if self.version > 46:
            _if.export_properties(None, self, cse_alife_item_weapon.properties_info[4])

        if self.version > 122 or (self.flags & (entity.FL_LA == entity.FL_LA)):
            _if.export_properties(None, self, cse_alife_item_weapon.properties_info[5])

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item.update_read(self, packet)
        if (self.version >= 118) and (self.script_version > 5):
            packet.unpack_properties(self, cse_alife_item_weapon.upd_properties_info[0])

        if self.version > 39:
            packet.unpack_properties(
                self,
                cse_alife_item_weapon.upd_properties_info[1 : 6 + 1],
            )
        else:
            packet.unpack_properties(self, cse_alife_item_weapon.upd_properties_info[9])
            packet.unpack_properties(self, cse_alife_item_weapon.upd_properties_info[1])
            packet.unpack_properties(self, cse_alife_item_weapon.upd_properties_info[7])
            packet.unpack_properties(self, cse_alife_item_weapon.upd_properties_info[2])
            packet.unpack_properties(self, cse_alife_item_weapon.upd_properties_info[8])
            packet.unpack_properties(
                self,
                cse_alife_item_weapon.upd_properties_info[3 : 5 + 1],
            )

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item.update_write(self, packet)
        if (self.version >= 118) and (self.script_version > 5):
            packet.pack_properties(self, cse_alife_item_weapon.upd_properties_info[0])

        if self.version > 39:
            packet.pack_properties(
                self,
                cse_alife_item_weapon.upd_properties_info[1 : 6 + 1],
            )
        else:
            packet.pack_properties(self, cse_alife_item_weapon.upd_properties_info[9])
            packet.pack_properties(self, cse_alife_item_weapon.upd_properties_info[1])
            packet.pack_properties(self, cse_alife_item_weapon.upd_properties_info[7])
            packet.pack_properties(self, cse_alife_item_weapon.upd_properties_info[2])
            packet.pack_properties(self, cse_alife_item_weapon.upd_properties_info[8])
            packet.pack_properties(
                self,
                cse_alife_item_weapon.upd_properties_info[3 : 5 + 1],
            )

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item.update_import(self, _if, section)
        if (self.version >= 118) and (self.script_version > 5):
            _if.import_properties(
                section,
                self,
                cse_alife_item_weapon.upd_properties_info[0],
            )

        if self.version > 39:
            _if.import_properties(
                section,
                self,
                cse_alife_item_weapon.upd_properties_info[1 : 6 + 1],
            )
        else:
            _if.import_properties(
                section,
                self,
                cse_alife_item_weapon.upd_properties_info[9],
            )
            _if.import_properties(
                section,
                self,
                cse_alife_item_weapon.upd_properties_info[1],
            )
            _if.import_properties(
                section,
                self,
                cse_alife_item_weapon.upd_properties_info[7],
            )
            _if.import_properties(
                section,
                self,
                cse_alife_item_weapon.upd_properties_info[2],
            )
            _if.import_properties(
                section,
                self,
                cse_alife_item_weapon.upd_properties_info[8],
            )
            _if.import_properties(
                section,
                self,
                cse_alife_item_weapon.upd_properties_info[3 : 5 + 1],
            )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item.update_export(self, _if)
        if (self.version >= 118) and (self.script_version > 5):
            _if.export_properties(
                None,
                self,
                cse_alife_item_weapon.upd_properties_info[0],
            )

        if self.version > 39:
            _if.export_properties(
                None,
                self,
                cse_alife_item_weapon.upd_properties_info[1 : 6 + 1],
            )
        else:
            _if.export_properties(
                None,
                self,
                cse_alife_item_weapon.upd_properties_info[9],
            )
            _if.export_properties(
                None,
                self,
                cse_alife_item_weapon.upd_properties_info[1],
            )
            _if.export_properties(
                None,
                self,
                cse_alife_item_weapon.upd_properties_info[7],
            )
            _if.export_properties(
                None,
                self,
                cse_alife_item_weapon.upd_properties_info[2],
            )
            _if.export_properties(
                None,
                self,
                cse_alife_item_weapon.upd_properties_info[8],
            )
            _if.export_properties(
                None,
                self,
                cse_alife_item_weapon.upd_properties_info[3 : 5 + 1],
            )

    def is_handled(self):
        return self.flags & self.FL_HANDLED


#######################################################################
class cse_alife_item_weapon_magazined(base_entity):
    FL_HANDLED = 0x20
    upd_properties_info = (
        {"name": "upd:current_fire_mode", "type": "u8", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_item_weapon.init(self)
        entity.init_properties(
            self,
            cse_alife_item_weapon_magazined.upd_properties_info,
        )

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item_weapon.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item_weapon.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item_weapon.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item_weapon.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item_weapon.update_read(self, packet)
        if getattr(self, "is_handled", None) is not None and self.is_handled():
            return
        packet.unpack_properties(
            self,
            cse_alife_item_weapon_magazined.upd_properties_info,
        )

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item_weapon.update_write(self, packet)
        packet.pack_properties(
            self,
            cse_alife_item_weapon_magazined.upd_properties_info,
        )

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item_weapon.update_import(self, _if, section)
        _if.import_properties(
            section,
            self,
            cse_alife_item_weapon_magazined.upd_properties_info,
        )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item_weapon.update_export(self, _if)
        _if.export_properties(
            None,
            self,
            cse_alife_item_weapon_magazined.upd_properties_info,
        )

    def is_handled(self):
        return self.flags & self.FL_HANDLED


#######################################################################
class cse_alife_item_weapon_magazined_w_gl(base_entity):
    upd_properties_info = ({"name": "upd:grenade_mode", "type": "u8", "default": 0},)

    @classmethod
    def init(cls, self):
        cse_alife_item_weapon_magazined.init(self)
        entity.init_properties(
            self,
            cse_alife_item_weapon_magazined_w_gl.upd_properties_info,
        )

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item_weapon.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item_weapon.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item_weapon_magazined.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item_weapon_magazined.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        if self.version >= 118:
            packet.unpack_properties(
                self,
                cse_alife_item_weapon_magazined_w_gl.upd_properties_info,
            )

        cse_alife_item_weapon_magazined.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        if self.version >= 118:
            packet.pack_properties(
                self,
                cse_alife_item_weapon_magazined_w_gl.upd_properties_info,
            )

        cse_alife_item_weapon_magazined.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item_weapon_magazined.update_import(self, _if, section)
        if self.version >= 118:
            _if.import_properties(
                section,
                self,
                cse_alife_item_weapon_magazined_w_gl.upd_properties_info,
            )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item_weapon_magazined.update_export(self, _if)
        if self.version >= 118:
            _if.export_properties(
                None,
                self,
                cse_alife_item_weapon_magazined_w_gl.upd_properties_info,
            )


#######################################################################
class cse_alife_item_weapon_shotgun(base_entity):
    upd_properties_info = ({"name": "upd:ammo_ids", "type": "l8u8v", "default": []},)

    @classmethod
    def init(cls, self):
        cse_alife_item_weapon_magazined.init(self)
        entity.init_properties(self, cse_alife_item_weapon_shotgun.upd_properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_item_weapon.state_read(self, packet)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_item_weapon.state_write(self, packet, spawn_id, extended_size)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_item_weapon_magazined.state_import(self, _if, section, import_type)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_item_weapon_magazined.state_export(self, _if)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_item_weapon_magazined.update_read(self, packet)
        if getattr(self, "is_handled", None) is not None and self.is_handled():
            return
        packet.unpack_properties(
            self,
            cse_alife_item_weapon_shotgun.upd_properties_info,
        )

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_item_weapon_magazined.update_write(self, packet)
        packet.pack_properties(self, cse_alife_item_weapon_shotgun.upd_properties_info)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_item_weapon_magazined.update_import(self, _if, section)
        _if.import_properties(
            section,
            self,
            cse_alife_item_weapon_shotgun.upd_properties_info,
        )

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_item_weapon_magazined.update_export(self, _if)
        _if.export_properties(
            None,
            self,
            cse_alife_item_weapon_shotgun.upd_properties_info,
        )


#######################################################################
class se_actor(base_entity):
    FL_LEVEL_SPAWN = 0x01
    FL_SAVE = 0x40
    CRandomTask_info = (
        {"name": "inited_tasks", "type": "inited_tasks", "default": []},
        {"name": "rewards", "type": "rewards", "default": []},
        {
            "name": "inited_find_upgrade_tasks",
            "type": "inited_find_upgrade_tasks",
            "default": [],
        },
    )
    object_collection_info = (
        {"name": "m_count", "type": "u16", "default": 0},
        {"name": "m_last_id", "type": "u16", "default": 0},
        {"name": "m_free", "type": "l16u16v", "default": []},
        {"name": "m_given", "type": "l16u16v", "default": []},
    )
    object_collection_task_info = (
        {"name": "task:m_count", "type": "u16", "default": 0},
        {"name": "task:m_last_id", "type": "u16", "default": 0},
        {"name": "task:m_free", "type": "l16u16v", "default": []},
        {"name": "task:m_given", "type": "l16u16v", "default": []},
    )
    CMinigames_info = ({"name": "minigames", "type": "minigames", "default": []},)
    properties_info = (
        {"name": "start_position_filled", "type": "u8", "default": 0},
        {
            "name": "dumb_1",
            "type": "dumb_1",
            "default": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                8,
                0,
                0,
                0,
                0,
                15,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                8,
                0,
                2,
                0,
                116,
                101,
                115,
                116,
                95,
                99,
                114,
                111,
                119,
                107,
                105,
                108,
                108,
                101,
                114,
                0,
                67,
                77,
                71,
                67,
                114,
                111,
                119,
                75,
                105,
                108,
                108,
                101,
                114,
                0,
                118,
                97,
                108,
                105,
                97,
                98,
                108,
                101,
                0,
                0,
                60,
                0,
                0,
                4,
                0,
                0,
                0,
                0,
                10,
                0,
                100,
                0,
                0,
                0,
                0,
                0,
                0,
                10,
                0,
                0,
                0,
                22,
                0,
                116,
                101,
                115,
                116,
                95,
                115,
                104,
                111,
                111,
                116,
                105,
                110,
                103,
                0,
                67,
                77,
                71,
                83,
                104,
                111,
                111,
                116,
                105,
                110,
                103,
                0,
                118,
                97,
                108,
                105,
                97,
                98,
                108,
                101,
                0,
                0,
                0,
                110,
                105,
                108,
                0,
                110,
                105,
                108,
                0,
                110,
                105,
                108,
                0,
                110,
                105,
                108,
                0,
                110,
                105,
                108,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                110,
                105,
                108,
                0,
                38,
                0,
                140,
                0,
                169,
                0,
            ],
        },
        {
            "name": "dumb_2",
            "type": "dumb_2",
            "default": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                8,
                0,
                0,
                0,
                0,
                15,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                8,
                0,
                2,
                0,
                116,
                101,
                115,
                116,
                95,
                99,
                114,
                111,
                119,
                107,
                105,
                108,
                108,
                101,
                114,
                0,
                67,
                77,
                71,
                67,
                114,
                111,
                119,
                75,
                105,
                108,
                108,
                101,
                114,
                0,
                118,
                97,
                108,
                105,
                97,
                98,
                108,
                101,
                0,
                0,
                60,
                0,
                0,
                4,
                0,
                0,
                0,
                0,
                10,
                0,
                100,
                0,
                0,
                0,
                0,
                0,
                0,
                10,
                0,
                0,
                0,
                22,
                0,
                116,
                101,
                115,
                116,
                95,
                115,
                104,
                111,
                111,
                116,
                105,
                110,
                103,
                0,
                67,
                77,
                71,
                83,
                104,
                111,
                111,
                116,
                105,
                110,
                103,
                0,
                118,
                97,
                108,
                105,
                97,
                98,
                108,
                101,
                0,
                0,
                0,
                110,
                105,
                108,
                0,
                110,
                105,
                108,
                0,
                110,
                105,
                108,
                0,
                110,
                105,
                108,
                0,
                110,
                105,
                108,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ],
        },
        {
            "name": "dumb_3",
            "type": "dumb_3",
            "default": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                8,
                0,
                0,
                0,
                0,
                15,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                8,
                0,
                2,
                0,
                116,
                101,
                115,
                116,
                95,
                99,
                114,
                111,
                119,
                107,
                105,
                108,
                108,
                101,
                114,
                0,
                67,
                77,
                71,
                67,
                114,
                111,
                119,
                75,
                105,
                108,
                108,
                101,
                114,
                0,
                118,
                97,
                108,
                105,
                97,
                98,
                108,
                101,
                0,
                0,
                60,
                0,
                0,
                4,
                0,
                0,
                0,
                0,
                10,
                0,
                100,
                0,
                0,
                0,
                0,
                0,
                0,
                10,
                0,
                0,
                0,
                22,
                0,
                116,
                101,
                115,
                116,
                95,
                115,
                104,
                111,
                111,
                116,
                105,
                110,
                103,
                0,
                67,
                77,
                71,
                83,
                104,
                111,
                111,
                116,
                105,
                110,
                103,
                0,
                118,
                97,
                108,
                105,
                97,
                98,
                108,
                101,
                0,
                0,
                0,
                110,
                105,
                108,
                0,
                110,
                105,
                108,
                0,
                110,
                105,
                108,
                0,
                110,
                105,
                108,
                0,
                110,
                105,
                108,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
            ],
        },
    )

    @classmethod
    def init(cls, self):
        cse_alife_creature_actor.init(self)
        entity.init_properties(self, se_actor.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_creature_actor.state_read(self, packet)
        if self.version < 122:
            return
        if self.version > 123:
            packet.set_save_marker(self, "load", 0, "se_actor")
        if self.version >= 128:
            packet.unpack_properties(self, se_actor.properties_info[0])
        elif self.version >= 122:
            if self.is_save():
                self.CRandomTask_read(packet)
                self.object_collection_read(packet)
                self.CMinigames_read(packet)
            elif self.version >= 124:
                packet.unpack_properties(self, se_actor.properties_info[1])
            elif self.version >= 123:
                packet.unpack_properties(self, se_actor.properties_info[2])
            else:
                packet.unpack_properties(self, se_actor.properties_info[3])

        if self.version > 123:
            packet.set_save_marker(self, "load", 1, "se_actor")

    def CRandomTask_read(self, packet):
        packet.set_save_marker(self, "load", 0, "CRandomTask")
        packet.unpack_properties(self, self.CRandomTask_info[0])
        self.object_collection_task_read(packet)
        packet.unpack_properties(self, self.CRandomTask_info[1 : 2 + 1])
        packet.set_save_marker(self, "load", 1, "CRandomTask")

    def object_collection_read(self, packet):
        packet.set_save_marker(self, "load", 0, "object_collection")
        packet.unpack_properties(self, self.object_collection_info)
        packet.set_save_marker(self, "load", 1, "object_collection")

    def object_collection_task_read(self, packet):
        packet.set_save_marker(self, "load", 0, "object_collection")
        packet.unpack_properties(self, self.object_collection_task_info)
        packet.set_save_marker(self, "load", 1, "object_collection")

    def CMinigames_read(self, packet):
        packet.set_save_marker(self, "load", 0, "CMinigames")
        packet.unpack_properties(self, self.CMinigames_info)
        packet.set_save_marker(self, "load", 1, "CMinigames")

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_creature_actor.state_write(self, packet, spawn_id, extended_size)
        if self.version < 122:
            return
        if self.version > 123:
            packet.set_save_marker(self, "save", 0, "se_actor")
        if self.version >= 128:
            packet.pack_properties(self, se_actor.properties_info[0])
        elif self.version >= 122:
            if self.is_save():
                self.CRandomTask_write(packet)
                self.object_collection_write(packet)
                self.CMinigames_write(packet)
            elif self.version >= 124:
                packet.pack_properties(self, se_actor.properties_info[1])
            elif self.version >= 123:
                packet.pack_properties(self, se_actor.properties_info[2])
            else:
                packet.pack_properties(self, se_actor.properties_info[3])

        if self.version > 123:
            packet.set_save_marker(self, "save", 1, "se_actor")

    def CRandomTask_write(self, packet):
        packet.set_save_marker(self, "save", 0, "CRandomTask")
        packet.pack_properties(self, self.CRandomTask_info[0])
        self.object_collection_task_write(packet)
        packet.pack_properties(self, self.CRandomTask_info[1 : 2 + 1])
        packet.set_save_marker(self, "save", 1, "CRandomTask")

    def object_collection_write(self, packet):
        packet.set_save_marker(self, "save", 0, "object_collection")
        packet.pack_properties(self, self.object_collection_info)
        packet.set_save_marker(self, "save", 1, "object_collection")

    def object_collection_task_write(self, packet):
        packet.set_save_marker(self, "save", 0, "object_collection")
        packet.pack_properties(self, self.object_collection_task_info)
        packet.set_save_marker(self, "save", 1, "object_collection")

    def CMinigames_write(self, packet):
        packet.set_save_marker(self, "save", 0, "CMinigames")
        packet.pack_properties(self, self.CMinigames_info)
        packet.set_save_marker(self, "save", 1, "CMinigames")

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_creature_actor.state_import(self, _if, section, import_type)
        if self.version >= 128:
            _if.import_properties(section, self, se_actor.properties_info[0])
        elif self.version >= 122:
            if self.is_save():
                self.CRandomTask_import(_if, section)
                self.object_collection_import(_if, section)
                self.CMinigames_import(_if, section)
            elif self.version >= 124:
                _if.import_properties(section, self, se_actor.properties_info[1])
            elif self.version >= 123:
                _if.import_properties(section, self, se_actor.properties_info[2])
            else:
                _if.import_properties(section, self, se_actor.properties_info[3])

    def CRandomTask_import(self, _if, section):
        _if.import_properties(section, self, self.CRandomTask_info[0])
        self.object_collection_task_import(_if, section)
        _if.import_properties(section, self, self.CRandomTask_info[1 : 2 + 1])

    def object_collection_import(self, _if, section):
        _if.import_properties(section, self, self.object_collection_info)

    def object_collection_task_import(self, _if, section):
        _if.import_properties(section, self, self.object_collection_task_info)

    def CMinigames_import(self, _if, section):
        _if.import_properties(section, self, self.CMinigames_info)

    @classmethod
    def state_export(cls, self, _if: ini_file, arg2=None):
        cse_alife_creature_actor.state_export(self, _if)
        if self.version >= 128:
            _if.export_properties(arg2, self, se_actor.properties_info[0])
        elif self.version >= 122:
            if self.is_save():
                cls.CRandomTask_export(self, _if)
                cls.object_collection_export(self, _if)
                cls.CMinigames_export(self, _if)
            elif self.version >= 124:
                _if.export_properties(arg2, self, se_actor.properties_info[1])
            elif self.version >= 123:
                _if.export_properties(arg2, self, se_actor.properties_info[2])
            else:
                _if.export_properties(arg2, self, se_actor.properties_info[3])

    @classmethod
    def CRandomTask_export(cls, self, _if: ini_file, comment=None):
        _if.export_properties(comment, self, self.CRandomTask_info[0])
        cls.object_collection_export(self, _if)
        _if.export_properties(comment, self, self.CRandomTask_info[1 : 2 + 1])

    @classmethod
    def object_collection_export(cls, self, _if, arg2=None):
        _if.export_properties(arg2, self, self.object_collection_info)

    @classmethod
    def object_collection_task_export(cls, self, _if, arg2=None):
        _if.export_properties(arg2, self, self.object_collection_task_info)

    @classmethod
    def CMinigames_export(cls, self, _if, arg2=None):
        _if.export_properties(arg2, self, self.CMinigames_info)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_creature_actor.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_creature_actor.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_creature_actor.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_creature_actor.update_export(self, _if)

    def is_level(self):
        if self.flags & self.FL_LEVEL_SPAWN:
            return 1

        return 0

    def is_save(self):
        if self.flags & self.FL_SAVE:
            return 1

        return 0


#######################################################################
class se_anomaly_field(base_entity):
    properties_info = (
        {"name": "startup", "type": "u8", "default": 1},
        {"name": "update_time_present", "type": "u8", "default": 0},
        {"name": "zone_count", "type": "u8", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_space_restrictor.init(self)
        entity.init_properties(self, se_anomaly_field.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_space_restrictor.state_read(self, packet)
        if packet.resid() != 3:
            fail("unexpected size")
        packet.unpack_properties(self, se_anomaly_field.properties_info[0])
        if self.startup != 0:
            fail("unexpected value")
        packet.unpack_properties(self, se_anomaly_field.properties_info[1])
        if self.update_time_present != 0:
            fail("unexpected value")
        packet.unpack_properties(self, se_anomaly_field.properties_info[2])
        if self.zone_count != 0:
            fail("unexpected value")

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_space_restrictor.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, se_anomaly_field.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_space_restrictor.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, se_anomaly_field.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_space_restrictor.state_export(self, _if)
        _if.export_properties(
            se_anomaly_field.__name__,
            self,
            se_anomaly_field.properties_info,
        )


#######################################################################
class se_level_changer(base_entity):
    properties_info = (
        {"name": "enabled", "type": "u8", "default": 1},
        {"name": "hint", "type": "sz", "default": "level_changer_invitation"},
    )

    @classmethod
    def init(cls, self):
        cse_alife_level_changer.init(self)
        entity.init_properties(self, se_level_changer.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_level_changer.state_read(self, packet)
        if self.version >= 124:
            packet.set_save_marker(self, "load", 0, "se_level_changer")
            packet.unpack_properties(self, se_level_changer.properties_info)
            packet.set_save_marker(self, "load", 1, "se_level_changer")

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_level_changer.state_write(self, packet, spawn_id, extended_size)
        if self.version >= 124:
            packet.set_save_marker(self, "save", 0, "se_level_changer")
            packet.pack_properties(self, se_level_changer.properties_info)
            packet.set_save_marker(self, "save", 1, "se_level_changer")

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_level_changer.state_import(self, _if, section, import_type)
        if self.version >= 124:
            _if.import_properties(section, self, se_level_changer.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_level_changer.state_export(self, _if)
        if self.version >= 124:
            _if.export_properties(
                se_level_changer.__name__,
                self,
                se_level_changer.properties_info,
            )


#######################################################################
class se_monster(base_entity):
    properties_info = (
        {"name": "under_smart_terrain", "type": "u8", "default": 0},
        {"name": "job_online", "type": "u8", "default": 2},
        {"name": "job_online_condlist", "type": "sz", "default": "nil"},
        {"name": "was_in_smart_terrain", "type": "u8", "default": 0},
        {"name": "squad_id", "type": "sz", "default": "nil"},
        {"name": "sim_forced_online", "type": "u8", "default": 0},
        {"name": "old_lvid", "type": "sz", "default": "nil"},
        {"name": "active_section", "type": "sz", "default": "nil"},
    )

    @classmethod
    def init(cls, self):
        cse_alife_monster_base.init(self)
        cse_alife_monster_rat.init(self)
        entity.init_properties(self, se_monster.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        if (self.section_name == "m_rat_e") and (self.version <= 104):
            cse_alife_monster_rat.state_read(self, packet)
        else:
            cse_alife_monster_base.state_read(self, packet)
            if self.script_version > 0:
                if self.script_version > 10:
                    packet.unpack_properties(
                        self,
                        se_monster.properties_info[6 : 7 + 1],
                    )
                elif self.script_version > 3:
                    packet.unpack_properties(self, se_monster.properties_info[1])
                    if self.script_version > 4:
                        if self.job_online > 2:
                            packet.unpack_properties(
                                self,
                                se_monster.properties_info[2],
                            )

                        if self.script_version > 6:
                            packet.unpack_properties(
                                self,
                                se_monster.properties_info[4],
                            )
                        else:
                            packet.unpack_properties(
                                self,
                                se_monster.properties_info[3],
                            )

                        if self.script_version > 7:
                            packet.unpack_properties(
                                self,
                                se_monster.properties_info[5],
                            )

                elif self.script_version == 2:
                    packet.unpack_properties(self, se_monster.properties_info[0])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        if (self.section_name == "m_rat_e") and (self.version <= 104):
            cse_alife_monster_rat.state_write(self, packet, spawn_id, extended_size)
        else:
            cse_alife_monster_base.state_write(self, packet, spawn_id, extended_size)
            if self.script_version > 0:
                if self.script_version > 10:
                    packet.pack_properties(self, se_monster.properties_info[6 : 7 + 1])
                elif self.script_version > 3:
                    packet.pack_properties(self, se_monster.properties_info[1])
                    if self.script_version > 4:
                        if self.job_online > 2:
                            packet.pack_properties(self, se_monster.properties_info[2])

                        if self.script_version > 6:
                            packet.pack_properties(self, se_monster.properties_info[4])
                        else:
                            packet.pack_properties(self, se_monster.properties_info[3])

                        if self.script_version > 7:
                            packet.pack_properties(self, se_monster.properties_info[5])

                elif self.script_version == 2:
                    packet.pack_properties(self, se_monster.properties_info[0])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        if (self.section_name == "m_rat_e") and (self.version <= 104):
            cse_alife_monster_rat.state_import(self, _if, section, import_type)
        else:
            cse_alife_monster_base.state_import(self, _if, section, import_type)
            _if.import_properties(section, self, se_monster.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        if (self.section_name == "m_rat_e") and (self.version <= 104):
            cse_alife_monster_rat.state_export(self, _if)
        else:
            cse_alife_monster_base.state_export(self, _if)
            _if.export_properties(se_monster.__name__, self, se_monster.properties_info)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        if (self.section_name == "m_rat_e") and (self.version <= 104):
            cse_alife_monster_rat.update_read(self, packet)
        else:
            cse_alife_monster_base.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        if (self.section_name == "m_rat_e") and (self.version <= 104):
            cse_alife_monster_rat.update_write(self, packet)
        else:
            cse_alife_monster_base.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        if (self.section_name == "m_rat_e") and (self.version <= 104):
            cse_alife_monster_rat.update_import(self, _if, section)
        else:
            cse_alife_monster_base.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        if (self.section_name == "m_rat_e") and (self.version <= 104):
            cse_alife_monster_rat.update_export(self, _if)
        else:
            cse_alife_monster_base.update_export(self, _if)


#######################################################################
class se_respawn(base_entity):
    properties_info = (
        {"name": "spawned_obj", "type": "l8u16v", "default": []},
        {"name": "next_spawn_time_present", "type": "u8", "default": 0},  # +#LA
    )

    @classmethod
    def init(cls, self):
        cse_alife_smart_zone.init(self)
        entity.init_properties(self, se_respawn.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_smart_zone.state_read(self, packet)
        if self.version >= 116:
            packet.unpack_properties(self, se_respawn.properties_info[0])

        if (
            packet.resid() == 1
        ):  # or (self.flags & entity.FL_LA == entity.FL_LA)) {  // temporary
            packet.unpack_properties(self, se_respawn.properties_info[1])
            self.flags |= entity.FL_LA

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_smart_zone.state_write(self, packet, spawn_id, extended_size)
        if self.version >= 116:
            packet.pack_properties(self, se_respawn.properties_info[0])

        if self.flags & (entity.FL_LA == entity.FL_LA):
            packet.pack_properties(self, se_respawn.properties_info[1])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_smart_zone.state_import(self, _if, section, import_type)
        if self.version >= 116:
            _if.import_properties(section, self, se_respawn.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_smart_zone.state_export(self, _if)
        if self.version >= 116:
            _if.export_properties(se_respawn.__name__, self, se_respawn.properties_info)


#######################################################################
class se_sim_faction(base_entity):
    properties_info = (
        {"name": "community_player", "type": "u8", "default": 0},
        {"name": "start_position_filled", "type": "u8", "default": 0},
        {"name": "current_expansion_level", "type": "u8", "default": 0},
        {"name": "last_spawn_time", "type": "CTime", "default": 0},
        {"name": "squad_target_cache", "type": "l8szu16v", "default": []},
        {"name": "random_tasks", "type": "l8u16u16v", "default": []},
        {"name": "current_attack_quantity", "type": "l8u16u8v", "default": []},
        {"name": "squads", "type": "sim_squads", "default": []},
    )

    @classmethod
    def init(cls, self):
        cse_alife_smart_zone.init(self)
        entity.init_properties(self, se_sim_faction.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_smart_zone.state_read(self, packet)
        if self.version < 122:
            return
        if self.version >= 124:
            packet.set_save_marker(self, "load", 0, "se_sim_faction")
        packet.unpack_properties(self, se_sim_faction.properties_info)
        if self.version >= 124:
            packet.set_save_marker(self, "load", 1, "se_sim_faction")

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_smart_zone.state_write(self, packet, spawn_id, extended_size)
        if self.version < 122:
            return
        if self.version >= 124:
            packet.set_save_marker(self, "save", 0, "se_sim_faction")
        packet.pack_properties(self, se_sim_faction.properties_info)
        if self.version >= 124:
            packet.set_save_marker(self, "save", 1, "se_sim_faction")

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_smart_zone.state_import(self, _if, section, import_type)
        if self.version < 122:
            return
        _if.import_properties(section, self, se_sim_faction.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_smart_zone.state_export(self, _if)
        if self.version < 122:
            return
        _if.export_properties(
            se_sim_faction.__name__,
            self,
            se_sim_faction.properties_info,
        )


#######################################################################
class sim_squad_scripted(base_entity):
    properties_info = (
        {"name": "current_target_id", "type": "sz", "default": ""},
        {"name": "respawn_point_id", "type": "sz", "default": ""},
        {"name": "respawn_point_prop_section", "type": "sz", "default": ""},
        {"name": "smart_id", "type": "sz", "default": ""},
    )

    @classmethod
    def init(cls, self):
        cse_alife_online_offline_group.init(self)
        entity.init_properties(self, sim_squad_scripted.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_online_offline_group.state_read(self, packet)
        packet.set_save_marker(self, "load", 0, "sim_squad_scripted")
        packet.unpack_properties(self, sim_squad_scripted.properties_info)
        packet.set_save_marker(self, "load", 1, "sim_squad_scripted")

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_online_offline_group.state_write(
            self,
            packet,
            spawn_id,
            extended_size,
        )
        packet.set_save_marker(self, "save", 0, "sim_squad_scripted")
        packet.pack_properties(self, sim_squad_scripted.properties_info)
        packet.set_save_marker(self, "save", 1, "sim_squad_scripted")

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_online_offline_group.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, sim_squad_scripted.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_online_offline_group.state_export(self, _if)
        _if.export_properties(
            sim_squad_scripted.__name__,
            self,
            sim_squad_scripted.properties_info,
        )


###########################################
class se_smart_cover(base_entity):
    properties_info = (
        {"name": "last_description", "type": "sz", "default": ""},
        {"name": "loopholes", "type": "l8szbv", "default": []},
    )

    @classmethod
    def init(cls, self):
        cse_smart_cover.init(self)
        entity.init_properties(self, se_smart_cover.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_smart_cover.state_read(self, packet)
        if self.version >= 128:
            packet.unpack_properties(self, se_smart_cover.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_smart_cover.state_write(self, packet, spawn_id, extended_size)
        if self.version >= 128:
            packet.pack_properties(self, se_smart_cover.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_smart_cover.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, se_smart_cover.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_smart_cover.state_export(self, _if)
        _if.export_properties(
            se_smart_cover.__name__,
            self,
            se_smart_cover.properties_info,
        )


#######################################################################
class se_smart_terrain(base_entity):
    FL_LEVEL_SPAWN = 0x01
    combat_manager_properties = (
        ###CS
        {"name": "actor_defence_come", "type": "u8", "default": 0},
        {"name": "combat_quest", "type": "sz", "default": "nil"},
        {"name": "task", "type": "u16", "default": 0xFFFF},
        {"name": "see_actor_enemy", "type": "sz", "default": "nil"},
        {"name": "see_actor_enemy_time", "type": "complex_time", "default": 0},
        {"name": "squads", "type": "squads", "default": []},
        {"name": "force_online", "type": "u8", "default": 0},
        {"name": "force_online_squads", "type": "l8szv", "default": []},
    )
    cover_manager_properties = (
        ###CS
        {"name": "is_valid", "type": "u8", "default": 0},
        {"name": "covers", "type": "covers", "default": []},
    )
    cs_cop_properties_info = (
        {"name": "arriving_npc", "type": "l8u16v", "default": []},
        {"name": "npc_info", "type": "npc_info", "default": []},
        {"name": "dead_times", "type": "times", "default": []},
        {"name": "is_base_on_actor_control", "type": "u8", "default": 0},
        {"name": "status", "type": "u8", "default": 0},
        {"name": "alarm_time", "type": "CTime", "default": 0},
        {"name": "is_respawn_point", "type": "u8", "default": 0},
        {"name": "respawn_count", "type": "l8szbv", "default": []},
        {"name": "last_respawn_update", "type": "complex_time", "default": 0},
        {"name": "population", "type": "u8", "default": 0},
    )
    soc_properties_info = (
        {"name": "duration_end", "type": "CTime", "default": 0},
        {"name": "idle_end", "type": "CTime", "default": 0},
        {"name": "gulag_working", "type": "u8", "default": 0},
        {"name": "casualities", "type": "u8", "default": 0},
        {"name": "state", "type": "u8", "default": 0},
        {"name": "stateBegin", "type": "CTime", "default": 0},
        {"name": "population", "type": "u8", "default": 0},
        {"name": "population_comed", "type": "u8", "default": 0},
        {"name": "population_non_exclusive", "type": "u8", "default": 0},
        {"name": "jobs", "type": "jobs", "default": []},
        {"name": "npc_info", "type": "npc_info", "default": []},
        {"name": "population_locked", "type": "u8", "default": 0},
    )
    old_properties_info = (
        {"name": "gulagN", "type": "u8", "default": 0},
        {"name": "duration_end", "type": "CTime", "default": 0},
        {"name": "idle_end", "type": "CTime", "default": 0},
        {"name": "npc_info", "type": "npc_info", "default": []},
        {"name": "state", "type": "u8", "default": 0},
        {"name": "stateBegin", "type": "u32", "default": 0},
        {"name": "stateBegin", "type": "CTime", "default": 0},
        {"name": "casualities", "type": "u8", "default": 0},
        {"name": "jobs", "type": "l8u32v", "default": []},
    )

    @classmethod
    def init(cls, self):
        cse_alife_smart_zone.init(self)
        entity.init_properties(self, self.soc_properties_info)
        entity.init_properties(self, self.cs_cop_properties_info)
        entity.init_properties(self, self.cover_manager_properties)
        entity.init_properties(self, self.combat_manager_properties)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_smart_zone.state_read(self, packet)
        # 	return if self.is_level();
        if self.version >= 122:
            self.state_read_cs_cop(packet)
        elif self.version >= 117:
            self.state_read_soc(packet)
        elif self.version >= 95:
            self.state_read_old(packet)

    def state_read_old(self, packet):
        packet.unpack_properties(self, self.old_properties_info[0 : 3 + 1])
        if self.script_version >= 1 and self.gulagN != 0:
            packet.unpack_properties(self, self.old_properties_info[4])
            if self.version < 102:
                packet.unpack_properties(self, self.old_properties_info[5])
            if self.version >= 102:
                packet.unpack_properties(self, self.old_properties_info[6])
            packet.unpack_properties(self, self.old_properties_info[7 : 8 + 1])

    def state_read_soc(self, packet):
        packet.unpack_properties(self, self.soc_properties_info[0 : 2 + 1])
        if self.gulag_working != 0:
            packet.unpack_properties(self, self.soc_properties_info[3 : 5 + 1])
            if self.script_version > 5:
                packet.unpack_properties(self, self.soc_properties_info[6 : 8 + 1])

            packet.unpack_properties(self, self.soc_properties_info[9 : 10 + 1])
            if self.script_version > 4:
                packet.unpack_properties(self, self.soc_properties_info[11])

    def state_read_cs_cop(self, packet):
        if self.version > 123:
            packet.set_save_marker(self, "load", 0, "se_smart_terrain")
        if self.version >= 128:
            packet.unpack_properties(self, self.cs_cop_properties_info[0])
        else:
            self.CCombat_manager_read(packet)

        packet.unpack_properties(self, self.cs_cop_properties_info[1 : 2 + 1])
        if self.version > 124:
            if self.script_version > 9:
                packet.unpack_properties(self, self.cs_cop_properties_info[3])
                if self.is_base_on_actor_control == 1:
                    if self.version > 123:
                        packet.set_save_marker(self, "load", 0, "CBaseOnActorControl")
                    packet.unpack_properties(
                        self,
                        self.cs_cop_properties_info[4 : 5 + 1],
                    )
                    if self.version > 123:
                        packet.set_save_marker(self, "load", 1, "CBaseOnActorControl")

            packet.unpack_properties(self, self.cs_cop_properties_info[6])
            if self.is_respawn_point == 1:
                packet.unpack_properties(self, self.cs_cop_properties_info[7])
                if self.script_version > 11:
                    packet.unpack_properties(self, self.cs_cop_properties_info[8])

            packet.unpack_properties(self, self.cs_cop_properties_info[9])

        if self.version > 123:
            packet.set_save_marker(self, "load", 1, "se_smart_terrain")

    def CCombat_manager_read(self, packet):
        if self.version > 123:
            packet.set_save_marker(self, "load", 0, "CCombat_manager")
        packet.unpack_properties(self, self.combat_manager_properties)
        self.CCover_manager_read(packet)
        if self.version > 123:
            packet.set_save_marker(self, "load", 1, "CCombat_manager")

    def CCover_manager_read(self, packet):
        if self.version > 123:
            packet.set_save_marker(self, "load", 0, "CCover_manager")
        packet.unpack_properties(self, self.cover_manager_properties)
        if self.version > 123:
            packet.set_save_marker(self, "load", 1, "CCover_manager")

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_smart_zone.state_write(self, packet, spawn_id, extended_size)
        # 	return if self.is_level();
        if self.version >= 122:
            self.state_write_cs_cop(packet, spawn_id, extended_size)
        elif self.version >= 117:
            self.state_write_soc(packet, spawn_id, extended_size)
        elif self.version >= 95:
            self.state_write_old(packet, spawn_id, extended_size)

    def state_write_old(self, packet, spawn_id, extended_size):
        packet.pack_properties(self, self.old_properties_info[0 : 3 + 1])
        if self.script_version >= 1 and self.gulagN != 0:
            packet.pack_properties(self, self.old_properties_info[4])
            if self.version < 102:
                packet.pack_properties(self, self.old_properties_info[5])
            if self.version >= 102:
                packet.pack_properties(self, self.old_properties_info[6])
            packet.pack_properties(self, self.old_properties_info[7 : 8 + 1])

    def state_write_soc(self, packet, spawn_id, extended_size):
        packet.pack_properties(self, self.soc_properties_info[0 : 2 + 1])
        if self.gulag_working != 0:
            packet.pack_properties(self, self.soc_properties_info[3 : 5 + 1])
            if self.script_version > 5:
                packet.pack_properties(self, self.soc_properties_info[6 : 8 + 1])

            packet.pack_properties(self, self.soc_properties_info[9 : 10 + 1])
            if self.script_version > 4:
                packet.pack_properties(self, self.soc_properties_info[11])

    def state_write_cs_cop(self, packet, spawn_id, extended_size):
        if self.version > 123:
            packet.set_save_marker(self, "save", 0, "se_smart_terrain")
        if self.version >= 128:
            packet.pack_properties(self, self.cs_cop_properties_info[0])
        else:
            self.CCombat_manager_write(packet, spawn_id, extended_size)

        packet.pack_properties(self, self.cs_cop_properties_info[1 : 2 + 1])
        if self.version > 124:
            if self.script_version > 9:
                packet.pack_properties(self, self.cs_cop_properties_info[3])
                if self.is_base_on_actor_control == 1:
                    if self.version > 123:
                        packet.set_save_marker(self, "save", 0, "CBaseOnActorControl")
                    packet.pack_properties(self, self.cs_cop_properties_info[4 : 5 + 1])
                    if self.version > 123:
                        packet.set_save_marker(self, "save", 1, "CBaseOnActorControl")

            packet.pack_properties(self, self.cs_cop_properties_info[6])
            if self.is_respawn_point == 1:
                packet.pack_properties(self, self.cs_cop_properties_info[7])
                if self.script_version > 11:
                    packet.pack_properties(self, self.cs_cop_properties_info[8])

            packet.pack_properties(self, self.cs_cop_properties_info[9])

        if self.version > 123:
            packet.set_save_marker(self, "save", 1, "se_smart_terrain")

    def CCombat_manager_write(self, packet, spawn_id, extended_size):
        if self.version > 123:
            packet.set_save_marker(self, "save", 0, "CCombat_manager")
        packet.pack_properties(self, self.combat_manager_properties)
        self.CCover_manager_write(packet, spawn_id, extended_size)
        if self.version > 123:
            packet.set_save_marker(self, "save", 1, "CCombat_manager")

    def CCover_manager_write(self, packet, spawn_id, extended_size):
        if self.version > 123:
            packet.set_save_marker(self, "save", 0, "CCover_manager")
        packet.pack_properties(self, self.cover_manager_properties)
        if self.version > 123:
            packet.set_save_marker(self, "save", 1, "CCover_manager")

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_smart_zone.state_import(self, _if, section, import_type)
        # 	return if self.is_level();
        if self.version >= 122:
            self.state_import_cs_cop(_if, section)
        elif self.version >= 117:
            self.state_import_soc(_if, section)
        elif self.version >= 95:
            self.state_import_old(_if, section)

    def state_import_old(self, _if, section):
        _if.import_properties(section, self, self.old_properties_info[0 : 3 + 1])
        if self.script_version >= 1 and self.gulagN != 0:
            _if.import_properties(section, self, self.old_properties_info[4])
            if self.version < 102:
                _if.import_properties(section, self, self.old_properties_info[5])
            if self.version >= 102:
                _if.import_properties(section, self, self.old_properties_info[6])
            _if.import_properties(section, self, self.old_properties_info[7 : 8 + 1])

    def state_import_soc(self, _if, section):
        _if.import_properties(section, self, self.soc_properties_info[0 : 2 + 1])
        if self.gulag_working != 0:
            _if.import_properties(section, self, self.soc_properties_info[3 : 5 + 1])
            if self.script_version > 5:
                _if.import_properties(
                    section,
                    self,
                    self.soc_properties_info[6 : 8 + 1],
                )

            _if.import_properties(section, self, self.soc_properties_info[9 : 10 + 1])
            if self.script_version > 4:
                _if.import_properties(section, self, self.soc_properties_info[11])

    def state_import_cs_cop(self, _if, section):
        if self.version >= 128:
            _if.import_properties(section, self, self.cs_cop_properties_info[0])
        else:
            self.CCombat_manager_import(_if, section)

        _if.import_properties(section, self, self.cs_cop_properties_info[1 : 2 + 1])
        if self.script_version > 9:
            _if.import_properties(section, self, self.cs_cop_properties_info[3])
            if self.is_base_on_actor_control == 1:
                _if.import_properties(
                    section,
                    self,
                    self.cs_cop_properties_info[4 : 5 + 1],
                )

        _if.import_properties(section, self, self.cs_cop_properties_info[6])
        if self.is_respawn_point == 1:
            _if.import_properties(section, self, self.cs_cop_properties_info[7])
            if self.script_version > 11:
                _if.import_properties(section, self, self.cs_cop_properties_info[8])

        _if.import_properties(section, self, self.cs_cop_properties_info[9])

    def CCombat_manager_import(self, _if, section):
        _if.import_properties(section, self, self.combat_manager_properties)
        self.CCover_manager_import(_if, section)

    def CCover_manager_import(self, _if, section):
        _if.import_properties(section, self, self.cover_manager_properties)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_smart_zone.state_export(self, _if)
        # 	return if self.is_level();
        if self.version >= 122:
            self.state_export_cs_cop(_if)
        elif self.version >= 117:
            self.state_export_soc(_if)
        elif self.version >= 95:
            self.state_export_old(_if)

    def state_export_old(self, _if):
        _if.export_properties(
            self.__class__.__name__,
            self,
            self.old_properties_info[0 : 3 + 1],
        )
        if self.script_version >= 1 and self.gulagN != 0:
            _if.export_properties(None, self, self.old_properties_info[4])
            if self.version < 102:
                _if.export_properties(None, self, self.old_properties_info[5])
            if self.version >= 102:
                _if.export_properties(None, self, self.old_properties_info[6])
            _if.export_properties(None, self, self.old_properties_info[7 : 8 + 1])

    def state_export_soc(self, _if):
        _if.export_properties(
            self.__class__.__name__,
            self,
            self.soc_properties_info[0 : 2 + 1],
        )
        if self.gulag_working != 0:
            _if.export_properties(None, self, self.soc_properties_info[3 : 5 + 1])
            if self.script_version > 5:
                _if.export_properties(None, self, self.soc_properties_info[6 : 8 + 1])

            _if.export_properties(None, self, self.soc_properties_info[9 : 10 + 1])
            if self.script_version > 4:
                _if.export_properties(None, self, self.soc_properties_info[11])

    def state_export_cs_cop(self, _if):
        if self.version >= 128:
            _if.export_properties(None, self, self.cs_cop_properties_info[0])
        else:
            self.CCombat_manager_export(_if)

        _if.export_properties(None, self, self.cs_cop_properties_info[1 : 2 + 1])
        if self.script_version > 9:
            _if.export_properties(None, self, self.cs_cop_properties_info[3])
            if self.is_base_on_actor_control == 1:
                _if.export_properties(
                    None,
                    self,
                    self.cs_cop_properties_info[4 : 5 + 1],
                )

        _if.export_properties(None, self, self.cs_cop_properties_info[6])
        if self.is_respawn_point == 1:
            _if.export_properties(None, self, self.cs_cop_properties_info[7])
            if self.script_version > 11:
                _if.export_properties(None, self, self.cs_cop_properties_info[8])

        _if.export_properties(None, self, self.cs_cop_properties_info[9])

    def CCombat_manager_export(self, _if):
        _if.export_properties(None, self, self.combat_manager_properties)
        self.CCover_manager_export(_if)

    def CCover_manager_export(self, _if):
        _if.export_properties(None, self, self.cover_manager_properties)

    def is_level(self):
        if self.flags & self.FL_LEVEL_SPAWN:
            return 1

        return 0


#######################################################################
class se_stalker(base_entity):
    FL_HANDLED = 0x20

    properties_info = (
        {"name": "under_smart_terrain", "type": "u8", "default": 0},
        {"name": "job_online", "type": "u8", "default": 2},
        {"name": "job_online_condlist", "type": "sz", "default": "nil"},
        {"name": "was_in_smart_terrain", "type": "u8", "default": 0},
        {"name": "death_dropped", "type": "u8", "default": 0},
        {"name": "squad_id", "type": "sz", "default": "nil"},
        {"name": "sim_forced_online", "type": "u8", "default": 0},
        {"name": "old_lvid", "type": "sz", "default": "nil"},
        {"name": "active_section", "type": "sz", "default": "nil"},
        {"name": "pda_dlg_count", "type": "u8", "default": 0},  # +#LA
        {"name": "pda_dlg_update", "type": "s32", "default": 0},  # +#LA
    )

    @classmethod
    def init(cls, self):
        cse_alife_human_stalker.init(self)
        entity.init_properties(self, se_stalker.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_human_stalker.state_read(self, packet)
        if self.script_version is not None:
            if self.script_version > 10:
                packet.unpack_properties(self, se_stalker.properties_info[7 : 8 + 1])
                packet.unpack_properties(self, se_stalker.properties_info[4])
            elif self.script_version > 2:
                packet.unpack_properties(self, se_stalker.properties_info[1])
                if self.script_version > 4:
                    if self.job_online > 2:
                        packet.unpack_properties(self, se_stalker.properties_info[2])

                    if self.script_version > 6:
                        packet.unpack_properties(
                            self,
                            se_stalker.properties_info[4 : 5 + 1],
                        )
                    elif self.script_version > 5:
                        packet.unpack_properties(
                            self,
                            se_stalker.properties_info[3 : 4 + 1],
                        )
                        if (packet.resid() > 0) or (
                            self.flags & (entity.FL_LA == entity.FL_LA)
                        ):
                            packet.unpack_properties(
                                self,
                                se_stalker.properties_info[9 : 10 + 1],
                            )
                            self.flags |= entity.FL_LA

                    else:
                        packet.unpack_properties(self, se_stalker.properties_info[3])

                    if self.script_version > 7:
                        packet.unpack_properties(self, se_stalker.properties_info[6])

            elif self.script_version == 2:
                packet.unpack_properties(self, se_stalker.properties_info[0])

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_human_stalker.state_write(self, packet, spawn_id, extended_size)
        if self.script_version is not None:
            if self.script_version > 10:
                packet.pack_properties(self, se_stalker.properties_info[7 : 8 + 1])
                packet.pack_properties(self, se_stalker.properties_info[4])
            elif self.script_version > 2:
                packet.pack_properties(self, se_stalker.properties_info[1])
                if self.script_version > 4:
                    if self.job_online > 2:
                        packet.pack_properties(self, se_stalker.properties_info[2])

                    if self.script_version > 6:
                        packet.pack_properties(
                            self,
                            se_stalker.properties_info[4 : 5 + 1],
                        )
                    elif self.script_version > 5:
                        packet.pack_properties(
                            self,
                            se_stalker.properties_info[3 : 4 + 1],
                        )
                        if self.flags & (entity.FL_LA == entity.FL_LA):
                            packet.pack_properties(
                                self,
                                se_stalker.properties_info[9 : 10 + 1],
                            )

                    else:
                        packet.pack_properties(self, se_stalker.properties_info[3])

                    if self.script_version > 7:
                        packet.pack_properties(self, se_stalker.properties_info[6])

            elif self.script_version == 2:
                packet.pack_properties(self, se_stalker.properties_info[0])

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_human_stalker.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, se_stalker.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_human_stalker.state_export(self, _if)
        _if.export_properties(se_stalker.__name__, self, se_stalker.properties_info)

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_human_stalker.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_human_stalker.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_human_stalker.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_human_stalker.update_export(self, _if)

    def is_handled(self):
        return self.flags & self.FL_HANDLED


#######################################################################
class se_turret_mgun(base_entity):
    properties_info = ({"name": "health", "type": "f32", "default": 1.0},)

    @classmethod
    def init(cls, self):
        cse_alife_helicopter.init(self)
        entity.init_properties(self, se_turret_mgun.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_helicopter.state_read(self, packet)
        packet.unpack_properties(self, se_turret_mgun.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_helicopter.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, se_turret_mgun.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_helicopter.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, se_turret_mgun.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_helicopter.state_export(self, _if)
        _if.export_properties(
            se_turret_mgun.__name__,
            self,
            se_turret_mgun.properties_info,
        )


#######################################################################
class se_zone_anom(base_entity):
    FL_LEVEL_SPAWN = 0x01
    properties_info = (
        {"name": "last_spawn_time", "type": "complex_time", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_anomalous_zone.init(self)
        entity.init_properties(self, se_zone_anom.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_anomalous_zone.state_read(self, packet)
        if self.is_level() and (packet.resid() == 0):
            return
        if (self.version < 128) and (self.section_name.startswith("zone_field")):
            return
        if self.version >= 118:
            packet.unpack_properties(self, se_zone_anom.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_anomalous_zone.state_write(self, packet, spawn_id, extended_size)
        # 	return if self.is_level();
        if (self.version < 128) and (self.section_name.startswith("zone_field")):
            return
        if self.version >= 118:
            packet.pack_properties(self, se_zone_anom.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_anomalous_zone.state_import(self, _if, section, import_type)
        # 	return if self.is_level();
        if (self.version < 128) and (self.section_name.startswith("zone_field")):
            return
        if self.version >= 118:
            _if.import_properties(section, self, se_zone_anom.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_anomalous_zone.state_export(self, _if)
        # 	return if self.is_level();
        if (self.version < 128) and (self.section_name.startswith("zone_field")):
            return
        if self.version >= 118:
            _if.export_properties(
                se_zone_anom.__name__,
                self,
                se_zone_anom.properties_info,
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_anomalous_zone.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_anomalous_zone.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_anomalous_zone.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_anomalous_zone.update_export(self, _if)

    def is_level(self):
        if self.flags & self.FL_LEVEL_SPAWN:
            return 1

        return 0


#######################################################################
class se_zone_visual(base_entity):
    FL_LEVEL_SPAWN = 0x01
    properties_info = (
        {"name": "last_spawn_time", "type": "complex_time", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_zone_visual.init(self)
        entity.init_properties(self, se_zone_visual.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_zone_visual.state_read(self, packet)
        if self.is_level() and (packet.resid() == 0):
            return
        if self.version >= 118:
            packet.unpack_properties(self, se_zone_visual.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_zone_visual.state_write(self, packet, spawn_id, extended_size)
        if self.is_level():
            return
        if self.version >= 118:
            packet.pack_properties(self, se_zone_visual.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_zone_visual.state_import(self, _if, section, import_type)
        if self.is_level():
            return
        if self.version >= 118:
            _if.import_properties(section, self, se_zone_visual.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_zone_visual.state_export(self, _if)
        if self.is_level():
            return
        if self.version >= 118:
            _if.export_properties(
                se_zone_visual.__name__,
                self,
                se_zone_visual.properties_info,
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_zone_visual.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_zone_visual.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_zone_visual.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_zone_visual.update_export(self, _if)

    def is_level(self):
        if self.flags & self.FL_LEVEL_SPAWN:
            return 1

        return 0


#######################################################################
class se_zone_torrid(base_entity):
    FL_LEVEL_SPAWN = 0x01
    properties_info = (
        {"name": "last_spawn_time", "type": "complex_time", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_torrid_zone.init(self)
        entity.init_properties(self, se_zone_torrid.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_torrid_zone.state_read(self, packet)
        if self.is_level() and (packet.resid() == 0):
            return
        if self.version >= 128:
            packet.unpack_properties(self, se_zone_torrid.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_torrid_zone.state_write(self, packet, spawn_id, extended_size)
        if self.is_level():
            return
        if self.version >= 128:
            packet.pack_properties(self, se_zone_torrid.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_torrid_zone.state_import(self, _if, section, import_type)
        if self.is_level():
            return
        if self.version >= 128:
            _if.import_properties(section, self, se_zone_torrid.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_torrid_zone.state_export(self, _if)
        if self.is_level():
            return
        if self.version >= 128:
            _if.export_properties(
                se_zone_torrid.__name__,
                self,
                se_zone_torrid.properties_info,
            )

    @classmethod
    def update_read(cls, self, packet: data_packet):
        cse_alife_torrid_zone.update_read(self, packet)

    @classmethod
    def update_write(cls, self, packet: data_packet):
        cse_alife_torrid_zone.update_write(self, packet)

    @classmethod
    def update_import(cls, self, _if: ini_file, section: str):
        cse_alife_torrid_zone.update_import(self, _if, section)

    @classmethod
    def update_export(cls, self, _if: ini_file):
        cse_alife_torrid_zone.update_export(self, _if)

    def is_level(self):
        if self.flags & self.FL_LEVEL_SPAWN:
            return 1

        return 0


#######################################################################
class se_safe(base_entity):
    properties_info = (
        {"name": "items_spawned", "type": "u8", "default": 0},
        {"name": "safe_locked", "type": "u8", "default": 0},
        {"name": "quantity", "type": "u16", "default": 0},  # +#LA
    )

    @classmethod
    def init(cls, self):
        cse_alife_object_physic.init(self)
        entity.init_properties(self, se_safe.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        self.flags |= entity.FL_LA
        cse_alife_object_physic.state_read(self, packet)
        packet.unpack_properties(self, se_safe.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_object_physic.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, se_safe.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_object_physic.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, se_safe.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_object_physic.state_export(self, _if)
        _if.export_properties(se_safe.__name__, self, se_safe.properties_info)


###########################################################################
class se_car(base_entity):  # +#LA

    properties_info = (
        {"name": "se_car__unk1_u8", "type": "u8", "default": 0},
        {"name": "se_car__unk2_f32", "type": "f32", "default": 1.0},
        {"name": "se_car__unk3_u16", "type": "u16", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_car.init(self)
        entity.init_properties(self, se_car.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        self.flags |= entity.FL_LA
        cse_alife_car.state_read(self, packet)
        if packet.resid() != 0:
            packet.unpack_properties(self, se_car.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_car.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, se_car.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_car.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, se_car.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_car.state_export(self, _if)
        _if.export_properties(se_car.__name__, self, se_car.properties_info)


#######################################################################
class se_anom_zone(base_entity):  # LA

    properties_info = (
        {"name": "af_spawn_id", "type": "u16", "default": 0},
        {"name": "af_spawn_time", "type": "complex_time", "default": 0},
    )

    @classmethod
    def init(cls, self):
        cse_alife_space_restrictor.init(self)
        entity.init_properties(self, se_anom_zone.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        self.flags |= entity.FL_LA
        cse_alife_space_restrictor.state_read(self, packet)
        if packet.resid() != 0:
            packet.unpack_properties(self, se_anom_zone.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_space_restrictor.state_write(self, packet, spawn_id, extended_size)
        packet.pack_properties(self, se_anom_zone.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_space_restrictor.state_import(self, _if, section, import_type)
        _if.import_properties(section, self, se_anom_zone.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_space_restrictor.state_export(self, _if)
        _if.export_properties(se_anom_zone.__name__, self, se_anom_zone.properties_info)


#######################################################################
class custom_storage(base_entity):  ##### OGSE #######

    # properties_info = (
    # 	{ "name": 'se_car__unk1_u8', "type": 'u8', "default": 0 },
    # 	{ "name": 'se_car__unk2_f32', "type": 'f32', "default": 1.0 },
    # 	{ "name": 'se_car__unk3_u16', "type": 'u16', "default": 0 },
    # );

    @classmethod
    def init(cls, self):
        cse_alife_dynamic_object.init(self)

    # 	entity.init_properties($_[0], custom_storage.properties_info)

    @classmethod
    def state_read(cls, self, packet: data_packet):
        cse_alife_dynamic_object.state_read(self, packet)

    # 	$_[1].unpack_properties($_[0], custom_storage.properties_info)

    @classmethod
    def state_write(cls, self, packet: data_packet, spawn_id: str, extended_size: int):
        cse_alife_dynamic_object.state_write(self, packet, spawn_id, extended_size)

    # 	$_[1].pack_properties($_[0], custom_storage.properties_info)

    @classmethod
    def state_import(cls, self, _if: ini_file, section: str, import_type):
        cse_alife_dynamic_object.state_import(self, _if, section, import_type)

    # 	$_[1].import_properties($_[2], $_[0], custom_storage.properties_info)

    @classmethod
    def state_export(cls, self, _if: ini_file):
        cse_alife_dynamic_object.state_export(self, _if)


# 	$_[1].export_properties(self.__class__.__name__, $_[0], custom_storage.properties_info)

#######################################################################
