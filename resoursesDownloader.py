import sys
from pathlib import Path

import requests


# https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url
def download_file_from_google_drive(file_id, destination):
    URL = "https://docs.google.com/uc?export=download&confirm=1"

    if Path(destination).is_file():
        print(f"{destination} already exists")
        return None
    else:
        print(f"{destination} downloading")

    session = requests.Session()

    response = session.get(URL, params={"id": file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value

    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


# def main():
#     if len(sys.argv) >= 3:
#         file_id = sys.argv[1]
#         destination = sys.argv[2]
#     else:
#         file_id = "TAKE_ID_FROM_SHAREABLE_LINK"
#         destination = "DESTINATION_FILE_ON_YOUR_DISK"
#     print(f"download {file_id} to {destination}")
#     download_file_from_google_drive(file_id, destination)

if __name__ == "__main__":
    # https://drive.google.com/file/d/16-LqEkArtWMRLbRa5HfKXZk3xVBWUzCO/view?usp=sharing
    download_file_from_google_drive('16-LqEkArtWMRLbRa5HfKXZk3xVBWUzCO', 'NoOperation.mp4')

    # https://drive.google.com/file/d/1tiWLeiAmXx3BU6qNzYcBY_JWN5qjRRfm/view?usp=sharing
    download_file_from_google_drive('1tiWLeiAmXx3BU6qNzYcBY_JWN5qjRRfm', 'Container_01_MoveToTable.mp4')

    # https://drive.google.com/file/d/1OaTmVB28XK1xXW_XtVWOzi5BvBPvNCUa/view?usp=sharing
    download_file_from_google_drive('1OaTmVB28XK1xXW_XtVWOzi5BvBPvNCUa', 'Container_01_MoveToRack.mp4')

    # https://drive.google.com/file/d/1lyajhzb3xDVpb9zJXhUDdvJOF2pIHkXT/view?usp=sharing
    download_file_from_google_drive('1lyajhzb3xDVpb9zJXhUDdvJOF2pIHkXT', 'Container_02_MoveToTable.mp4')

    # https://drive.google.com/file/d/198SC97NfiD-u8B5CZ_C5rkW2jFdGc4Lb/view?usp=sharing
    download_file_from_google_drive('198SC97NfiD-u8B5CZ_C5rkW2jFdGc4Lb', 'Container_02_MoveToRack.mp4')

    # https://drive.google.com/file/d/1MG_8A8f7mrr7PNpOipmp8v3P_OXkSMZk/view?usp=sharing
    download_file_from_google_drive('1MG_8A8f7mrr7PNpOipmp8v3P_OXkSMZk', 'Container_03_MoveToTable.mp4')

    # https://drive.google.com/file/d/1RrLw93ydqrdswG9wybT18MMsKyn2gWGM/view?usp=sharing
    download_file_from_google_drive('1RrLw93ydqrdswG9wybT18MMsKyn2gWGM', 'Container_03_MoveToRack.mp4')

    # https://drive.google.com/file/d/1mUK0WxfI96tMvp9mDu3LFnLfNlydTzjT/view?usp=sharing
    download_file_from_google_drive('1mUK0WxfI96tMvp9mDu3LFnLfNlydTzjT', 'Container_04_MoveToTable.mp4')

    # https://drive.google.com/file/d/1zQDD1VeI0f4vC58ibpbFkhU2CdKTpsRH/view?usp=sharing
    download_file_from_google_drive('1zQDD1VeI0f4vC58ibpbFkhU2CdKTpsRH', 'Container_04_MoveToRack.mp4')

    # https://drive.google.com/file/d/1zvUOqIMCDCeVERkU_XcvDbTWcI-KXbtz/view?usp=sharing
    download_file_from_google_drive('1zvUOqIMCDCeVERkU_XcvDbTWcI-KXbtz', 'Container_05_MoveToTable.mp4')

    # https://drive.google.com/file/d/1arHi_0QeNRh1JjWlmap8jiAUqcwkpsBZ/view?usp=sharing
    download_file_from_google_drive('1arHi_0QeNRh1JjWlmap8jiAUqcwkpsBZ', 'Container_05_MoveToRack.mp4')

    # https://drive.google.com/file/d/1pdvgjId3hPzGwv17MoHSpiZRGSYeuKfi/view?usp=sharing
    download_file_from_google_drive('1pdvgjId3hPzGwv17MoHSpiZRGSYeuKfi', 'Container_06_MoveToTable.mp4')

    # https://drive.google.com/file/d/1fxyANflvIWyoG3qNLu1atfEYQcqkPMs2/view?usp=sharing
    download_file_from_google_drive('1fxyANflvIWyoG3qNLu1atfEYQcqkPMs2', 'Container_06_MoveToRack.mp4')

    # https://drive.google.com/file/d/1R5SlmLvA3Z6YRqb-FnwSWNtHLvfwnPtR/view?usp=sharing
    download_file_from_google_drive('1R5SlmLvA3Z6YRqb-FnwSWNtHLvfwnPtR', 'Container_07_MoveToTable.mp4')

    # https://drive.google.com/file/d/1CGX8pO0J3VDDZqVSKpUBhOgy94U9LXDV/view?usp=sharing
    download_file_from_google_drive('1CGX8pO0J3VDDZqVSKpUBhOgy94U9LXDV', 'Container_07_MoveToRack.mp4')

    # https://drive.google.com/file/d/17NDsxSysw1RlFNYdcI_PPad4kRX1lyZU/view?usp=sharing
    download_file_from_google_drive('17NDsxSysw1RlFNYdcI_PPad4kRX1lyZU', 'Container_08_MoveToTable.mp4')

    # https://drive.google.com/file/d/1YsA5FI0CjSRGaVrV9zHFcjQ74-EKBv5q/view?usp=sharing
    download_file_from_google_drive('1YsA5FI0CjSRGaVrV9zHFcjQ74-EKBv5q', 'Container_08_MoveToRack.mp4')

    # https://drive.google.com/file/d/1gibZ8kLFeXvi1OrZUcGU-ZfeuDo_ICSY/view?usp=sharing
    download_file_from_google_drive('1gibZ8kLFeXvi1OrZUcGU-ZfeuDo_ICSY', 'Container_09_MoveToTable.mp4')

    # https://drive.google.com/file/d/1s0KLIq10KTpZVp3dWtIoSF2Vfvd_cdmb/view?usp=sharing
    download_file_from_google_drive('1s0KLIq10KTpZVp3dWtIoSF2Vfvd_cdmb', 'Container_09_MoveToRack.mp4')

    # https://drive.google.com/file/d/1XtAZF7Oo9cqxneX3Z3y6SXDW-OFfDRUr/view?usp=sharing
    download_file_from_google_drive('1XtAZF7Oo9cqxneX3Z3y6SXDW-OFfDRUr', 'Container_10_MoveToTable.mp4')

    # https://drive.google.com/file/d/1wlJGpgD6OK23jkLhoy-1qoYph8GGBiox/view?usp=sharing
    download_file_from_google_drive('1wlJGpgD6OK23jkLhoy-1qoYph8GGBiox', 'Container_10_MoveToRack.mp4')
