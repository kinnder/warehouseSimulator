import sys
import requests


# https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url
def download_file_from_google_drive(file_id, destination):
    URL = "https://docs.google.com/uc?export=download&confirm=1"

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
