class MovieChanger(object):
    def __init__(self, *movies):
        self.movies = movies
        pass

    def setActive(self):
        self.__disable_rest(self.movies[1])

    def setIdle(self):
        self.__disable_rest(self.movies[0])
        pass

    def setUse(self):
        self.__disable_rest(self.movies[2])
        pass

    def getUseMovie(self):
        return self.movies[2]
        pass

    def __disable_rest(self, moviePass):
        for movie in self.movies:
            if movie is moviePass:
                movie.setEnable(True)
                movie.setPlay(True)
                continue
                pass
            movie.setEnable(False)
            movie.setPlay(False)
            pass
        pass
