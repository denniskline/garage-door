import os
import datetime
import time
import logging
import dropbox
import math
import threading

class Dropbox:

    def __init__(self, accessToken):
        self.accessToken = accessToken
        pass

    def upload(self, fileNames):
        if type(fileNames) is not list: fileNames = [ fileNames ]
        dbx = dropbox.Dropbox(self.accessToken)

        uploadThreads = []
        for fileName in fileNames:
            uploadThreads.append(UploadThread(dbx, fileName))
 
        # Start all the threads
        for uploadThread in uploadThreads:
            uploadThread.start()

        # Wait for all the threads to complete
        for uploadThread in uploadThreads:
            uploadThread.join()

    def diagnostics(self):
        dbx = dropbox.Dropbox(self.accessToken)
        usage = dbx.users_get_space_usage() 

        diag = {}
        diag['Used'] = self.__convertSize(usage.used)
        diag['Allocated'] = self.__convertSize(usage.allocation.get_individual().allocated)
        diag['Remaining'] = self.__convertSize(usage.allocation.get_individual().allocated - usage.used)

        return diag

    def __convertSize(self, size):
        if (size == 0):
            return '0B'
        size = size/1024
        size_name = ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size,1024)))
        p = math.pow(1024,i)
        s = round(size/p,2)
        return '%s %s' % (s,size_name[i])

class UploadThread (threading.Thread):

    def __init__(self, dbx, fileName):
        threading.Thread.__init__(self)
        self.dbx = dbx
        self.fileName = fileName

    def run(self):
        logging.info("Uploading file: {}".format(self.fileName))
        mode = dropbox.files.WriteMode.overwrite
        mtime = os.path.getmtime(self.fileName)
        fileStamp = datetime.datetime(*time.gmtime(mtime)[:6])

        dropBoxFileName = ('/photo/' + datetime.datetime.now().strftime("/photo/%Y/%B/%d-%A/") + os.path.basename(self.fileName))

        with open(self.fileName, 'rb') as f:
            data = f.read()

        return dbx.files_upload(data, dropBoxFileName, mode, client_modified=fileStamp, mute=True)

