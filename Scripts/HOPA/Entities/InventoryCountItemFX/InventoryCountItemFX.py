from Foundation.DefaultManager import DefaultManager
from HOPA.Entities.InventoryItem.InventoryItem import InventoryItem
from HOPA.ItemManager import ItemManager
from HOPA.PopUpItemManager import PopUpItemManager


class SubMovie(object):
    def __init__(self, movie):
        self.movie = movie
        self.on_end = Event("MovieEnd")
        self.play_id = 0

        self.movie.setEventListener(onAnimatableEnd=self._on_animatable_end)
        self.movie.setLoop(False)

    def play(self):
        self.play_id = self.movie.play()

        if self.play_id == 0:
            self.end()

    def end(self):
        if self.play_id == 0:
            return

        self.play_id = 0
        self.on_end()

    def setLastFrame(self):
        self.movie.setLastFrame()

    def setFirstFrame(self):
        self.movie.setFirstFrame()

    def valid_play_id(self, id):
        return self.play_id == id

    def _on_animatable_end(self, id):
        if not self.valid_play_id(id):
            return

        self.end()


class InventoryCountItemFX(InventoryItem):
    @staticmethod
    def declareORM(Type):
        InventoryItem.declareORM(Type)

        Type.addAction(Type, "FontName")

        Type.addAction(Type, "ResourceMovieParts")
        Type.addAction(Type, "ResourceMovieCombine")
        Type.addAction(Type, "ResourceMovieFull")

        Type.addAction(Type, "ItemMovies")

        Type.addAction(Type, "PlayedItems")
        Type.addAction(Type, "Combined")
        pass

    def __init__(self):
        super(InventoryCountItemFX, self).__init__()

        self.current_movie = None

        self.movies = {}

        self.textField = None

        self.submovies = {}

    def getSprite(self):
        return self.current_movie

    def _getItemCenter(self):  # overrided
        # default value (local top left point of movie)
        center = self.current_movie.getLocalPosition()

        slot = self.current_movie.getMovieSlot("center")
        if slot is None:
            return center

        # if movie contain 'center' MovieSlot
        center = slot.getLocalPosition()
        return center

    def _updateCount(self):  # overrided
        self._updateLayers()
        self._updateTextField()

    def checkCount(self):
        progress, total = self._getProgressTotal()

        if progress == total:
            return True

        return False

    def _onActivate(self):
        self._updateMovies()

    def _onInitialize(self, obj):
        super(InventoryCountItemFX, self)._onInitialize(obj)

        self._createMovies()

        self._initSubMovies()

        self._updateMovies()

        self._createTextField()

    def _onFinalize(self):
        super(InventoryCountItemFX, self)._onFinalize()

        self._destroyMovies()
        self._destroyTextField()

    # - admin logic ----------------------------------------------
    def _createResourceMovie(self, MovieName, MovieResourceName, Enable=True, Loop=False, AutoPlay=False):
        if MovieResourceName is None:
            return None

        movie = self.createChild("Movie")
        movie.setName(MovieName)
        movie.setResourceMovie(MovieResourceName)

        if Enable is True:
            movie.enable()

        if Loop is True:
            movie.setLoop(True)

        if AutoPlay is True:
            movie.setAutoPlay(True)

        self.addChild(movie)
        return movie

    def _createMovies(self):
        if self.ResourceMovieParts is None:
            return

        name = self.getName()

        self.movies["Parts"] = self._createResourceMovie("{}_Parts".format(name), self.ResourceMovieParts)
        self.movies["Combine"] = self._createResourceMovie("{}_Combine".format(name), self.ResourceMovieCombine, Enable=False)
        self.movies["Full"] = self._createResourceMovie("{}_Full".format(name), self.ResourceMovieFull, Enable=False, Loop=True, AutoPlay=True)

        self.current_movie = self.movies.get("Parts")

    def _destroyMovies(self):
        self.current_movie = None

        for movie in self.movies.itervalues():
            if movie is None:
                continue
            Mengine.destroyNode(movie)

        self.movies = {}

    def _initSubMovies(self):
        if self.current_movie is None:
            return

        for item_layer in self.ItemMovies:
            if not self.current_movie.hasSubMovie(item_layer):
                continue

            submovie = self.current_movie.getSubMovie(item_layer)

            self.submovies[item_layer] = SubMovie(submovie)

    def _updateMovies(self):
        if self.Combined is True:
            if self.movies.get("Full") is not None:
                self._change_current_movie("Full")
            elif self.movies.get("Combine") is not None:
                self._change_current_movie("Combine")
                self.movies.get("Combine").setLastFrame()
            else:
                for found_item in self.FoundItems:
                    Item = ItemManager.getItem(found_item)

                    item_layer = Item.PartSubMovieName

                    submovie = self.submovies.get(item_layer)

                    if item_layer in self.PlayedItems:
                        submovie.setLastFrame()

    def _createTextField(self):
        self.textField = Mengine.createNode("TextField")

        # if self.FontName is not None:
        #     self.textField.setFontName(self.FontName)
        #
        # self.textField.setTextID("ID_InventoryCountItem")
        # self.textField.setFontColor((1, 0, 0, 1))  # red
        # self.textField.enable()

        DefaultTextID = DefaultManager.getDefault('DefaultInventoryCountItemTextID', None)
        if DefaultTextID is not None:
            self.textField.setTextId(DefaultTextID)
        else:
            if self.FontName is not None:
                self.textField.setFontName(self.FontName)
                pass

            self.textField.setTextId("ID_InventoryCountItem")
            self.textField.setFontColor((1, 1, 1, 1))
            pass

        self.textField.enable()

        self.addChild(self.textField)

    def _destroyTextField(self):
        if self.textField is None:
            return

        Mengine.destroyNode(self.textField)
        self.textField = None

    def playSubMovie(self, ItemName):
        if ItemName not in self.FoundItems:
            return

        Item = ItemManager.getItem(ItemName)

        submovie = self.submovies.get(Item.PartSubMovieName)

        submovie.on_end += Functor(self._onMoviePartPlayEnd, Item.PartSubMovieName)
        submovie.play()

    def _onMoviePartPlayEnd(self, MovieName):
        self.object.appendParam("PlayedItems", MovieName)

        self._updateCount()

    def getSubMovie(self, ItemName):
        if ItemName not in self.FoundItems:
            return None

        Item = ItemManager.getItem(ItemName)

        submovie = self.submovies.get(Item.PartSubMovieName)
        return submovie

    def _play_movie(self, movie, cb):
        if movie is None:
            return

        if callable(cb) is False:
            return

        play_id = movie.play()

        def _cb(id):
            if id != play_id:
                return

            cb()

        movie.setEventListener(onAnimatableEnd=_cb)

    def _change_current_movie(self, MovieName):
        if MovieName not in self.movies:
            return

        Movie = self.movies.get(MovieName)

        if Movie is None:
            return

        self.current_movie.disable()
        self.current_movie = Movie
        self.current_movie.enable()

    def _updateLayers(self):
        if self.current_movie is None:
            return

        if self.Combined is True:
            return

        if self.isProgressFull() and self.isPlayedAllParts():
            if self.movies.get("Combine") is not None:
                self._change_current_movie("Combine")

                self._play_movie(self.current_movie, Functor(self._change_current_movie, "Full"))
            else:
                self._change_current_movie("Full")

            self.object.setParam("Combined", True)

        for found_item in self.FoundItems:
            Item = ItemManager.getItem(found_item)

            item_layer = Item.PartSubMovieName

            submovie = self.submovies.get(item_layer)

            if item_layer in self.PlayedItems:
                submovie.setLastFrame()

    def isProgressFull(self):
        progress, total = self._getProgressTotal()
        return progress == total

    def _getProgressTotal(self):
        FindItems = ItemManager.getInventoryItemFindItems(self.object)

        # FindItems may be empty in case of CountItem using for ItemPopUp
        if not FindItems:
            FindItems = PopUpItemManager.getInventoryItemFindItems(self.object)

        total = 0
        for find_item in FindItems:
            Item = ItemManager.getItem(find_item)

            count = Item.ItemPartsCount
            if count is None:
                total += 1
                continue

            total += count

        progress = 0
        for found_item in self.FoundItems:
            Item = ItemManager.getItem(found_item)

            count = Item.ItemPartsCount
            if count is None:
                progress += 1
                continue

            progress += count

        return progress, total

    def isPlayedAllParts(self):
        FindItems = ItemManager.getInventoryItemFindItems(self.object)

        for find_item in FindItems:
            Item = ItemManager.getItem(find_item)

            MovieName = Item.PartSubMovieName

            if MovieName not in self.PlayedItems:
                return False

        return True

    def _updateTextField(self):
        if self.textField is None:
            return

        self.textField.enable()

        CountItemDisableTextWhenFull = DefaultManager.getDefaultBool("CountItemDisableTextWhenFull", False)
        if CountItemDisableTextWhenFull and self.isProgressFull() and self.isPlayedAllParts():
            self.textField.disable()

        progress, total = self._getProgressTotal()
        self.textField.setTextFormatArgs(progress, total)
