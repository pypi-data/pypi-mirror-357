import functools
import re
from pathlib import Path

from r00docker import DockerClient
from r00logger import log
from richi import print_vs_text, print_nice
from system import run
from system import set_file_metadata, get_file_metadata


def log_pp(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print_nice(f"START PATCH PROPS [{func.__name__}]")
        result = func(*args, **kwargs)
        return result

    return wrapper


class PropsPatch:
    def __init__(self, data_prop: dict):
        self.data_prop = data_prop

    @log_pp
    def update_ramdisk_host(self, aik_dir):
        otn_paths = [
            'ramdisk/default.prop',
            'ramdisk/default.prop.bak',
        ]
        filepaths = [Path(aik_dir) / item for item in otn_paths]
        self._generate_props(self.data_prop, filepaths)
        print_nice('Patched: Ramdisk default.prop in host -> OK')

    @log_pp
    def update_ramdisk_container(self, docker: DockerClient, container_name: str):
        aik_dir = '/root/aik'
        otn_paths = [
            'ramdisk/default.prop',
            'ramdisk/default.prop.bak',
        ]
        remote_filepaths = [Path(aik_dir) / item for item in otn_paths]
        local_filepaths = [Path('/tmp') / item.name for item in remote_filepaths]
        filepaths = list(zip(remote_filepaths, local_filepaths))
        for remote_filepath, local_filepath in filepaths:
            docker.copy_from_container(container_name, remote_filepath, local_filepath)

        self._generate_props(self.data_prop, local_filepaths)

        for remote_filepath, local_filepath in filepaths:
            docker.copy_to_container(container_name, local_filepath, remote_filepath)
        print_nice('Patched: Ramdisk default.prop in container -> OK')

    @log_pp
    def update_system(self):
        target_filepaths = []
        for allow_prop in devconf.allow_system_props:
            if allow_prop == 'system':
                filepath = devconf.dir_custom / 'system/build.prop'
                target_filepaths.append(filepath)

            elif allow_prop == 'vendor':
                filepath = devconf.dir_custom / 'system/vendor/build.prop'
                target_filepaths.append(filepath)

            elif allow_prop == 'horione':
                filepath = devconf.dir_custom / 'HoriOne/Devices/S8/build.prop'
                target_filepaths.append(filepath)

        self._generate_props(devconf.data_prop, target_filepaths)
        print_nice('Patched: System *.prop in host -> OK')

    @staticmethod
    def _write_props_file(file_path: Path, master_props: dict):
        if not file_path.is_file():
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Файл не найден, пропуск.")
            return
        try:
            metadata_file = get_file_metadata(file_path)
            run(f'sudo chmod 777 {file_path}')

            original_lines = file_path.read_text(encoding='utf-8').splitlines()
            new_lines = []
            updated_keys = set()
            for line in original_lines:
                stripped_line = line.strip()
                if not stripped_line or stripped_line.startswith('#'): new_lines.append(line); continue
                match = re.match(r'([^=]+?)\s*=\s*(.*)', stripped_line)
                if match:
                    key = match.group(1).strip()
                    value_current = match.group(2).strip()
                    value_need = str(master_props.get(key))
                    if value_need and key in master_props and value_current != value_need:
                        new_lines.append(f"{key}={value_need}")
                        print_vs_text(value_current, value_need, title=key)
                        updated_keys.add(key)
                    else: new_lines.append(line)
                else: new_lines.append(line)

            if updated_keys:
                file_path.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
                log.debug(f"Модифицированный файл сохранён: {file_path}")
            else:
                log.debug(f"В файле {file_path} не найдено ключей для обновления.")
            set_file_metadata(file_path, metadata_file)

        except Exception as e:
            log.exception(f"[ОШИБКА] Не удалось обработать файл {file_path}: {e}")

    def _generate_props(self, fake_params: dict, target_files: list):
        master_props = {}
        aliases = {
            "alarm_alert": [
                "ro.config.alarm_alert"
            ],
            "baseband": [
                "gsm.version.baseband"
            ],
            "board": [
                "ro.product.board"
            ],
            "brand": [
                "ro.product.brand",
                "ro.product.manufacturer",
                "ro.product.vendor.brand",
                "ro.product.vendor.manufacturer"
            ],
            "changelist": [
                "ro.build.changelist"
            ],
            "characteristics": [
                "ro.build.characteristics",
                "ro.vendor.build.characteristics"
            ],
            "chipname": [
                "ro.hardware.chipname"
            ],
            "country_code": [
                "ro.csc.country_code"
            ],
            "country_iso": [
                "ro.csc.countryiso_code"
            ],
            "cpu_abi": [
                "ro.product.cpu.abi"
            ],
            "cpu_abilist": [
                "ro.product.cpu.abilist",
                "ro.vendor.product.cpu.abilist"
            ],
            "cpu_abilist32": [
                "ro.product.cpu.abilist32",
                "ro.vendor.product.cpu.abilist32"
            ],
            "cpu_abilist64": [
                "ro.product.cpu.abilist64",
                "ro.vendor.product.cpu.abilist64"
            ],
            "date": [
                "ro.build.date",
                "ro.bootimage.build.date",
                "ro.vendor.build.date"
            ],
            "date_utc": [
                "ro.build.date.utc",
                "ro.bootimage.build.date.utc",
                "ro.vendor.build.date.utc"
            ],
            "device": [
                "ro.product.device",
                "ro.product.vendor.device",
                "ro.build.product"
            ],
            "first_api_level": [
                "ro.product.first_api_level"
            ],
            "hardware": [
                "ro.hardware",
                "ro.boot.hardware"
            ],
            "host": [
                "ro.build.host"
            ],
            "id": [
                "ro.build.id"
            ],
            "incremental": [
                "ro.build.version.incremental",
                "ro.build.PDA",
                "ro.bootloader"
            ],
            "locale": [
                "ro.product.locale"
            ],
            "media_sound": [
                "ro.config.media_sound"
            ],
            "model": [
                "ro.product.model",
                "ro.product.vendor.model"
            ],
            "name": [
                "ro.product.name",
                "ro.product.vendor.name"
            ],
            "notification_sound": [
                "ro.config.notification_sound"
            ],
            "notification_sound_2": [
                "ro.config.notification_sound_2"
            ],
            "official_cscver": [
                "ril.official_cscver"
            ],
            "omcnw_code": [
                "ro.csc.omcnw_code"
            ],
            "product_code": [
                "ril.product_code",
                "vendor.ril.product_code"
            ],
            "product_ship": [
                "ro.product_ship",
                "ro.vendor.product_ship"
            ],
            "release": [
                "ro.build.version.release"
            ],
            "ringtone": [
                "ro.config.ringtone"
            ],
            "ringtone_2": [
                "ro.config.ringtone_2"
            ],
            "sales_code": [
                "ro.csc.sales_code",
                "ro.oem.key1"
            ],
            "sdk": [
                "ro.build.version.sdk",
                "ro.vndk.version"
            ],
            "security_patch": [
                "ro.build.version.security_patch",
                "ro.vendor.build.security_patch"
            ],
            "serialno": [
                "ro.serialno"
            ],
            "tags": [
                "ro.build.tags"
            ],
            "timezone": [
                "persist.sys.timezone"
            ],
            "treble_enabled": [
                "ro.treble.enabled"
            ],
            "type": [
                "ro.build.type"
            ],
            "user": [
                "ro.build.user"
            ]
        }
        for param_key, prop_keys in aliases.items():
            if param_key in fake_params:
                for prop_key in prop_keys:
                    master_props[prop_key] = str(fake_params[param_key])

        for key, value in fake_params.items():
            if (key.startswith('ro.') or key.startswith('pm.')) and key not in master_props:
                master_props[key] = str(value)
        try:
            master_props['ro.build.flavor'] = f"{master_props['ro.product.name']}-{master_props['ro.build.type']}"
            master_props[
                'ro.build.description'] = f"{master_props['ro.build.flavor']} {master_props['ro.build.version.release']} {master_props['ro.build.id']} {master_props['ro.build.version.incremental']} {master_props['ro.build.tags']}"
            master_props[
                'ro.build.display.id'] = f"{master_props['ro.build.id']}.{master_props['ro.build.version.incremental']}"
            fp = f"{master_props['ro.product.brand']}/{master_props['ro.product.name']}/{master_props['ro.product.device']}:{master_props['ro.build.version.release']}/{master_props['ro.build.id']}/{master_props['ro.build.version.incremental']}:{master_props['ro.build.type']}/{master_props['ro.build.tags']}"
            master_props['ro.build.fingerprint'] = fp
            master_props['ro.vendor.build.fingerprint'] = fp
            master_props[
                'ro.build.version.base_os'] = 'samsung/greatltexx/greatlte:9/PPR1.180610.011/N950FXXUDDTH1:user/release-keys'
            bootimage_fp_tags = fake_params.get('bootimage_tags', master_props['ro.build.tags'])
            master_props['ro.bootimage.build.fingerprint'] = fp.replace(master_props['ro.build.tags'],
                                                                        bootimage_fp_tags)
        except KeyError as e:
            print(f"[КРИТИЧЕСКАЯ ОШИБКА] Недостаточно параметров: {e}")
            return

        if not target_files: return
        target_paths = [Path(f) for f in target_files]
        for file_path in target_paths:
            self._write_props_file(file_path, master_props)
