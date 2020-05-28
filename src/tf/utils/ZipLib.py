
import os
from zipfile import ZipFile


from tf.utils.SandBox import SandBox

logger = SandBox().get_logger()
ZIP_FILE = "test.zip"  # server assumes this


def valid_file(fn):

    blacklist = [".zip", ".pyc", "client.py"]
    for b in blacklist:
        if fn.endswith(b):
            return False
    return True


def create_zipfile(dir_or_file, output_dir='.'):

    zipfile = '{:s}/{:s}'.format(output_dir, ZIP_FILE)

    # need the abs path to the zip file
    zipfile = os.path.abspath(zipfile)

    old_dir = os.getcwd()
    try:
        # cli client.py assn1/
        if os.path.isdir(dir_or_file) and dir_or_file != '.':
            os.chdir(dir_or_file)
            dir_or_file = '.'

        # cli client.py assn1/solution.py
        parts = os.path.split(dir_or_file)
        if len(parts) == 2 and os.path.isfile(dir_or_file):
            if len(parts[0]) > 0:
                os.chdir(parts[0])
            dir_or_file = parts[1]

        #logger.log('create', zipfile, ' fp ', os.getcwd())
        with ZipFile(zipfile, 'w') as zipObj:
            # Iterate over all the files in directory
            if os.path.isdir(dir_or_file):
                for folderName, subfolders, filenames in os.walk(dir_or_file):
                    for filename in filenames:
                        if valid_file(filename):
                            # create complete filepath of file in directory
                            fq_path = os.path.join(folderName, filename)
                            # Add file to zip
                            logger.log("adding", fq_path)
                            zipObj.write(fq_path)
            else:
                logger.log("adding", dir_or_file)
                zipObj.write(dir_or_file)

            return zipfile
    finally:
        os.chdir(old_dir)

