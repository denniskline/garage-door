import os
import datetime
import time
import logging
import dropbox

class Dropbox:

    def __init__(self, accessToken):
        self.accessToken = accessToken
        pass

    def upload(self, fileNames):
        if type(fileNames) is not list: fileNames = [ fileNames ]
        for fileName in fileNames:
            logging.info("Uploading file: {}".format(fileName))
            mode = dropbox.files.WriteMode.overwrite
            mtime = os.path.getmtime(fileName)

            dropBoxFileName = ('/photo/' + 
                          os.path.basename(os.path.dirname(fileName)) + '/' + 
                          os.path.basename(fileName))

            with open(fileName, 'rb') as f:
                data = f.read()

            try:
                dbx = dropbox.Dropbox(self.accessToken)
                response = dbx.files_upload(data, dropBoxFileName, mode,
                        client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
                        mute=True)
            except dropbox.exceptions.ApiError as err:
                raise err

