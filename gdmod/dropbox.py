import os
import datetime
import time
import logging
import dropbox
import math

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

    def diagnostics(self):
        dbx = dropbox.Dropbox(self.accessToken)
        usage = dbx.users_get_space_usage() 

        diag = {}
        diag['Used'] = self.convertSize(usage.used)
        diag['Allocated'] = self.convertSize(usage.allocation.get_individual().allocated)
        diag['Remaining'] = self.convertSize(usage.allocation.get_individual().allocated - usage.used)

        return diag

    def convertSize(self, size):
        if (size == 0):
            return '0B'
        size = size/1024
        size_name = ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size,1024)))
        p = math.pow(1024,i)
        s = round(size/p,2)
        return '%s %s' % (s,size_name[i])
