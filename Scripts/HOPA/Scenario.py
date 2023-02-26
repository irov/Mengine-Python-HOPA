from Foundation.Initializer import Initializer
from Foundation.TaskManager import TaskManager
from Foundation.Task.TaskGenerator import TaskGeneratorException

from HOPA.Macro.MacroCommandFactory import MacroCommandFactory

class ScenarioElement(object):
    __slots__ = "Index", "CommandType", "Repeat"

    def __init__(self, Index, CommandType, Repeat):
        self.Index = Index
        self.CommandType = CommandType
        self.Repeat = Repeat

    def onGenerator(self, source, ScenarioRunner, ScenarioChapter, ScenarioCommands, ScenarioQuests):
        if self.Repeat is False:
            if ScenarioRunner.isMacroEnd(self.Index) is True:
                return

            source.addTask("TaskFunction", Fn=ScenarioRunner.runMacro, Args=(self.Index,))

        # source.addTask("TaskPrint", Value = "%s Macro run %s:%s"%(ScenarioRunner.getGroupName(), self.Index, self.CommandType ))

        sc_count = len(source.getSource())
        self._onGenerator(source, ScenarioRunner, ScenarioChapter, ScenarioCommands, ScenarioQuests)
        sc_count_after = len(source.getSource())

        if sc_count == sc_count_after:
            Trace.log("Macro", 0, "ScenarioElement.onGenerator %s:%d generator %s not add task!" % (ScenarioRunner.Name, self.Index, self.CommandType))

        if self.Repeat is False:
            source.addFunction(ScenarioRunner.endMacro, self.Index)  # source.addTask("TaskPrint", Value = "%s Macro end %s:%s"%(ScenarioRunner.getGroupName(), self.Index, self.CommandType ))

    def _onGenerator(self, source, ScenarioRunner, ScenarioChapter, ScenarioCommands, ScenarioQuests):
        return

class ScenarioMacroCommand(ScenarioElement):
    __slots__ = "Values"

    def __init__(self, Index, CommandType, Repeat, Values):
        super(ScenarioMacroCommand, self).__init__(Index, CommandType, Repeat)

        self.Values = Values

    def _onGenerator(self, source, ScenarioRunner, ScenarioChapter, ScenarioCommands, ScenarioQuests):
        super(ScenarioMacroCommand, self)._onGenerator(source, ScenarioRunner, ScenarioChapter, ScenarioCommands, ScenarioQuests)

        command = MacroCommandFactory.createCommand(self.CommandType)

        if command is None:
            Trace.log("Macro", 0, "ScenarioMacroCommand._onGenerator command not found %s:%d - %s" % (ScenarioRunner.Name, self.Index, self.CommandType))
            return False

        command.setIndex(self.Index)

        command.setScenarioRunner(ScenarioRunner)
        command.setScenarioChapter(ScenarioChapter)
        command.setScenarioCommands(ScenarioCommands)
        command.setScenarioQuests(ScenarioQuests)

        command.setSceneName(ScenarioRunner.SceneName)
        command.setGroupName(ScenarioRunner.GroupName)

        command.setRepeatScenario(self.Repeat)

        command.onValues(self.Values)

        if command.onInitialize() is False:
            Trace.log("Macro", 0, "ScenarioMacroCommand._onGenerator command not initialize %s:%d - %s %s" % (ScenarioRunner.Name, self.Index, self.CommandType, self.Values))
            return False

        if _DEVELOPMENT is True:
            source.setDocument("Scenario macro command '%s' scene '%s' group '%s' macro index [%u]" % (self.CommandType, ScenarioRunner.SceneName, ScenarioRunner.GroupName, self.Index))
            pass

        # FixMe [AutoSave]
        if command.Immediately is True:
            source.addFunction(ScenarioRunner.endMacro, self.Index)

        if self.Repeat is False:
            ID = ScenarioRunner.createMacroCommand(command)

            source.addFunction(ScenarioRunner.runCommand, ID)

            command.onGenerate(source)

            source.addFunction(ScenarioRunner.endCommand, ID)
        else:
            command.onGenerate(source)

        return True

class ScenarioParallel(ScenarioElement):
    __slots__ = "Count", "commands"

    def __init__(self, Index, Repeat, Count):
        super(ScenarioParallel, self).__init__(Index, "__Parallel__", Repeat)

        self.Count = Count

        self.commands = [[] for i in range(self.Count)]

    def addActive(self, Index, Id, CommandType, *Values):
        command = ScenarioMacroCommand(Index, CommandType, self.Repeat, Values)

        if Id < 0 or Id >= self.Count:
            Trace.log("Scenario", 0, "ScenarioParallel.addActive Index %d Invalid Id %s CommandType %s Values %s" % (Index, Id, CommandType, Values))
            return

        self.commands[Id].append(command)

    def _onGenerator(self, source, ScenarioRunner, ScenarioChapter, ScenarioCommands, ScenarioQuests):
        if _DEVELOPMENT is True:
            source.setDocument("Scenario parallel command '%s' scene '%s' group '%s' macro index [%u]" % (self.CommandType, ScenarioRunner.SceneName, ScenarioRunner.GroupName, self.Index))
            pass

        ParallelScenarioQuests = []
        with source.addParallelTask(self.Count) as parallel_sources:
            for parallel, commands in zip(parallel_sources, self.commands):
                CurParallelScenarioQuests = []
                for command in commands:
                    command.onGenerator(parallel, ScenarioRunner, ScenarioChapter, ScenarioCommands, CurParallelScenarioQuests)
                ParallelScenarioQuests.append(CurParallelScenarioQuests)

        ScenarioQuests.append(('parallel', ParallelScenarioQuests))

        return True

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is not None:
            return False

        return True

class ScenarioRace(ScenarioElement):
    __slots__ = "Count", "commands"

    def __init__(self, Index, Repeat, Count):
        super(ScenarioRace, self).__init__(Index, "__Race__", Repeat)

        self.Count = Count

        self.commands = [[] for i in range(self.Count)]

    def addActive(self, Index, Id, CommandType, *Values):
        command = ScenarioMacroCommand(Index, CommandType, self.Repeat, Values)

        self.commands[Id].append(command)

    def _onGenerator(self, source, ScenarioRunner, ScenarioChapter, ScenarioCommands, ScenarioQuests):
        if _DEVELOPMENT is True:
            source.setDocument("Scenario race command '%s' scene '%s' group '%s' macro index [%u]" % (self.CommandType, ScenarioRunner.SceneName, ScenarioRunner.GroupName, self.Index))
            pass

        RaceScenarioQuests = []
        with source.addRaceTask(self.Count) as race_sources:
            for race, commands in zip(race_sources, self.commands):
                CurParallelScenarioQuests = []
                for command in commands:
                    command.onGenerator(race, ScenarioRunner, ScenarioChapter, ScenarioCommands, CurParallelScenarioQuests)
                RaceScenarioQuests.append(CurParallelScenarioQuests)

        ScenarioQuests.append(('race', RaceScenarioQuests))

        return True

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is not None:
            return False

        return True

class ScenarioShiftCollect(ScenarioElement):
    __slots__ = "Count", "commands"

    def __init__(self, Index, Repeat, Count):
        super(ScenarioShiftCollect, self).__init__(Index, "__ShiftCollect__", Repeat)

        self.Count = Count

        self.commands = [[] for i in range(Count)]

    def addActive(self, Index, Id, *Values):
        self.commands[Id] = dict(InteractionName=Values[0], ShiftName=Values[1], State=Values[2])

    def _onGenerator(self, source, ScenarioRunner, ScenarioChapter, ScenarioCommands, ScenarioQuests):
        if _DEVELOPMENT is True:
            source.setDocument("Scenario shift collect '%s' scene '%s' group '%s' macro index [%u]" % (self.CommandType, ScenarioRunner.SceneName, ScenarioRunner.GroupName, self.Index))
            pass

        source.addShiftCollect(self.Index, self.commands)

        return True

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is not None:
            return False

        return True

def generateParagraph(Index, Paragraphs, source, ScenarioRunner, ScenarioChapter):
    with source.addParallelTask(len(Paragraphs)) as tcp_paragraphs:
        for tci, paragraphID in zip(tcp_paragraphs, Paragraphs):
            if paragraphID == "BEGIN":
                pass
            elif paragraphID == "StageFX1":
                pass
            else:
                if paragraphID[:3] != "PH_":
                    Trace.log("Scenario", 0, "ScenarioParagraph.onGenerator: %s:%d Paragraph %s invalid - 'PH_'" % (ScenarioRunner.getName(), Index, paragraphID))

                def __checkParagraph(id):
                    return ScenarioChapter.isParagraphComplete(id)

                def __filterParagraph(paragraphID, id):
                    if id != paragraphID:
                        return False

                    return True

                tci.addTask("TaskListener", ID=Notificator.onParagraphRun, Check=__checkParagraph, Filter=__filterParagraph, Args=(paragraphID,))

def generatorSceneInitial(source, ScenarioRunner):
    source.addTask("AliasScenarioInit", ScenarioRunner=ScenarioRunner)

def generatorSceneEnter(source, ScenarioRunner):
    source.addTask("AliasScenarioEnter", ScenarioRunner=ScenarioRunner)

PARAGRAPH_WAIT = 1
PARAGRAPH_RUN = 2
PARAGRAPH_COMPLETE = 3

class ScenarioCommands(Initializer):
    def __init__(self, GroupName, SceneName, Index, Paragraphs):
        self.GroupName = GroupName
        self.SceneName = SceneName
        self.Index = Index
        self.Paragraphs = Paragraphs

        self.Quests = []

        self.Status = PARAGRAPH_WAIT

    def _onFinalize(self):
        super(ScenarioCommands, self)._onFinalize()
        self.Quests = []

    def __runCommands(self):
        self.Status = PARAGRAPH_RUN

    def __completeCommands(self):
        self.Status = PARAGRAPH_COMPLETE
        Notification.notify(Notificator.onParagraphCompleteForReal)

    def onGenerator(self, source, ScenarioRunner, ScenarioChapter):
        if ScenarioRunner.isMacroEnd(self.Index) is True:
            return

        if _DEVELOPMENT is True:
            source.setDocument("Scenario commands scene '%s' group '%s' macro index [%u]" % (self.SceneName, self.GroupName, self.Index))
            pass

        generateParagraph(self.Index, self.Paragraphs, source, ScenarioRunner, ScenarioChapter)

        source.addFunction(self.__runCommands)

        source.addFunction(ScenarioRunner.runMacro, self.Index)

        self._onGenerator(source, ScenarioRunner, ScenarioChapter)

        source.addFunction(self.__completeCommands)

        source.addFunction(ScenarioRunner.endMacro, self.Index)

    def _onGenerator(self, source, ScenarioRunner, ScenarioChapter):
        return

    def getQuests(self):
        return self.Quests

    def visitQuests(self, visitor, b, *args):
        """

        :param visitor:
            :return  - control for paragraphs quests traverse logic

        :param b: - brake - work only with races and parallels
            b is True - if visitor return True we breaking if parallel/race was fully checked
            b is False - ignore, used for full paragraph quests traverse


        :return:
                False: visitor result was False, loop braked
                True: visitor result on one of the iteration was True
                None: quest traverse loop finished and visitor result on all quests of paragraph was None
        """

        for quest_container in self.Quests:
            if type(quest_container) is tuple:
                '''
                self.Quests: quests of checking paragraph
                type(quest_container)==tuple(): mean it's parallel/race quests. Else it's common Quest object
                quest_list: quests in thread of race/parallel with index [0:N]
                '''

                quests_type = quest_container[0]  # can be 'race' or 'parallel'
                quest = quest_container[1]  # actual quest list of race/parallel this look like this:
                # [[quests of thread1], [quests of thread2], [quests of thread3], ...]
                completed_threads = 0  # completed_treads mean checked threads

                for quest_list in quest:  # check thread of race/parallel
                    if len(quest_list) == 0:
                        '''
                        quest_list empty, mean thread was completed before, and all quest was deleted
                        
                        if it's race then one completed thread mean all race complete and now we
                            manually set that all threads completed
                            and check next quests after race in paragraph(in self.Quests)
                            
                        else it's parallel and we increment completed threads counter
                            and check next thread in parallel
                        '''
                        if quests_type is 'race':
                            completed_threads = len(quest)
                            break

                        completed_threads += 1
                        continue

                    result = None

                    for q in quest_list:
                        result = visitor(q, *args)

                        if result is None:
                            '''
                            check another quest in thread
                            '''
                            continue

                        if result is True:
                            '''
                            start cheking next quest_list of next thread
                            '''
                            break

                        if result is False:
                            return False

                    if result is None:
                        '''
                        last quest in thread is completed, mean thread is completed
                        
                        if it's race then one completed thread mean all race complete and now we
                            manually set that all threads completed 
                            and check next quests after race in paragraph(in self.Quests)
                        else it's parallel and we increment completed threads counter
                        '''

                        # # THIS PART OF LOGIC MOVED TO brake case
                        # if quests_type is 'race':
                        #     completed_threads = len(quest)
                        #     break

                        completed_threads += 1

                if b is True:
                    '''
                    param b(break): 
                        - if we need find just one quest, we set b=True, 
                          mean if we got result=None we checked all quest in threads race/parallel and we will check
                          next paragraph, or we got result=True, visitor of quest in threads ended loop on force and
                          we will check next paragraph
                    
                        - if we need visitor for all quests in paragraph
                          (even those we can't complete yet), we set b=False
                    
                    Assume visitor is checking for quest which can be completed
                    
                    If all threads is completed
                        then we check for next quest in paragraph after race/parallel
                    else there are quest in race/parallel we can't complete yet and will check next paragraph
                    
                    P.S.
                    previously there was just brake, so even if we complete race/parallel, 
                    (loop for quest type=list finished and all result was None and algorithm continued),
                    algorithm would not check next quest(type=list) or quest(type=Quest) in paragraph
                    also it thread race as parallel before, no way to resolve logic correctly without 
                    parameter which can tell if this race or parallel to resolve logic properly
                    '''
                    if completed_threads == len(quest):
                        continue

                    elif quests_type is 'race':
                        if completed_threads > 0:
                            print('ScenarioCommands.visitQuests race fix fired !!!')
                            continue

                    break
            else:
                '''
                we got not race/parallel quests list but common Quest object
                '''
                quest = quest_container
                result = visitor(quest, *args)

                if result is None:
                    continue

                if result is True:
                    break

                if result is False:
                    return False

        return True  # default return

    def filterQuests(self, filter, *args):
        # not used in project, and probably will work incorrect with race/parallel quests
        quests = []
        for quest in self.Quests:
            if type(quest) is list:
                quest2 = []
                for qList in quest:
                    qList2 = []
                    for q in qList:
                        if filter(q, *args) is True:
                            qList2.append(q)
                    quest2.append(qList2)
                quests.append(quest2)
            else:
                q = quest
                if filter(q, *args) is True:
                    quests.append(q)

        return quests

class ScenarioParagraph(ScenarioCommands):
    def __init__(self, GroupName, SceneName, Index, Paragraphs):
        super(ScenarioParagraph, self).__init__(GroupName, SceneName, Index, Paragraphs)

        self.Preparations = []
        self.Initials = []
        self.Actives = []

    def _onFinalize(self):
        super(ScenarioParagraph, self)._onFinalize()
        for preparations in self.Preparations:
            preparations.onFinalize()

        self.Preparations = []

        for initial in self.Initials:
            initial.onFinalize()

        self.Initials = []

        for active in self.Actives:
            active.onFinalize()

        self.Actives = []

    def _onGenerator(self, source, ScenarioRunner, ScenarioChapter):
        if _DEVELOPMENT is True:
            source.setDocument("Scenario paragraph scene '%s' group '%s' macro index [%u]" % (self.SceneName, self.GroupName, self.Index))
            pass

        for command in self.Preparations:
            command.onGenerator(source, ScenarioRunner, ScenarioChapter, self, self.Quests)

        if len(self.Initials) != 0:
            generatorSceneInitial(source, ScenarioRunner)

            for command in self.Initials:
                command.onGenerator(source, ScenarioRunner, ScenarioChapter, self, self.Quests)

        if len(self.Actives) != 0:
            generatorSceneEnter(source, ScenarioRunner)

            for command in self.Actives:
                command.onGenerator(source, ScenarioRunner, ScenarioChapter, self, self.Quests)

    def addActive(self, Index, CommandType, *Values):
        command = ScenarioMacroCommand(Index, CommandType, False, Values)

        self.Actives.append(command)

    def addPreparation(self, Index, CommandType, *Values):
        command = ScenarioMacroCommand(Index, CommandType, False, Values)

        self.Preparations.append(command)

    def addInitial(self, Index, CommandType, *Values):
        command = ScenarioMacroCommand(Index, CommandType, False, Values)

        self.Initials.append(command)

    def addParallel(self, Index, Count):
        command = ScenarioParallel(Index, False, Count)

        self.Actives.append(command)

        return command

    def addRace(self, Index, Count):
        command = ScenarioRace(Index, False, Count)

        self.Actives.append(command)

        return command

    def addShiftCollect(self, Index, Count):
        command = ScenarioShiftCollect(Index, False, Count)

        self.Actives.append(command)

        return command

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if len(self.Preparations) == 0 and len(self.Initials) == 0 and len(self.Actives) == 0:
            Trace.log("Macro", 0, "ScenarioParagraph %s in Macro Index %s has Paragraph %s with 0 commands" % (self.GroupName, self.Index, self.Paragraphs))

        if type is not None:
            return False

        return True

class ScenarioRepeat(ScenarioCommands):
    def __init__(self, GroupName, SceneName, Index, Paragraphs):
        super(ScenarioRepeat, self).__init__(GroupName, SceneName, Index, Paragraphs)

        self.Preparations = []
        self.Initials = []
        self.Actives = []

        self.UntilIndex = None
        self.UntilParagraphs = []

    def _onFinalize(self):
        super(ScenarioRepeat, self)._onFinalize()

        for preparations in self.Preparations:
            preparations.onFinalize()

        self.Preparations = []

        for initial in self.Initials:
            initial.onFinalize()

        self.Initials = []

        for active in self.Actives:
            active.onFinalize()

        self.Actives = []

    def addActive(self, Index, CommandType, *Values):
        command = ScenarioMacroCommand(Index, CommandType, True, Values)

        self.Actives.append(command)

    def addPreparation(self, Index, CommandType, *Values):
        command = ScenarioMacroCommand(Index, CommandType, True, Values)

        self.Preparations.append(command)

    def addInitial(self, Index, CommandType, *Values):
        command = ScenarioMacroCommand(Index, CommandType, True, Values)

        self.Initials.append(command)

    def addParallel(self, Index, Count):
        command = ScenarioParallel(Index, True, Count)

        self.Actives.append(command)

        return command

    def addRace(self, Index, Count):
        command = ScenarioRace(Index, True, Count)

        self.Actives.append(command)

        return command

    def addShiftCollect(self, Index, Count):
        command = ScenarioShiftCollect(Index, True, Count)

        self.Actives.append(command)

        return command

    def addUntil(self, Index, *Paragraphs):
        self.UntilIndex = Index

        if len(Paragraphs) == 0:
            Trace.log("Scenario", 0, "ScenarioRepeat.addUntil scene %s group %s line %d until invalid setup paragraphs" % (self.SceneName, self.GroupName, self.Index))

        self.UntilParagraphs = Paragraphs

    def _onGenerator(self, source, ScenarioRunner, ScenarioChapter):
        if _DEVELOPMENT is True:
            source.setDocument("Scenario repeat scene '%s' group '%s' macro index [%u]" % (self.SceneName, self.GroupName, self.Index))
            pass

        with source.addRepeatTask() as (source_repeat, source_until):
            for command in self.Preparations:
                command.onGenerator(source_repeat, ScenarioRunner, ScenarioChapter, self, self.Quests)

            if len(self.Initials) != 0:
                generatorSceneInitial(source_repeat, ScenarioRunner)

                for command in self.Initials:
                    command.onGenerator(source_repeat, ScenarioRunner, ScenarioChapter, self, self.Quests)

            if len(self.Actives) != 0:
                generatorSceneEnter(source_repeat, ScenarioRunner)

                for command in self.Actives:
                    command.onGenerator(source_repeat, ScenarioRunner, ScenarioChapter, self, self.Quests)

            generateParagraph(self.Index, self.UntilParagraphs, source_until, ScenarioRunner, ScenarioChapter)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if len(self.Preparations) == 0 and len(self.Initials) == 0 and len(self.Actives) == 0:
            Trace.log("Macro", 0, "!!!!!!! Warning: %s in Macro %s has Paragraph with 0 commands" % (self.GroupName, self.Paragraphs))

        if type is not None:
            return False

        return True

class Scenario(object):
    def __init__(self):
        self.ScenarioID = None
        self.GroupName = None
        self.SceneName = None

        self.paragraphs = []
        self.repeats = []

    def addParagraph(self, Index, *Paragraphs):
        paragraph = ScenarioParagraph(self.GroupName, self.SceneName, Index, Paragraphs)

        self.paragraphs.append(paragraph)

        return paragraph

    def getParagraphs(self):
        return self.paragraphs

    def getRepeats(self):
        return self.repeats

    def getRunParagraphs(self):
        runParagraphs = []
        for paragraph in self.paragraphs:
            if paragraph.Status != PARAGRAPH_RUN:
                continue
            runParagraphs.append(paragraph)

        return runParagraphs

    def getWaitParagraphs(self):
        waitParagraphs = []
        for paragraph in self.paragraphs:
            if paragraph.Status != PARAGRAPH_WAIT:
                continue
            waitParagraphs.append(paragraph)

        return waitParagraphs

    def addRepeat(self, Index, *Paragraphs):
        repeat = ScenarioRepeat(self.GroupName, self.SceneName, Index, Paragraphs)

        self.repeats.append(repeat)

        return repeat

    def onInitialize(self, GroupName, SceneName, ScenarioID):
        self.GroupName = GroupName
        self.SceneName = SceneName
        self.ScenarioID = ScenarioID

        self._onInitialize()

    def _onInitialize(self):
        return

    def onFinalize(self):
        for paragraph in self.paragraphs:
            paragraph.onFinalize()

        self.paragraphs = []

        for repeat in self.repeats:
            repeat.onFinalize()

        self.repeats = []

    def onGenerator(self, ScenarioRunner, ScenarioChapter):
        paragraphs_taskChain = TaskManager.createTaskChain(GroupName=self.GroupName)
        paragraphs_source = paragraphs_taskChain.createTaskSource()

        paragraphs_source.addNotify(Notificator.onScenarioRun, self.ScenarioID)

        try:
            self.__onGeneratorParagraphs(paragraphs_source, ScenarioRunner, ScenarioChapter)
        except TaskGeneratorException as ex:
            Trace.log("Manager", 0, "Scenario invalid generate paragraphs: %s", ex)

            return False
            pass

        paragraphs_source.addNotify(Notificator.onScenarioComplete, self.ScenarioID)

        repeats_taskChain = TaskManager.createTaskChain(GroupName=self.GroupName)
        repeats_source = repeats_taskChain.createTaskSource()

        try:
            self.__onGeneratorRepeats(repeats_source, ScenarioRunner, ScenarioChapter)
        except TaskGeneratorException as ex:
            Trace.log("Manager", 0, "Scenario invalid generate repeats paragraphs: %s", ex)

            return False
            pass

        tcs = [paragraphs_taskChain, repeats_taskChain]

        return tcs

    def __onGeneratorParagraphs(self, scope, ScenarioRunner, ScenarioChapter):
        for paragraph, source in scope.addParallelTaskList(self.paragraphs):
            paragraph.onGenerator(source, ScenarioRunner, ScenarioChapter)

    def __onGeneratorRepeats(self, scope, ScenarioRunner, ScenarioChapter):
        for repeat, source in scope.addParallelTaskList(self.repeats):
            repeat.onGenerator(source, ScenarioRunner, ScenarioChapter)