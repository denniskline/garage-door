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

        uploadThreads = []
        for fileName in fileNames:
            uploadThreads.append(threading.Thread(target=self.__upload, args=(fileName,)))

        # Start all the threads
        for uploadThread in uploadThreads:
            uploadThread.start()

        # Wait for all the threads to complete
        #for uploadThread in uploadThreads:
        #    uploadThread.join()

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

    def __upload(self, fileName):
        logging.info("Uploading file: {}".format(fileName))
        mode = dropbox.files.WriteMode.overwrite
        mtime = os.path.getmtime(fileName)
        fileStamp = datetime.datetime(*time.gmtime(mtime)[:6])

        dropBoxFileName = (datetime.datetime.now().strftime("/photo/%Y/%B/%d-%A/") + os.path.basename(fileName))

        with open(fileName, 'rb') as f:
            data = f.read()

        dbx = dropbox.Dropbox(self.accessToken)
        logging.info("Uploading file {} to dropbox: {}".format(fileName, dropBoxFileName))
        response = dbx.files_upload(data, dropBoxFileName, mode, client_modified=fileStamp, mute=True)
        logging.debug("Response from dropbox: {}".format(response))
       
        return response

