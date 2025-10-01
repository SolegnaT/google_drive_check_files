from googleapiclient.discovery import build
import  os

def get_folder_id_from_path(service, path):
    """
    Resolve a folder path like "Parent/Child/SubChild" into a folder ID.
    """
    folder_id = "root"
    for name in path.strip("/").split("/"):
        response = service.files().list(
            q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and name='{name}' and trashed=false",
            spaces='drive',
            fields="files(id, name)"
        ).execute()
        folders = response.get('files', [])
        if not folders:
            raise FileNotFoundError(f"Folder '{name}' not found in '{folder_id}'")
        folder_id = folders[0]['id']  # take the first match
    return folder_id


def get_folders():
    folders = dict()
    try:

        with build('drive', 'v3') as service:
            files = []
            page_token = None
            while True:
              response = (
                  service.files()
                  .list(
                     q="mimeType = 'application/vnd.google-apps.folder'",
                      spaces="drive",
                      fields="nextPageToken, files(id, name)",
                      pageToken=page_token,
                  )
                  .execute()
              )
              for file in response.get("files", []):
                # Process change
                #if folders.get(file.get("name")) is not None: # TODO: HANDLE COPIES OF FOLDERNAMES
                #    raise Exception("Folder name already exists!")
                folders[file.get("name")] = file.get("id")
              page_token = response.get("nextPageToken", None)
              if page_token is None:
                break
        print('DONE')
    except HttpError as error:
        print(f"An error occurred: {error}")
        folder = None
    return folders

def list_files(path):
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow

        flow = InstalledAppFlow.from_client_config(
            {
              "installed": {
                "client_id": "459965082135-n4ifbs3d0gkf87qi25urhfgbqfhqra1m.apps.googleusercontent.com",
                "client_secret":"",
                "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token"
              }
            },
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
        credentials = flow.run_local_server(port=0)
        #flow.fetch_token()
        #credentials = flow.credentials()#
        with build('drive', 'v3',credentials = credentials) as service:
            folder_id = get_folder_id_from_path(service, path)
            files = []
            page_token = None
            while True:
              response = (
                  service.files()
                  .list(
                      q= f"'{folder_id}' in parents",
                      spaces="drive",
                      fields="nextPageToken, files(id, name, size)",
                      pageToken=page_token,
                  )
                  .execute()
              )
              for file in response.get("files", []):
                # Process change
                #print(f'Found file: {file.get("name")}, {file.get("id")}, {file.get("size")}')
                files.append((file.get("name"),file.get("size")))
              page_token = response.get("nextPageToken", None)
              if page_token is None:
                break
        print('DONE')

    except HttpError as error:
        print(f"An error occurred: {error}")
        files = None

    return files


if __name__ == '__main__':
    google_drive_path = "Photos/2019/angelos mobil"
    files = list_files(google_drive_path)
    #disk_path = os.path.join("D:/", google_drive_path)
    disk_path = r"D:\FOTO\bilder från angelos mobil 2april2022\2019"
    n_matched = 0
    n_missing = 0
    n_extra = 0
    files_local = os.listdir(disk_path)
    for fn,sz in files:
        matched = False
        for fn_local in files_local:
            if (fn == fn_local) and int(sz) == os.path.getsize(os.path.join(disk_path,fn_local)):
                matched = True
                break
        if matched:
            n_matched += 1
        else:
            n_missing += 1

    for fn_local in files_local:
        is_extra = 1;
        for fn,sz in files:
            if  (fn == fn_local) and int(sz) == os.path.getsize(os.path.join(disk_path,fn_local)):
                is_extra = 0
        if is_extra == 1:
            print(f"EXTRA: {fn_local}")

    print(f"RESULT: {n_matched} matches, {n_missing} missing, and {len(files_local)-n_matched} extra out of {len(files)} files.")

