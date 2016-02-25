class ImageMatcher:
    """
    Class for using C++ library of image matching system
    """

    # create object by refference to C class obj
    # def by_ref(self, ref):
    #     self.lib.obj = ref

    def __init__(self, lib_path, db_path, logger):
        """
        lib_path - path to shared object c++ lib (*.so file), should be without closing "/"
        db_path - path to the working directory, where all data files will be stored
        """
        try:
            self.lib = ctypes.cdll.LoadLibrary(lib_path)

            self.obj = self.lib.init(db_path)

            # create template by img_url
            self.lib.addImage.argtypes = [
                ctypes.c_int,  # class ptr
                ctypes.c_int,  # img id
                ctypes.c_char_p  # img url
            ]
            self.lib.addImage.restype = ctypes.c_bool  # success

            # search by template id
            # class ptr, tempId to search by, max results, sim rate, size of result array
            self.lib.search.argtypes = [
                ctypes.c_int,  # class pointer
                ctypes.c_int,  # image id
                ctypes.c_int,  # max results
                ctypes.c_float,  # sim rate
                ctypes.POINTER(ImageStrength)  # array to write results
            ]
            self.lib.search.restype = ctypes.c_int  # result array of tempId's

            # safely exit c++ with saving all new templates
            self.lib.quit.argtypes = [ctypes.c_int]
            self.lib.quit.restype = ctypes.c_bool

        except Exception as e:
            self.logger.error("Cannot open shared library. Error: %s", e)            

    def add_image(self, img_id, url):
        res = self.lib.addImage(self.obj, img_id, url)
        return res

    def search(self, img_id, max_results, rate):
        """
        returns int size of found matches, -1 if id not found it db
        """
        results_type = (ImageStrength * max_results)
        self.lib.search.argtypes[-1] = ctypes.POINTER(ImageStrength)
        results = results_type()
        res_size = self.lib.search(self.obj, img_id, max_results, rate, results)
        self.logger.info("Search results: %s", res_size)
        if res_size < 1:
            return '[]'
        return results[:res_size]

    def exit(self):
        """
        safely exit shared lib, saving all new templates
        returns boolean, true if success
        """
        return self.lib.quit(self.obj)