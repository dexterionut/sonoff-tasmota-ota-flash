import hashlib
import requests

SONOFF_IP_ADDRESS = '192.168.168.134'
TASMOTA_FILE_URL = 'http://192.168.168.12:8000/files/tasmota-lite.bin'


def _get_in(source_dict, get_list, default=None):
    value = source_dict
    try:
        for get_param in get_list:
            value = value[get_param]
        return value
    except Exception:
        return default


def _get_sha_256_sum(url):
    sha256_hash = hashlib.sha256()

    r = requests.get(url)

    for data in r.iter_content(8192):
        sha256_hash.update(data)

    return sha256_hash.hexdigest()


def get_device_info_request():
    url = 'http://{}:8081/zeroconf/info'.format(SONOFF_IP_ADDRESS)

    headers = {
        'Content-Type': 'application/json'
    }
    json = {
        'deviceid': '',
        'data': {}
    }
    r = requests.post(url, json=json, headers=headers)

    return r.json()


def enable_diy_mode_request():
    url = 'http://{}:8081/zeroconf/ota_unlock'.format(SONOFF_IP_ADDRESS)

    headers = {
        'Content-Type': 'application/json'
    }
    json = {
        'deviceid': '',
        'data': {}
    }
    r = requests.post(url, json=json, headers=headers)

    return r.json()


def flash_firmware_request():
    url = 'http://{}:8081/zeroconf/ota_flash'.format(SONOFF_IP_ADDRESS)

    headers = {
        'Content-Type': 'application/json'
    }
    json = {
        'deviceid': '',
        'data': {
            'downloadUrl': TASMOTA_FILE_URL,
            'sha256sum': _get_sha_256_sum(TASMOTA_FILE_URL)
        }
    }
    r = requests.post(url, json=json, headers=headers)

    return r.json()


def is_diy_enabled():
    device_info = get_device_info_request()

    return _get_in(device_info, ['data', 'otaUnlock'])


def main():
    if not is_diy_enabled():
        print('[INFO] Executing enable_diy_mode_request...')
        r_json = enable_diy_mode_request()
        print('[INFO] Result: {}\n\n'.format(r_json))

    if is_diy_enabled():
        print('[INFO] Executing flash_firmware_request...')
        r_json = flash_firmware_request()
        print('[INFO] Result: {}\n\n'.format(r_json))
    else:
        print('[ERROR] DIY mode is not enabled. Firmware was not flashed.')


if __name__ == '__main__':
    main()
