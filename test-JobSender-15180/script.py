import os
import zipfile
import requests

def _download_and_unpack(uri, archive_root, contents_root, is_workitem_payload=False):
    file_name = uri.split('/')[-1].split('?')[0]
    file_path = os.path.join(archive_root, file_name)
    if not os.path.exists(archive_root):
        os.makedirs(archive_root)
    if not os.path.exists(contents_root):
        os.makedirs(contents_root)
    print("Downloading {} to {}".format(_strip_uri(uri), file_path))
    partial_file_path = file_path + ".partial"
    
    if not os.path.exists(file_path):
        # In the case of a reboot, the .partial file will be in an indeterminate state.
        #_delete_if_exists(partial_file_path)
        _download_to(uri, partial_file_path)
        if os.path.exists(partial_file_path):
            _unpack(partial_file_path, contents_root, is_workitem_payload)  # failure here?
            os.rename(partial_file_path, file_path)
            return True
        else:
            print("File '{name}' failed to download!".format(name=partial_file_path))
    else:
        print("File '{}' already exists, skipping".format(file_path))
        return False

def _download_to(uri, path):
    print("requesting {}".format(_strip_uri(uri)))
    response = requests.get(uri, stream=True)
    print("response received. Status: {} Elapsed time: {}".format(response.status_code, response.elapsed))
    size = str(response.headers.get('Content-Length', default='0'))
    print("Blob Size: {}".format(size))    
    with open(path, 'wb') as file_to_download:
        downloaded_size = 0
        for chunk in response.iter_content(chunk_size=1024):
            downloaded_size += 1024
            if chunk:
                file_to_download.write(chunk)
                file_to_download.flush()
        print("End of Download Loop")

def _unpack(file_path, contents_root, is_workitem_payload):
    _unpack_to(file_path, contents_root)

def _unpack_to(archive_path, out_dir):
    _unpack_zipfile(archive_path, out_dir)

def _unpack_zipfile(archive_path, out_dir):
    print("Unpacking {}".format(archive_path))
    with zipfile.ZipFile(archive_path) as zfile:
        for name in zfile.namelist():
            print("Found zip part {}".format(name.encode('ascii', 'replace')))
            zip_dir = ""
            zip_name = ""
            requires_create_dirs = False
            if "\\" in name:
                zip_filename = name.replace('\\', os.path.sep)
                requires_create_dirs = True
                (zip_dir, zip_name) = os.path.split(zip_filename)
            else:
                zip_filename = name
            print("Extracting to %s" % (os.path.join(out_dir, zip_dir)))
            out_file_dir = os.path.join(out_dir, zip_dir)
            if zip_filename == '':
                if not os.path.exists(out_file_dir) and requires_create_dirs:
                    os.makedirs(out_file_dir)
            else:
                if not os.path.exists(out_file_dir) and requires_create_dirs:
                    os.makedirs(out_file_dir)
                zfile.extract(name, out_file_dir)
                if requires_create_dirs:
                    os.rename(os.path.join(out_file_dir, name), os.path.join(out_file_dir, zip_name))
        zfile.close()

def _strip_uri(uri_to_strip):
    return str(uri_to_strip).split("?")[0]

os.environ['PYTHONIOENCODING'] = 'utf-8'

print('ENVIRONMENT:')
for key, value in os.environ.items():
    print('{}: {}'.format(key, value))

print('')
_download_and_unpack("https://helixde8s23ayyeko0k025g8.blob.core.windows.net/helix-job-33fed28d-e352-4636-b5c2-d2675d2142a4fb0f082979d45709c/XsltCompiler.Tests.zip", "archive_root", "content_root")