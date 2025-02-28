def onInitialize():
    from Foundation.TaskManager import TaskManager

    tasks = [
        "TaskItemPick"
        , "TaskItemClick"
        , "TaskMovieItemClick"
        , "TaskMovieItemClickOBS"
        , "TaskMovieItemPick"
        , "TaskItemPlaceInventoryItem"
        , "TaskItemPlaceInventoryAccumulateItem"
        , "TaskItemPopUp"
        , "TaskItemPlaceItem"
        , "TaskItemAutoClick"
        , "TaskItemEnable"
        , "TaskItemInvalidUse"
        , "TaskEnableBonusItem"

        , "TaskZoomOpen"
        , "TaskZoomInit"
        , "TaskZoomEnter"
        , "TaskZoomLeave"
        , "TaskZoomEmpty"
        , "TaskZoomLeave"
        , "TaskZoomClose"
        , "TaskZoomClick"
        , "TaskZoomInterrupt"

        , "TaskScenePlusInit"
        , "TaskScenePlusEnter"

        , "TaskStageInit"
        , "TaskStageSave"
        , "TaskStageResume"
        , "TaskStageRun"

        , "TaskHOGFoundItem"
        , "TaskHOGComplete"
        , "TaskHOGRollingComplete"
        , "TaskHOGItemTakeEffect"
        , "TaskHOGInventoryCrossOut"
        , "TaskHOGInventoryFoundItem"

        , "TaskInventoryScrolling"
        , "TaskInventoryAddItem"
        , "TaskInventoryAddInventoryItem"
        , "TaskInventorySlotSetItem"
        , "TaskInventorySlotReturnItem"
        , "TaskInventorySlotRemoveItem"
        , "TaskArrowAttachInventoryItem"
        #    , "TaskInventoryChangeInventoryItem"
        , "TaskInventoryCombineInventoryItem"
        , "TaskInventoryItemDontDrop"
        , "TaskInventoryCurrentSlotIndex"
        , "TaskInventoryCarriageChange"
        , "TaskInventorySlotAddInventoryItem"
        , "TaskInventorySlotsHideInventoryItem"
        , "TaskInventorySlotsShowInventoryItem"
        , "TaskInventorySetupSlots"
        , "TaskInventorySlotAttachMovie"
        , "TaskInventoryDetachItem"
        , 'TaskInventoryRise'

        , "TaskArrowAttach"

        , "TaskEnigmaPlay"
        , "TaskEnigmaComplete"

        , "TaskScenarioRun"
        , "TaskScenarioSkip"
        , "TaskScenarioEnd"
        , "TaskScenarioCancel"
        , "TaskScenarioInjectionCreate"
        , "TaskScenarioInit"
        , "TaskScenarioEnter"
        , "TaskScenarioLeave"

        , "TaskQuestRun"

        , "TaskEffectInventoryPickInventoryItem"
        , "TaskEffectInventoryAddInventoryItem"
        , "TaskEffectInventoryAddInventoryItemFromPoint"
        , "TaskEffectInventoryGetInventoryItem"

        #    , "TaskChapter"

        , "TaskTipPlay"
        , "TaskTipFinish"

        , "TaskSocketPlaceInventoryItem"  # click socket with identified inventoryItem, can remove attach
        , "TaskSocketPlaceInventoryAccumulateItem"  # click socket with identified inventoryItem, can remove attach
        , "TaskSocketUseItem"  # click socket with identified item, can remove attach
        , "TaskZoomGiveInventoryItem"
        , "TaskTransitionGiveInventoryItem"

        , "TaskHintSetMask"
        , "TaskHintClearMask"
        , "TaskHintClick"

        , "TaskSetCursorMode"

        , "TaskFanClick"
        , "TaskFanComplete"
        , "TaskFanFoundItem"
        , "TaskFanItemInHand"
        , "TaskFanItemInNone"
        , "TaskFanItemInFan"
        , "TaskFanItemInvalidUse"
        , "TaskFanPlay"
        , "TaskFanUse"
        , "TaskFanOpen"
        , "TaskFanClose"

        , "TaskTipItemFinish"
        , "TaskTipItemPlay"

        , "TaskFoundBonusItem"
        , "TaskBonusItemCollect"

        , "TaskFittingInventoryAddInventoryItem"
        , "TaskFittingInventoryRemoveInventoryItem"
        , "TaskFittingInventoryAddFitting"
        , "TaskFittingInventoryRemoveFitting"
        , "TaskFittingInventorySlotSetItem"
        , "TaskFittingInventorySlotReturnItem"
        , "TaskEffectFittingInventoryReturnInventoryItem"
        , "TaskEffectFittingInventoryAddInventoryItem"
        , "TaskEffectFittingInventoryGetInventoryItem"

        , "TaskJournal"
        , "TaskSplashScreenPlay"
        , "TaskCutScenePlay"
        , "TaskDialogPlay"
        , "TaskDialogSkip"

        , "TaskObjective"
        , "TaskObjectiveFinish"
        , "TaskObjectiveStart"
        , "TaskMindPlay"
        , "TaskDialogBoxPlay"
        , "TaskMousePull"
        , "TaskActiveLayerEsc"
        , "TaskSpellOnItem"
        , "TaskSpellOnZoom"
        , "TaskSpellOnSocket"
        , "TaskSpellOnTransition"
        , "TaskSpellUse"
        , "TaskPlaceRespectSlot"
        , "TaskHOGRollingInventoryCrossOut"
        , "TaskHOGFittingItemUse"
        , "TaskHOGFittingItemUseSocket"
        , "TaskHOGFindItemClick"
        , "TaskFunctionResult"
        , 'TaskDelayPointer'
        , "TaskAnimatableButtonClick"
        , "TaskAnimatableButtonClickEndUp"
        , "TaskAnimatableButtonEnter"
        , "TaskAnimatableButtonLeave"

        , "TaskInventorySlotReturnItemFX"
        , "TaskEffectInventoryGetInventoryItemFX"

        , "TaskMusicFadeIn"
        , "TaskMusicFadeOut"

        , "TaskMacroCommandRun"

        , "TaskSocketUseElementalMagic"
        , "TaskSocketPickElementalMagic"
    ]

    TaskManager.importTasks("HOPA.Task", tasks)

    aliases = [
        "AliasStageRun"
        , "AliasTransition"

        , "AliasFadeIn"
        , "AliasFadeOut"
        , "AliasFadeInBefore"

        , "AliasMessageShow"
        , "AliasMessageOKShow"
        , "AliasMessageOKClick"
        , "AliasMessageHide"
        , "AliasMessageYes"
        , "AliasMessageNo"
        , "AliasMessageYesUp"
        , "AliasMessageNoUp"

        , "AliasEnigmaPlay"
        , "AliasHOGFindItem"
        , "AliasHOGFoundItem"
        , "AliasHOGRollingFindItem"
        , "AliasHOGRollingFoundItem"
        , "AliasHOGFXPartsGatheringFindItem"
        , "AliasHOGFXPartsGatheringFoundItem"
        , "AliasHOGSilhouetteFindItem"
        , "AliasHOGSilhouetteFoundItem"

        , "AliasTipPlay"
        , "AliasMindPlay"
        , "AliasDialogBoxPlay"

        , "AliasInventoryScrolling"
        , "AliasInventorySlotsShiftLeft"
        , "AliasInventorySlotsShiftRight"
        , "AliasInventoryGetInventoryItem"
        , "AliasInventoryReturnInventoryItem"
        , "AliasInventoryPickInventoryItem"
        , "AliasInventoryAddInventoryItem"
        , "AliasInventoryAddInventoryItemFromPoint"
        , "AliasInventoryRemoveAttachInventoryItem"
        , "AliasInventoryCombineInventoryItem"
        , "AliasInventoryInvalidUseInventoryItem"
        , "AliasInventoryInvalidCombineInventoryItem"
        , "AliasInventoryRemoveInventoryItem"
        , "AliasInventoryShowCurrentSlots"
        , "AliasInventoryFindItem"
        , "AliasInventorySlotsScrollingRight"
        , "AliasInventorySlotsScrollingLeft"
        , "AliasInventorySlotsScrolling"
        , "AliasEffectInventoryReturnInventoryItem"
        , "AliasInventoryChangeCurrentSlotIndex"
        , "AliasItemAttach"
        , "AliasRemoveItemAttach"
        , "AliasInventorySlotsMoveAddItem"
        , "AliasInventorySlotsMoveLeft"
        , "AliasInventorySlotsMoveRight"
        , "AliasInventoryItemAttach"
        #    , "AliasEffectBeforeInventoryAddItem"

        , "AliasInventoryItemPopUp"

        , "AliasInventorySlotsMoveLeft"
        , "AliasInventorySlotsMoveRight"
        , "AliasInventorySlotsMoveAddItem"

        , "AliasFittingInventoryAddInventoryItem"
        , "AliasFittingInventoryReturnInventoryItem"
        , "AliasFittingInventoryInvalidUseInventoryItem"
        , "AliasFittingInventoryRemoveInventoryItem"
        , "AliasFittingInventoryGetInventoryItem"
        , "AliasFittingInventoryInvalidCombineInventoryItem"
        , "AliasFittingFindItem"

        , "AliasDialogPlay"
        , "AliasDialogSwitchAvatar"

        , "AliasFanFindItem"
        , "AliasFanBezier2To"

        , "AliasTransition"
        , "AliasObjectClick"
        , "AliasObjectEnter"
        , "AliasObjectLeave"

        #    , "AliasChapter"
        , "AliasObjective"
        , "AliasObjectives"

        , "AliasFindItem"
        , "AliasDragDropItem"
        , "AliasDragDropPuzzle"
        , "AliasGetBonusItem"
        , "AliasJournalAddItemPage"

        , "AliasSystemMessage"
        , "AliasGiveItem"
        , "AliasSpinCircles"
        , "AliasOverViewPlay"
        , "AliasMousePull"
        , "AliasPetItem"
        , "AliasBoneUsage"
        , "AliasHOGRollingItemFoundEffect"
        , "AliasHOGSilhouetteItemFoundEffect"
        , "AliasHOGFXPartsGatheringItemFoundEffect"
        , "AliasItemDetach"
        , "AliasSpellUsage"
        , "AliasEnableMagicVision"

        , "AliasHOGFittingMoveItemToSlot"
        , "AliasHOGInventoryFittingAddItem"
        , "AliasHOGFittingUseItem"
        , "AliasHOGFittingReturnItemToSlot"
        , "AliasCombatSpellAiTurn"
        , "AliasCombatSpellPlayerTurn"
        , "AliasMultyplMovePlay"
        , "AliasBombGamePlayerClickProcces"
        , "AliasBombGameBombRotate"

        , "AliasCruiseControlAction"

        , "AliasInventoryAddInventoryItemFX"
        , "AliasInventoryAddInventoryAccumulateItemFX"
        , "AliasInventoryRemoveInventoryItemFX"
        , "AliasInventoryReturnInventoryItemFX"
        , "AliasItemDetachFX"
        , "AliasInventoryInvalidUseInventoryItemFX"
        , "AliasInventorySlotsMoveRemoveItem"

        , "AliasCollectedAmuletAddEffect"
        , "AliasPickSpellTokenEffect"
        , "AliasPickLabItemEffect"

        , "AliasScenarioInit"
        , "AliasScenarioEnter"

        , "AliasNotEnoughGold"
        , "AliasNotEnoughEnergy"

        , "AliasEnergyConsume"
    ]

    TaskManager.importTasks("HOPA.Alias", aliases)

    policies = [
        "PolicyHintWayEffect"
        , "PolicyHintActivateWayEffect"
        , "PolicyHintNotFoundMind"

        , "PolicyHintWayTargetLoopEffect"
        , "PolicyHintWayEffectInterrupt"

        , "PolicyHintTargetEffect"
        , "PolicyHintTargetEffectWait"
        , "PolicyHintTargetInterruptEffect"
        , "PolicyHintTargetLoopEffect"
        , "PolicyHintTargetLoopInterruptEffect"

        , "PolicyHintTargetStop"
        , "PolicyHintTargetInventoryStop"
        , "PolicyHintWayStop"

        , "PolicyHintInventoryTargetEffect"
        , "PolicyHintInventoryTargetEffectWait"
        , "PolicyHintInventoryTargetInterruptEffect"
        , "PolicyHintInventoryTargetLoopEffect"
        , "PolicyHintInventoryTargetLoopInterruptEffect"

        , "PolicyHintReloadMovie"
        , "PolicyHintReadyEffect"
        , "PolicyHintReadyEffectMovie"
        , "PolicyHintReadyInterruptEffect"
        , "PolicyHintReadyInterruptEffectMovie"
        , "PolicyHintReadyMovie"
        , "PolicyHintReadyMovieFade"
        , "PolicyHintReadyMovieStop"
        , "PolicyHintActivateMovie"
        , "PolicyHintEmptyDefault"
        , "PolicyHintCharged"

        , "PolicyHintPlayDefault"
        , "PolicyHintPlayPaid"

        , "PolicyBlackBarPlayStatic"
        , "PolicyBlackBarPlayStaticWithMovie"
        , "PolicyBlackBarMovieClick"
        , "PolicyBlackBarPlayText"

        , "PolicyInventoryScrollingDefault"
        , "PolicyInventoryFXScrolling"

        , "PolicyDialogStaticText"
        , "PolicyDialogDynamicTextPlay"
        , "PolicyDialogAvatar"
        , "PolicyDialogAvatarMovie"
        , "PolicyDialogAvatarMovie2"
        , "PolicyDialogVoiceAvatar"
        , "PolicyMonologue"

        , "PolicyDummy"
        , "PolicyHintTargetDummy"

        , "PolicyEffectInventoryAddInventoryItemParticles"
        , "PolicyEffectInventoryAddInventoryItemParticles2"
        , "PolicyEffectInventoryAddInventoryItemWithItemPopup"
        , "PolicyEffectInventoryAddInventoryItemWithItemPopupForCountItemFX"
        , "PolicyEffectFXInventoryAddInventoryItemParticles"
        , "PolicyPickInventoryItemEffect"
        , "PolicyPickInventoryItemEffectEnd"
        , "PolicyPickInventoryItemEffectStop"
        , "PolicyPickInventoryItemEffectDummy"

        , "PolicyCloseProfileOk"
        , "PolicyCloseProfileOkClose"

        , "PolicyCloseProfileMovieOk"

        , "PolicyMenuHelpDefault"
        , "PolicyCutSceneSkip"
        , "PolicyCutSceneNext"

        , "PolicyHintClickButton"
        , "PolicyHintClickMovieButton"
        , "PolicyHintClickButtonEndUp"
        , "PolicyHintClickSocket"

        , "PolicyCreditsDefault"
        , "PolicyHOGFindItemFly"
        , "PolicyBlackBarPlayWithMovie"
        , "PolicyBlackBarTipPlayWithMovie"
        # , "PolicyHOGRollingItemFoundEffectCrossOut" # Deprecated

        , "PolicyEffectInventoryGetInventoryItemFXMovie"
        , "PolicySkipPuzzleClickButton"
        , "PolicySkipPuzzleClickMovie2Button"
        , "PolicySkipPuzzleReadyEffect"
        , "PolicySkipPuzzleReadyMovie"
        , "PolicySkipPuzzlePlayPaid"
        , "PolicySkipPuzzlePlayDefault"
        , "PolicyHOGDisappearanceItemFoundEffect"
        , "PolicyDeleteItemFromInventory"
        , "PolicyCheckMarkNearItem"
        , "PolicyHOGRollingMovieItemFoundEffect"
        , "PolicyHOGRollingMovie2ItemFoundEffect"
        , "PolicyCheckMarkNearMovieItem"
        , "PolicyTransitionBack"
        , "PolicyTransitionBackWay"

        , "PolicyInteractionShiftCollect"
        , "PolicySocketShiftCollect"

        , "PolicyGuideOpenPaid"
        , "PolicyGuideOpenDefault"

        , "PolicyNotEnoughGoldSpecialPacks"
        , "PolicyNotEnoughEnergySpecialPacks"
        , "PolicyNotEnoughGoldStoreWithPack"
        , "PolicyNotEnoughEnergyStoreWithPack"
        , "PolicyNotEnoughGoldWithLimitedOffer"
        , "PolicyNotEnoughEnergyWithLimitedOffer"
        , "PolicyNotEnoughGoldRewardedAdvert"
        , "PolicyNotEnoughEnergyRewardedAdvert"

        , "PolicyAuthGoogleService"

        , "PolicyNotEnoughGoldDialog"
        , "PolicyNotEnoughGoldMessage"
        , "PolicyNotEnoughEnergyDialog"
        , "PolicyNotEnoughEnergyMessage"

        , "PolicyEnergyClickItem"

        , "PolicyTransitionAdvertising"
    ]

    TaskManager.importTasks("HOPA.Policy", policies)

    from Notification import Notification

    notifiers = [
        "onChapters"
        , "onTutorialComplete"
        , "onTutorialSkip"
        , "onTutorialSkipEnd"
        , "onTutorialSkipRequest"
        , "onNewspaperOpen"
        , "onNewspaperShow"
        , "onMessage"
        , "onTutorialRunScenarios"
        , "onScenarioInjectionEnd"
        , "onTabDiaryOpen"
        , "onJournalOpen"
        , "onJournalClose"
        , "onJournalLeft"
        , "onJournalRight"
        , "onJournalAppendPage"
        , "onJournalAddPage"
        , "onJournalSetPage"
        , "onJournalStart"
        , "onJournalAllPagesFound"
        , "onGuidebookAddPage"

        , "onSurveyPhotoOpen"
        , "onSurveyPhotoClose"

        , "onShiftNext"

        , "onTipShow"
        , "onTipPlayComplete"
        , "onTipActivate"

        , "onTipActivateWithoutParagraphs"
        , "onTipRemoveWithoutParagraphs"

        , "onObjectiveActivate"
        , "onObjectiveShow"
        , "onObjectiveHide"

        , "onDialogBoxShow"
        , "onDialogBoxShowRelease"
        , "onDialogBoxPlayComplete"

        , "onMindShow"
        , "onMindPlayComplete"

        , "onDialogShow"
        , "onDialogHide"
        , "onDialogMessageComplete"
        , "onDialogSkip"

        , "onBlackBarRelease"

        , "onNavigationButtonPressed"
        , "onButtonBackPressed"

        , "onItemPopUp"
        , "onItemPopUpClose"
        , "onItemPopUpOpen"

        , "onMovieItemClick"
        , "onMovieItemPick"
        , "onMovieItemEnter"
        , "onMovieItemLeave"

        , "onSoundEffectOnObject"

        , "onChangeGameMusic"
        , "onChangeMenuMusic"

        , "onItemInvalidUse"
        , "onSocketUseItemInvalidUse"
        , "onItemPicked"
        , "onItemClickToInventory"
        , "onItemChangeEnable"
        , "onItemEffectEnd"
        , "onInventoryFXAction"
        , "onInventoryFXActionEnd"

        , "onInventoryAttachMovies"
        , "onInventoryActivate"
        , "onInventoryDeactivate"
        , "onInventoryClickReturnItem"
        , "onInventoryClickRemoveItem"
        , "onInventoryActionEnd"
        , "onInventoryCombineInventoryItem"
        , "onInventoryRemoveInventoryItem"
        , "onInventoryRemoveItem"
        , "onInventoryReturnInventoryItem"
        , "onInventoryPickInventoryItem"
        , "onInventoryItemMouseEnter"
        , "onInventoryItemMouseLeave"
        , "onInventoryUpdateItem"
        , "onInventoryAddItem"
        , "onInventoryAppendInventoryItem"
        , "onInventoryReady"
        , "onInventoryItemCountComplete"
        , "onInventoryItemTake"
        , "onInventoryItemInvalidUse"
        , "onInventoryPrepareToItem"
        , "onInventoryScrolling"
        , "onInventoryCurrentSlotIndex"
        , "onInventoryAttachInvItemToArrow"
        , "onInventoryHide"
        , "onInventoryShow"
        , "onInventoryUp"
        , "onInventorySlotItemEnter"
        , "onInventorySlotItemLeave"
        , "onInventorySlotSetItem"
        , "onInventorySlotsShiftEnd"
        , "onInventoryRise_Complete"
        , "onInventoryFold_Complete"
        , "onInventoryItemDetach"
        , "onInventoryItemPick"

        , "onEnigmaPlay"
        , "onEnigmaStart"
        , "onEnigmaComplete"
        , "onEnigmaStop"
        , "onEnigmaPause"
        , "onEnigmaRestore"
        , "onEnigmaSkip"
        , "onEnigmaUndoStep"
        , 'onEnigmaActivate'
        , 'onEnigmaDeactivate'

        , "onShiftCollectSkip"

        , "onPazzleFoundElement"
        , "onBeginMovingChip"
        , "onPlaceChip"
        , "onColumnPlaced"
        , "onChipTransporterPlay"
        , "onChessTurn"
        , "onHintClick"
        , "onHintActivate"
        , "onHintActionStart"
        , "onHintActionEnd"
        , "onHintUIActionEnd"
        , "onCurrentHintEnd"

        , "onFanClick"
        , "onFanItemInvalidUse"
        , "onFanComplete"
        , "onFanClose"
        , "onFanCloseDone"
        , "onFanOpen"

        , "onHOGInventoryFoundItem"
        , "onHOGCloseClick"
        , "onHOGItemPicked"

        , "onBonusItemCollect"
        , "onOverclickHook"
        , "onOverClick"

        , "onChangeDifficulty"

        , "onPlaySplashScreens"
        , "onCutScenePlay"
        , "onCutSceneSkip"
        , "onCutSceneComplete"
        , "onCutSceneStart"

        , "onStageAutoSave"

        , "onSliderMusic"
        , "onSliderSound"
        , "onSliderUpDing"

        , "onTabClick"
        , "onTasksShow"

        , "onHOGFoundItem"
        , "onHOGInventoryAppendItem"

        , "onHOGComplete"
        , "onHOGStart"
        , "onHOGStop"
        , "onHOGSkip"

        , "onMusicPlay"
        , "onMusicStop"
        , "onMusicContinue"

        , "onMusicPlatlistPlay"
        , "onMusicMenu"
        , "onMusicMenuReturn"

        , "onPuzzleDragDropWin"
        , "onPuzzleOutPlaced"
        , "onAttachTrade"
        , "onOverView"
        , "onOverViewLeave"
        , "onMousePull"
        , "onPuzzleDragWrongPlaced"
        , "onInGameMenuCalled"
        , "onInGameMenuShow"

        , "onSpotHide"
        , "onSpotActivate"
        , "onSpotDeactivate"
        , "onSpinWin"
        , "onSpin"
        , "onSpinMove"
        , "onMapMarked"
        , "onEnigmaReset"
        , "onPetPush"
        , "onPetComplete"
        , "onPetSwitch"
        , "onPetLeave"
        , "onInstructionPullIn"
        , "onEnigmaAction"
        , "onAwardsOpen"
        , "onBoneAdd"
        , "onTrafficJamClick"
        , "onBoneUse"
        , "onEscPressed"
        , "onChipsMoving"
        , "onPullArrowAttach"
        , "onPullArrowDetach"
        , "onPullWrong"
        , "onMousePullComplete"
        , "onChase"
        , "onChased"
        , "onBonusItemFound"
        , "onGetItem"
        , "onHintSceneException"
        , "onTutorialShow"
        , "onTutorialHide"
        , "onTasksOpen"
        , "onTasksClose"
        , "onNoteClick"
        , "onMagicVisionDone"
        , "onMagicVisionStart"
        , "onMagicVisionBlockScene"
        , "onMagicVisionUnblockScene"

        , "onSelectedDifficulty"
        , "OptionsClose"
        , "onCreateNewProfile"
        , "onNewProfile"
        , "onProfileCreated"

        , "OnOverViewShowed"

        , "onEditProfile"
        , "onHOGFittinItemReturn"
        , "onCombatSpellSlotClick"
        , "onRemoveAccount"
        , "onReloadAccount"

        , "onLightCircleGameCircleClick"

        , "onPlumberItemWinPos"
        , "onPlumberCollision"

        , "onCruiseActionEnd"
        , "onBombEndMov"
        , "onBombGameEnd"
        , "onBombGameMoveDir"

        , "onExtraEnigmaPlay"
        , "onExtraHOGPlay"

        , "onAnimatableButtonClick"
        , "onAnimatableButtonClickEndUp"
        , "onAnimatableButtonMouseLeave"
        , "onAnimatableButtonMouseEnter"

        , "onSpellPrepared"
        , "onSpellReady"
        , "onSpellLock"
        , "onSpellBeginUse"
        , "onSpellEndUse"
        , "onSpellUseMacroBegin"
        , "onSpellUseMacroEnd"

        , "onSpellOneMouseEnter"
        , "onSpellOneMouseLeave"
        , "onSpellTwoMouseEnter"
        , "onSpellTwoMouseLeave"
        , "onSpellThreeMouseEnter"
        , "onSpellThreeMouseLeave"
        , "onSpellFourMouseEnter"
        , "onSpellFourMouseLeave"

        , "onManaIncrease"
        , "onManaDecrease"
        , "onManaSearchBegin"
        , "onManaFind"

        , "onSurveyComplete"

        , "onZoomEnigmaChangeFrameGroup"
        , "onZoomEnigmaChangeBackFrameGroup"

        , "onZoomAttachToFrame"
        , "onZoomDeAttachToFrame"
        , "onItemZoomEnter"
        , "onItemZoomLeaveOpenZoom"

        , "onAchievementUnlocked"
        , "onAchievementExternalUnlocked"
        , "onAchievementProgress"
        , "onCloseAchievementPlate"

        , "onCollectedAmuletAdd"
        , "onCollectedAmuletUse"
        , "onGlobeGameRotate"
        , "onHanoisTowerClick"

        , "onMapPointBlock"
        , "onMapPointUnblock"
        , "onMapTransition"
        , "onMapSilenceOpen"
        , "onMapOpen"
        , "onMapClose"
        # , "onTaskListShow"
        # , "onTaskListShowOpen"
        # , "onTaskListShowIdle"
        # , "onTaskListShowHide"
        , "onMapHogUnblock"
        , "onCollectedMapAddPart"

        , "onDiaryClose"

        , "onAddReagent"
        , "onCheckReagentReaction"
        , "onCheckReagentsButton"
        , "onReagentsCleanData"

        , "onPetnaSwap"
        , "onRailRoadGameMove"
        , "onSandGlassMouseEnterSocket"
        , "onSandGlassMouseLeaveSocket"
        , "onSandGlassMouseClickSocket"

        , "onLetItSlideWin"
        , "onPickLabItem"

        , "onCommandMusicFadeIn"
        , "onCommandMusicFadeOut"

        , "onShootGameRestart"
        , "onAccountChangeName"
        , "onInventoryItemPlace"
        , "onInventoryChage"

        , "onAssociationElementActive"

        , "onGameComplete"
        , "onBonusGameComplete"
        , "onStrategyGuideZoomOpen"

        , "onProfileDelete"
        , "onProfileChange"

        , "onReloaderBegin"
        , "onReloaderEnd"

        , "onSessionInvalidLoad"
        , "onUseRune"
        , "onStartUseRune"
        , "onRuneReady"
        , "onMahjongFoundPair"

        , "onEnigmaSlotClick"
        , "onEnigmaChipMove"
        , "onGroupEnable"
        , "onGroupDisable"
        , "onMindGroupDisable"
        , "onGroupEnableMacro"

        , "onMagicGloveClick"
        , "onSetReloading"
        , "onTutorialFadeShow"
        , "onTutorialFadeShowEnd"
        , "onTutorialFadeHide"
        , "onTutorialFadeHideEnd"

        , "onItemCollectInit"
        , "onFinishItemCollect"
        , "onItemCollectComplete"
        , "onCheatTest"
        , "onTutorial_Start"
        , "onTutorialProgres"
        , "onTutorialFinalSkip"
        , "onTutorialBlockScreen"
        , "onChapterDone"

        , "onClickItemCollectHintSocket"
        , 'onItemCollectSetItem'
        , 'onCloseCurrentItemCollect'
        , 'onCloseItemCollect'
        , 'onItemPopUpEnd'
        , 'onMindEndlessEnd'
        , 'onCheatAutoSave'
        , 'onBlockInput'
        , 'onAppendFoundItemsHOG2'
        , 'onDebugTweenLeft'
        , 'onDebugTweenRight'
        , 'onShowMindByID'
        , 'onRuneListChanges'

        , 'onBonusSceneChangeState'
        , 'onBonusSceneTransition'
        , 'onBonusCutScenePlay'
        , 'onBonusMusicPlaylistPlay'
        , 'onBonusVideoOpenCutScene'

        , 'onCollectiblesComplete'
        , 'onCollectiblesPart'
        , 'onSwitchCollectible'
        , 'onHintStartReloading'
        , 'onHintReloadEnter'
        , 'onHintReloadLeave'

        , 'onAddAchievementPlateToQueue'
        , 'onLocationComplete'
        , 'onSceneCompleteCollectibles'
        , 'onParagraphCompleteForReal'

        , 'onChapterSelectionChoseChapter'
        , 'onChapterSelectionClose'
        , 'onChapterOpen'
        , 'onChapterSelectionBlock'
        , 'onChapterSelectionResetProfile'

        , 'onMapEntityInit'
        , 'onMapEntityDeactivate'

        , 'onDragDropItemCreate'
        , 'onDragDropItemComplete'
        , 'onHOGDragDropMGInit'
        , 'onHOGDragDropCounterFrameSwitch'
        , 'onHOGDragDropComplete'
        , 'onHOGDragDropUpdateText'

        , 'onHunt2dPreyHit'

        , 'onSpellUISpellButtonClick'
        , 'onSpellUISpellUnlock'
        , 'onSpellUISpellLock'
        , 'onSpellUISpellUpdate'

        , 'onSpellAmuletButtonClick'
        , 'onSpellAmuletAddPower'
        , 'onSpellAmuletRemovePower'
        , 'onSpellAmuletUsePower'
        , 'onSpellAmuletBlockPower'
        , 'onSpellAmuletUnblockPower'
        , 'onSpellAmuletOpenClose'
        , 'onSpellAmuletStateChange'
        , 'onSpellAmuletPowerButtonStateChange'
        , 'onSpellAmuletSpellButtonStateChange'

        , 'onSpellMacroComplete'

        , 'onPopupMessageShow'
        , 'onMacroClick'

        , 'onHOGFittingItemUsed'
        , 'onHOGFittingItemPicked'
        , 'onHOGFittingItemDetached'

        , 'onLoadingFinishedSuccess'
        , 'onAchievementMovieVisible'

        , "onScenarioInjectionCreate"
        , "onScenarioRun"
        , "onScenarioComplete"
        , "onScenarioInit"
        , "onScenarioEnter"
        , "onScenarioLeave"

        , "onQuestRun"
        , "onQuestEnd"

        , "onParagraph"

        , "onMacroArrowAttach"
        , "onMacroCommandParams"
        , "onMacroCommandRun"
        , "onMacroCommandEnd"
        , 'onMacroAttachItemRemoveObserver'

        , "onGiftExchangeRedeemResult"

        , "onProductGroupReset"
        , "onProductGroupStartProgress"
        , "onProductGroupProgress"

        , "onMorphPicked"
        , "onMorphsSceneComplete"
        , "onAllMorphsPicked"
        , "onMorphsCheatSceneReset"

        , "onDialogWindowConfirm"
        , "onDialogWindowCancel"

        , "onEnergyConsumed"
        , "onEnergyNotEnough"
        , "onEnergyRecharge"
        , "onEnergyCharged"
        , "onEnergyIncrease"
        , "onEnergyDecrease"
        , "onEnergySet"
        , "onIndicatorClicked"

        , "onStoreSetPage"
        , "onStoreTabSwitched"
        , "onStorePageNewActions"
        , "onStorePageNewActionsEnd"
        , "onStorePageButtonClick"
        , "onStoreTabSectionClickedBack"
        , "onStoreTabSectionClickedTab"

        , "onElementalMagicReady"
        , "onElementalMagicReadyEnd"
        , "onElementalMagicUse"
        , "onElementalMagicPick"
        , "onElementalMagicInvalidClick"
        , "onElementalMagicRingMouseEnter"
        , "onElementalMagicRingMouseLeave"

        , "onMazeScreensGroupDone"
    ]

    from Foundation.Notificator import Notificator
    Notificator.addIdentities(notifiers)

    from TraceManager import TraceManager

    traceList = [
        "HOGManager"
        , "Transition"
        , "MindManager"
        , "TipManager"
        , "ItemManager"
        , "MacroCommand"
        , "TaskInventoryReturnItem"
        , "ShootingRangeManager"
        , "SparksAction"
        , "NotebookManager"
        , "NotebookInventoryManager"
        , "NotebookInventoryListManager"
        , "NotebookDescription"
        , "TasksShowManager"
        , "Notebook"
        , "SpinCirclesMastermindManager"
        , "LightLockManager"
        , "SpellManager"
        , "ManaManager"
        , "MagicVisionManager"
        , "SpinCirclesDependsPluginManager"
        , "BonusManager"
        , "BonusVideoManager"
        , "AchievementManager"
        , "Scenario"
        , "Macro"
    ]

    TraceManager.addTraces(traceList)

    from HOPA.ItemManager import ItemManager

    def __findInventoryItem(name):
        if ItemManager.hasItem(name) is False:
            return None
            pass

        if ItemManager.hasItemObject(name) is False:
            return None
            pass

        obj = ItemManager.getItemObject(name)

        return obj
        pass

    from HOPA.FanItemManager import FanItemManager
    from HOPA.MacroManager import MacroManager

    MacroManager.addFinder("InventoryItem", __findInventoryItem)

    def __findFanItem(name):
        if FanItemManager.hasItem(name) is False:
            return None
            pass

        if FanItemManager.hasItemObject(name) is False:
            return None
            pass

        obj = FanItemManager.getItemObject(name)

        return obj
        pass

    MacroManager.addFinder("FanItem", __findFanItem)

    from HOPA.HintManager import HintManager

    hintActions = [
        "HintActionDummy"
        , "HintActionCombine"
        , "HintActionHOGItem"
        , "HintActionItem"
        , "HintActionUseInventoryItem"
        , "HintActionUseHOGFittingItem"
        , "HintActionItemUseFittingInventoryItem"
        , "HintActionSocketUseFittingInventoryItem"
        , "HintActionClick"
        , "HintActionHOG"
        , "HintActionFan"
        , "HintActionTransition"
        , "HintActionTransitionBack"
        , "HintActionTransitionBackMobile"
        , "HintActionZoom"
        , "HintActionZoomOut"
        , "HintActionPull"
        , "HintActionDragDropItem"
        , "HintActionBoneUse"
        , "HintActionBoneAdd"
        , "HintActionSpellUse"
        , "HintActionEnvSpellUse"
        , "HintActionGiveItemOr"
        , "HintActionFindHiddenItem"
        , "HintActionFindMana"
        , "HintActionMagicVisionUse"
        , "HintActionUsePet"
        , "HintActionShiftCollect"
        , "HintActionMahjong"
        , "HintActionMagicGlove"
        , 'HintActionItemCollect'
        , 'HintActionItemCollectOpen'
        , 'HintActionCollectibleItem'
        , 'HintActionSpellAmuletUsePower'
        , "HintActionElementalMagicUse"
        , "HintActionElementalMagicPick"
    ]

    HintManager.importHintActions("HOPA.HintActions", hintActions)

    from HOPA.CruiseControlManager import CruiseControlManager

    cruiseActions = [
        "CruiseActionDummy"
        , "CruiseActionCombine"
        , "CruiseActionHOGItem"
        , "CruiseActionItem"
        , "CruiseActionItemWithItemPopup"
        , "CruiseActionUseInventoryItem"
        , "CruiseActionItemUseFittingInventoryItem"
        , "CruiseActionUseHOGFittingItem"
        , "CruiseActionClick"
        , "CruiseActionHOG"
        , "CruiseActionFan"
        , "CruiseActionTransition"
        , "CruiseActionTransitionBack"
        , "CruiseActionTransitionBackMobile"
        , "CruiseActionZoom"
        , "CruiseActionZoomOut"
        , "CruiseActionPull"
        , "CruiseActionDragDropItem"
        , "CruiseActionBoneUse"
        , "CruiseActionBoneAdd"
        , "CruiseActionSpellUse"
        , "CruiseActionGetItem"
        , "CruiseActionCutScene"
        , "CruiseActionDialog"
        , "CruiseActionEnigma"
        , "CruiseActionNewspaper"
        , "CruiseActionMessage"
        , "CruiseActionWait"
        , "CruiseActionGiveItemOr"
        , "CruiseActionPlusScene"
        , "CruiseActionPlusSceneOut"
        , "CruiseActionShiftCollect"
        , "CruiseActionItemCollect"
        , "CruiseActionHint"
        , "CruiseActionSpellAmuletUseRune"
        , "CruiseActionElementalMagicUse"
        , "CruiseActionElementalMagicPick"
    ]

    CruiseControlManager.importCruiseActions("HOPA.CruiseActions", cruiseActions)

    from HOPA.QuestIconManager import QuestIconManager

    questIconActions = [
        "QuestIconActionDefault"
        , "QuestIconActionObject"
        , "QuestIconActionSocket"
        , "QuestIconActionTransition"
        , "QuestIconActionZoom"
        , "QuestIconActionInteraction"
    ]

    QuestIconManager.importQuestIconActions("HOPA.QuestIconActions", questIconActions)

    from HOPA.SparksManager import SparksManager

    sparksActions = [
        "SparksActionClick"
        , "SparksActionItem"
        , "SparksActionUseInventoryItem"
        , "SparksActionItemUseInventoryItem"
        , "SparksActionTransition"
        , "SparksActionZoom"
        , "SparksActionHint"
    ]

    SparksManager.importSparksActions("HOPA.SparksActions", sparksActions)

    from HOPA.Entities.InventoryFX.InventoryFXManager import InventoryFXManager

    hintActions = [
        "ActionGetItem"
        , "ActionPickItem"
        , "ActionAddItem"
        , "ActionHintUse"
        , "ActionRemoveItem"
    ]

    InventoryFXManager.importActions("HOPA.Entities.InventoryFX", hintActions)

    from Foundation.EntityManager import EntityManager
    from Foundation.ObjectManager import ObjectManager
    Types = [
        "Item"
        , "MovieItem"
        , "Movie2Item"
        , "Zoom"
        , "Transition"
        , "TransitionBack"
        , "Enigma"
        , "EnigmaUndo"
        , "HOG"
        , "HOG2"
        , "HOGRolling"
        , "LampOnCursor"
        , "HOGFXPartsGathering"
        , "HOGSilhouette"
        , "Inventory"
        , "HOGInventory"
        , "HOGInventoryRolling"
        , "HOGInventorySilhouette"
        , "HOGInventoryFXPartsGathering"
        , "HOGInventoryImage"
        , "FittingInventory"
        , "InventoryItem"
        , "InventoryCountItem"
        , "InventoryCountItemFX"
        , "HOGInventoryCount"

        , "Objective"
        , "Objectives"
        , "Dialog"
        , "ItemPopUp"
        , "StaticPopUp"
        , "Mind"
        , "DialogBox"
        , "Hint"
        , "SurveyPhotoGallery"

        , "MagicGlove"

        , "RollingBalls"
        , "Chip"
        , "ColumnChain"
        , "PathChipsCrypt"
        , "ChessPuzzle"
        , "OrderMatches"
        , "PathChipsTransporter"
        , "ChainClick"
        , "Connectors"
        , "ColoringPuzzle"
        , "RotateAndSwapChips"
        , "FragmentsRoll"
        , "SwapDifferent"

        , "TrafficJam"
        , "NFS"
        , "Tip"
        , "TipItem"
        , "Fan"
        , "FanItem"
        , "BonusItem"
        , "CloseZoom"
        , "Map"
        , "Journal"
        , "Tab"
        , "LocationComplete"
        , "OverclickHook"
        , "SplashScreen"
        , "CutScene"
        , "WalktrhoughText"
        , "AssociationElements"
        , "Sparks"
        , "PuzzleInventory"
        , "SkipPuzzle"
        , "ResetPuzzle"
        , "Geks"
        , "PuzzleDragDrop"
        , "PuzzleRules"
        , "HOGClose"
        , "QuestIcon"
        , "SwitchChains"
        , "Newspaper"
        , "MenuGreeting"
        , "State"
        , "MenuHelp"
        , "Spot"
        , "Zuma"
        , "HogPenalty"
        , "SpinCircles"
        , "JoinBlocks"
        , "CirclePairElements"
        , "ThimbleGame"
        , "ColorCollect"
        , "PlanetGame"
        , "ZoomFrame"
        , "MetalDetector"
        , "ZenElements"
        , "PuzzleButtons"
        , "PuzzleInstructions"
        , "Pet"
        , "InstructionPullOut"
        , "FeedStates"
        , "BoneBoard"
        , "ShootingRange"
        , "MagicVision"
        , "Tutorial"
        , "ButtonConjunction"
        , "MagneticLabyrinth"
        , "CircularReflection"
        , "Programmator"

        , "DrawMagicSymbols"
        , "DrawMagicSymbolsFight"
        , "ClickOnTarget"  # todo: rename to ClickOnTargetWithFloatingCursor
        , "MoveChipsOnGraphNodes"
        , "AmazingMaze"
        , "Counterbalance"
        , "StonePyramids"
        , "FindSymbolsSetsMatchingCenter"
        , "CursorMaskFindInvisibleChip"
        , "RotateTilesWhichRotateEachOther"

        , "RubiksPuzzle"
        , "SwapChipsWithDifferentSlotTypes"
        , "SwapAndRotateMovieChips"
        , "ChainClickMovie"
        , "LeversPuzzle"
        , "MoviePathChipTransporter"
        , "SwitchWayDirectionPuzzle"
        , "ChipDragDropConnectPuzzle"
        , "RotateCirclesWithChips"
        , "SwapChipsSwitchEnableAndDisable"
        , "ClickOnChipsInTheRightOrder"
        , "MoveChipsToRightPlaces"
        , "SwapChipsInPlace"
        , "MoveCursorToRightPlaces"
        , "ClickOnChipsAndRotateArrow"
        , 'MoveChipToCells'
        , 'DragTheChainToTheRightPlace'
        , 'MoveChipsToKeyPoints'
        , 'ClickOnChipAndPlacesForActionOverPlace'
        , 'RotateRingsAndSetInRightOrder'
        , 'ChipDragDropOnRightPlace'
        , 'FindSimilarChipsForActivate'
        , 'ChipMoveCount'
        , 'ChipMoveAtom'
        , 'ProgrammatorForFindWayMG'
        , 'ChipsMoveOnMouseMove'
        , 'ChipsInNet'
        , 'MouseMagnet'
        , 'ItemCollect'
        , 'SwapAndRotateSegments'
        , 'ChipGravitySlider'
        , 'ChangeScreenOnClick'
        , 'MazeScreens'
        , "Credits"
        , "InventoryBase"

        , "BonusVideo"
        , "BonusPapers"
        , "BonusMusic"

        , "Collectibles"
        , "Achievements"
        , "AchievementsInGameMenu"
        , "ChapterSelection"
        , "MapBonusChapter"

        , "MahjongInventory"
        , "Hunt2d"
        , "FindingAndPlacingChipsOnMovie"

        , "TurnBasedStrategyGo"

        , "Guide"
        , "GuideOpen"

        , "SpellsUI"
        , "SpellAmulet"

        , "ForestMaze"
        , "AssemblyDesigner"

        , "SurveyBigFish"
        , "FreezeHOG"

        , "LanguageSelect"
        , "LoadingScene"
        , "AdvertisingScene"
        , "TrialMobile"

        , "GiftExchange"
        , "GameStore"
        , "DialogWindow"
        , "SpecialPromotion"
        , "LimitedPromo"

        , "BalanceIndicator"

        , "Store"
        , "StorePage"
        , "RestorePurchases"

        , "About"
        , "TechnicalSupport"
        , "ConsentFlow"

        , "ElementalMagic"
    ]

    if Mengine.getGameParamBool("NotUseDefaultEntitiesList", False) is True:
        Types = []
        from Foundation.DatabaseManager import DatabaseManager
        records = DatabaseManager.getDatabaseRecordsFilterBy("Database", "Entities", Module="HOPA")

        for record in records:
            Types.append(record.get("Type"))

    EntityManager.importEntities("HOPA.Entities", Types)
    ObjectManager.importObjects("HOPA.Object", Types)

    from HOPA.HOGManager import HOGManager
    Types = [
        "HOGParamDefault"
        , "HOGParamRolling"
        , "HOGParamRollingLikeDefault"
        , "HOGParamFXPartsGathering"
        , "HOGParamSilhouette"
        , "HOGParamDragDrop"
    ]

    from Foundation.MonetizationManager import MonetizationManager

    Components = [
        "Hint"
        , "SkipPuzzle"
        , "Guides"
        , "SpecialPackage"
        , "DisableAds"
        , "PaidBonusChapter"
        , "LimitedOffer"
        , "PromoPackageNotEnoughMoney"
        , "TriggerSpecialPacks"
        , "AdvertNotEnoughMoney"
    ]

    MonetizationManager.importComponents("HOPA.Entities.Monetization", Components)

    from Foundation.AccountManager import AccountManager

    def accountSetuper(accountID, isGlobal):
        if isGlobal is True:
            return

        Mengine.addCurrentAccountSetting("Default", u"False", None)

        def __onAccountChangeName(account_id, newName):
            Notification.notify(Notificator.onAccountChangeName, newName)

        Mengine.addCurrentAccountSetting("Name", u"", __onAccountChangeName)

        Mengine.addCurrentAccountSetting("SlotID", u"", None)

        def __changeDifficulty(account_id, value):
            Notification.notify(Notificator.onChangeDifficulty, value)

        def __changeDifficulty_Cursore(account_id, value):
            if value == "True":
                CursorManager.setBlockCursorUpdate(False)
            if value == "False":
                CursorManager.setBlockCursorUpdate(True)

        Mengine.addCurrentAccountSetting("Difficulty", u"Casual", __changeDifficulty)
        Mengine.addCurrentAccountSetting("DifficultyCustomHintTime", u'1.0', None)
        Mengine.addCurrentAccountSetting("DifficultyCustomSkipTime", u'1.0', None)
        Mengine.addCurrentAccountSetting("DifficultyCustomTutorial", u'True', None)
        Mengine.addCurrentAccountSetting('DifficultyCustomSparklesOnActiveAreas', u'True', None)
        Mengine.addCurrentAccountSetting('DifficultyCustomSparklesOnHOPuzzles', u'True', None)
        Mengine.addCurrentAccountSetting('DifficultyCustomPlusItemIndicated', u'True', None)
        Mengine.addCurrentAccountSetting('DifficultyCustomIndicatorsOnMap', u'True', None)
        Mengine.addCurrentAccountSetting('DifficultyCustomChangeIconOnActiveAreas', u'True', __changeDifficulty_Cursore)

        Mengine.addCurrentAccountSetting("SurveyComplete", u"False", None)
        Mengine.addCurrentAccountSetting("GameComplete", u"False", None)
        Mengine.addCurrentAccountSetting("IsBonusChapter", u"0", None)

        def __changeMute(account_id, value):
            Mute = value == "True"
            Mengine.soundMute(Mute)
            Notification.notify(Notificator.onMute, Mute)

        Mute = Mengine.isMute()
        Mengine.addCurrentAccountSetting("Mute", unicode(Mute), __changeMute)

        def __changeCursor(account_id, value):
            Cursor = value == u"True"
            if Cursor == Mengine.getCursorMode():
                return
            Mengine.setCursorMode(Cursor)

        Cursor = Mengine.getCursorMode()

        Mengine.addCurrentAccountSetting("Cursor", unicode(Cursor), __changeCursor)

        def __changeCustomCursor(account_id, value):
            is_custom_cursor = value == u"True"
            Notification.notify(Notificator.onCustomCursor, is_custom_cursor)

        Mengine.addCurrentAccountSetting("CustomCursor", u"True", __changeCustomCursor)

        def __changeFullscreen(account_id, value):
            Fullscreen = value == u"True"
            if Fullscreen == Mengine.getFullscreenMode():
                return
            Mengine.setFullscreenMode(Fullscreen)

        Fullscreen = Mengine.getFullscreenMode()

        Mengine.addCurrentAccountSetting("Fullscreen", unicode(Fullscreen), __changeFullscreen)

        def __changeWidescreen(account_id, value):
            Widescreen = value == u"True"

            if Widescreen == Mengine.getFixedDisplayResolution():
                return

            Mengine.setFixedDisplayResolution(Widescreen)

        Widescreen = Mengine.getGameParamBool("Widescreen", Mengine.getFixedDisplayResolution())
        Mengine.addCurrentAccountSetting("Widescreen", unicode(Widescreen), __changeWidescreen)

        # - sound ---------------------------------------------------------
        def __changeVoiceVolume(account_id, value):
            volume = float(value)
            Mengine.voiceSetVolume(volume)

        VoiceVolume = Mengine.voiceGetVolume()
        Mengine.addCurrentAccountSetting("VoiceVolume", unicode(VoiceVolume), __changeVoiceVolume)

        def __changeMusicVolume(account_id, value):
            volume = float(value)
            Mengine.musicSetVolume(volume)
            pass

        MusicVolume = Mengine.musicGetVolume()
        Mengine.addCurrentAccountSetting("MusicVolume", unicode(MusicVolume), __changeMusicVolume)

        def __changeSoundVolume(account_id, value):
            volume = float(value)
            Mengine.soundSetVolume(volume)

        SoundVolume = Mengine.soundGetVolume()
        Mengine.addCurrentAccountSetting("SoundVolume", unicode(SoundVolume), __changeSoundVolume)

        # -----------------------------------------------------------------

        def __changeChapters(account_id, value):
            Chapters = int(value)
            Notification.notify(Notificator.onChapters, Chapters)

        Chapters = 0
        Mengine.addCurrentAccountSetting("Chapters", unicode(Chapters), __changeChapters)

        Mengine.addCurrentAccountSetting("Save", unicode(False), None)
        Mengine.addCurrentAccountSetting("SessionSave", unicode(False), None)

    AccountManager.setCreateAccount(accountSetuper)

    HOGManager.importParamTypes("HOPA", Types)

    EntityManager.importEntity("HOPA.Entities", "DebugMenu")
    ObjectManager.importObject("HOPA.Entities.DebugMenu", "DebugMenu")

    ObjectManager.importObject("HOPA.Entities.Awards", "Awards")
    EntityManager.importEntity("HOPA.Entities", "Awards")

    EntityManager.importEntity("HOPA.Entities", "GUI")
    ObjectManager.importObject("HOPA.Entities.GUI", "GUI")

    EntityManager.importEntity("HOPA.Entities", "Toolbar")
    ObjectManager.importObject("HOPA.Entities.Toolbar", "Toolbar")

    EntityManager.importEntity("HOPA.Entities", "Navigation")
    ObjectManager.importObject("HOPA.Entities.Navigation", "Navigation")

    EntityManager.importEntity("HOPA.Entities.StrategyGuide", "StrategyGuideMenu")
    ObjectManager.importObject("HOPA.Entities.StrategyGuide.StrategyGuideMenu", "StrategyGuideMenu")

    EntityManager.importEntity("HOPA.Entities.StrategyGuide", "StrategyGuideZoom")
    ObjectManager.importObject("HOPA.Entities.StrategyGuide.StrategyGuideZoom", "StrategyGuideZoom")

    EntityManager.importEntity("HOPA.Entities.StrategyGuide", "StrategyGuidePage")
    ObjectManager.importObject("HOPA.Entities.StrategyGuide.StrategyGuidePage", "StrategyGuidePage")

    EntityManager.importEntity("HOPA.Entities.StrategyGuide", "StrategyGuideController")
    ObjectManager.importObject("HOPA.Entities.StrategyGuide.StrategyGuideController", "StrategyGuideController")

    EntityManager.importEntity("HOPA.Entities", "Notebook")
    EntityManager.importEntity("HOPA.Entities", "NotebookInventory")
    EntityManager.importEntity("HOPA.Entities", "NotebookInventoryList")
    EntityManager.importEntity("HOPA.Entities", "NotebookDescription")
    EntityManager.importEntity("HOPA.Entities", "SpinCirclesMastermind")
    EntityManager.importEntity("HOPA.Entities", "SpinCirclesDependsPlugin")
    ObjectManager.importObject("HOPA.Entities.Notebook", "Notebook")
    ObjectManager.importObject("HOPA.Entities.NotebookInventory", "NotebookInventory")
    ObjectManager.importObject("HOPA.Entities.NotebookInventoryList", "NotebookInventoryList")
    ObjectManager.importObject("HOPA.Entities.NotebookDescription", "NotebookDescription")
    ObjectManager.importObject("HOPA.Entities.SpinCirclesMastermind", "SpinCirclesMastermind")
    ObjectManager.importObject("HOPA.Entities.SpinCirclesDependsPlugin", "SpinCirclesDependsPlugin")

    ObjectManager.importObject("HOPA.Entities.Difficulty", "Difficulty")
    EntityManager.importEntity("HOPA.Entities", "Difficulty")

    ObjectManager.importObject("HOPA.Entities.Difficulty2", "Difficulty2")
    EntityManager.importEntity("HOPA.Entities", "Difficulty2")

    EntityManager.importEntity("HOPA.Entities", "Plumber")
    ObjectManager.importObject("HOPA.Entities.Plumber", "Plumber")

    EntityManager.importEntity("HOPA.Entities", "MoveBlocks")
    ObjectManager.importObject("HOPA.Entities.MoveBlocks", "MoveBlocks")

    EntityManager.importEntity("HOPA.Entities", "RotateAndReflectElement")
    ObjectManager.importObject("HOPA.Entities.RotateAndReflectElement", "RotateAndReflectElement")

    EntityManager.importEntity("HOPA.Entities", "AssociationElements2")
    ObjectManager.importObject("HOPA.Entities.AssociationElements2", "AssociationElements2")

    EntityManager.importEntity("HOPA.Entities", "LetItSlide")
    ObjectManager.importObject("HOPA.Entities.LetItSlide", "LetItSlide")

    EntityManager.importEntity("HOPA.Entities", "InventoryItemAccumulate")
    ObjectManager.importObject("HOPA.Entities.InventoryItemAccumulate", "InventoryItemAccumulate")

    EntityManager.importEntity("HOPA.Entities", "Spell")
    ObjectManager.importObject("HOPA.Entities.Spell", "Spell")

    EntityManager.importEntity("HOPA.Entities", "Map2")
    ObjectManager.importObject("HOPA.Entities.Map2", "Map2")

    EntityManager.importEntity("HOPA.Entities.Map2", "OpenMap")
    ObjectManager.importObject("HOPA.Entities.Map2.OpenMap", "OpenMap")

    EntityManager.importEntity("HOPA.Entities", "OpenJournal")
    ObjectManager.importObject("HOPA.Entities.OpenJournal", "OpenJournal")

    EntityManager.importEntity("HOPA.Entities.Map2", "MapSwitch")
    ObjectManager.importObject("HOPA.Entities.Map2.MapSwitch", "MapSwitch")

    EntityManager.importEntity("HOPA.Entities.Map2", "CollectedMap")
    ObjectManager.importObject("HOPA.Entities.Map2.CollectedMap", "CollectedMap")

    EntityManager.importEntity("HOPA.Entities", "Journal2")
    ObjectManager.importObject("HOPA.Entities.Journal2", "Journal2")

    EntityManager.importEntity("HOPA.Entities.Map2", "CollectedMapIndicator")
    ObjectManager.importObject("HOPA.Entities.Map2.CollectedMapIndicator", "CollectedMapIndicator")

    EntityManager.importEntity("HOPA.Entities", "CloseDiary")
    ObjectManager.importObject("HOPA.Entities.CloseDiary", "CloseDiary")

    EntityManager.importEntity("HOPA.Entities", "Extras")
    ObjectManager.importObject("HOPA.Entities.Extras", "Extras")

    EntityManager.importEntity("HOPA.Entities.Extras", "ExtrasConcept")
    ObjectManager.importObject("HOPA.Entities.Extras.ExtrasConcept", "ExtrasConcept")

    EntityManager.importEntity("HOPA.Entities.Extras", "ExtrasWallpaper")
    ObjectManager.importObject("HOPA.Entities.Extras.ExtrasWallpaper", "ExtrasWallpaper")

    EntityManager.importEntity("HOPA.Entities.Extras", "ExtrasEnigma")
    ObjectManager.importObject("HOPA.Entities.Extras.ExtrasEnigma", "ExtrasEnigma")

    EntityManager.importEntity("HOPA.Entities.Extras", "ExtrasMusic")
    ObjectManager.importObject("HOPA.Entities.Extras.ExtrasMusic", "ExtrasMusic")

    EntityManager.importEntity("HOPA.Entities.Extras", "ExtrasHOG")
    ObjectManager.importObject("HOPA.Entities.Extras.ExtrasHOG", "ExtrasHOG")

    EntityManager.importEntity("HOPA.Entities", "LightLock")
    ObjectManager.importObject("HOPA.Entities.LightLock", "LightLock")

    EntityManager.importEntity("HOPA.Entities", "Mana")
    ObjectManager.importObject("HOPA.Entities.Mana", "Mana")

    EntityManager.importEntity("HOPA.Entities", "Reagents")
    ObjectManager.importObject("HOPA.Entities.Reagents", "Reagents")

    EntityManager.importEntity("HOPA.Entities.Reagents", "ReagentsEnigma")
    ObjectManager.importObject("HOPA.Entities.Reagents.ReagentsEnigma", "ReagentsEnigma")

    EntityManager.importEntity("HOPA.Entities.Reagents", "ReagentsButton")
    ObjectManager.importObject("HOPA.Entities.Reagents.ReagentsButton", "ReagentsButton")
    TaskManager.importTask("HOPA.Entities.Reagents.Macro", "AliasPickReagentPaper")

    ObjectManager.importObject("HOPA.Entities.ProfileNew", "ProfileNew")
    EntityManager.importEntity("HOPA.Entities", "ProfileNew")
    ObjectManager.importObject("HOPA.Entities.Puzzle", "Puzzle")
    EntityManager.importEntity("HOPA.Entities", "Puzzle")

    ObjectManager.importObject("HOPA.Entities.Profile", "Profile")
    EntityManager.importEntity("HOPA.Entities", "Profile")

    ObjectManager.importObject("HOPA.Entities.HOGFitting", "HOGFitting")
    EntityManager.importEntity("HOPA.Entities", "HOGFitting")

    ObjectManager.importObject("HOPA.Entities.HOGInventoryFitting", "HOGInventoryFitting")
    EntityManager.importEntity("HOPA.Entities", "HOGInventoryFitting")

    ObjectManager.importObject("HOPA.Entities.InventoryFX", "InventoryFX")
    EntityManager.importEntity("HOPA.Entities", "InventoryFX")
    InvFXTasks = ["TaskInventoryFXAddItem", ]
    TaskManager.importTasks("HOPA.Entities.InventoryFX", InvFXTasks)

    ObjectManager.importObject("HOPA.Entities.CombatSpell", "CombatSpell")
    EntityManager.importEntity("HOPA.Entities", "CombatSpell")

    ObjectManager.importObject("HOPA.Entities.LightCircleGame", "LightCircleGame")
    EntityManager.importEntity("HOPA.Entities", "LightCircleGame")

    ObjectManager.importObject("HOPA.Entities.PaperConnectGame", "PaperConnectGame")
    EntityManager.importEntity("HOPA.Entities", "PaperConnectGame")

    ObjectManager.importObject("HOPA.Entities.ZoomAfterFrame", "ZoomAfterFrame")
    EntityManager.importEntity("HOPA.Entities", "ZoomAfterFrame")

    ObjectManager.importObject("HOPA.Entities.GlobeGame", "GlobeGame")
    EntityManager.importEntity("HOPA.Entities", "GlobeGame")

    ObjectManager.importObject("HOPA.Entities.HanoisTower", "HanoisTower")
    EntityManager.importEntity("HOPA.Entities", "HanoisTower")

    ObjectManager.importObject("HOPA.Entities.PatchesGame", "PatchesGame")
    EntityManager.importEntity("HOPA.Entities", "PatchesGame")

    ObjectManager.importObject("HOPA.Entities.PetnaGame", "PetnaGame")
    EntityManager.importEntity("HOPA.Entities", "PetnaGame")

    ObjectManager.importObject("HOPA.Entities.RailRoadGame", "RailRoadGame")
    EntityManager.importEntity("HOPA.Entities", "RailRoadGame")

    ObjectManager.importObject("HOPA.Entities.CollectedAmulet", "CollectedAmulet")
    EntityManager.importEntity("HOPA.Entities", "CollectedAmulet")

    ObjectManager.importObject("HOPA.Entities.ShootGame", "ShootGame")
    EntityManager.importEntity("HOPA.Entities", "ShootGame")

    ObjectManager.importObject("HOPA.Entities.Sandglass", "Sandglass")
    EntityManager.importEntity("HOPA.Entities", "Sandglass")

    ObjectManager.importObject("HOPA.Entities.ConnectLamp", "ConnectLamp")
    EntityManager.importEntity("HOPA.Entities", "ConnectLamp")

    ObjectManager.importObject("HOPA.Entities.ChekersCR", "ChekersCR")
    EntityManager.importEntity("HOPA.Entities", "ChekersCR")

    ObjectManager.importObject("HOPA.Entities.ClickSequence", "ClickSequence")
    EntityManager.importEntity("HOPA.Entities", "ClickSequence")

    ObjectManager.importObject("HOPA.Entities.SwapGame", "SwapGame")
    EntityManager.importEntity("HOPA.Entities", "SwapGame")

    ObjectManager.importObject("HOPA.Entities.SameElements", "SameElements")
    EntityManager.importEntity("HOPA.Entities", "SameElements")

    ObjectManager.importObject("HOPA.Entities.Mahjong", "Mahjong")
    EntityManager.importEntity("HOPA.Entities", "Mahjong")

    ObjectManager.importObject("HOPA.Entities.Isometric", "Isometric")
    EntityManager.importEntity("HOPA.Entities", "Isometric")

    ObjectManager.importObject("HOPA.Entities.Options", "Options")
    EntityManager.importEntity("HOPA.Entities", "Options")

    ObjectManager.importObject("HOPA.Entities.OptionsMore", "OptionsMore")
    EntityManager.importEntity("HOPA.Entities", "OptionsMore")

    ObjectManager.importObject("HOPA.Entities.Reloader", "Reloader")
    EntityManager.importEntity("HOPA.Entities", "Reloader")

    ObjectManager.importObject("HOPA.Entities.InGameMenu", "InGameMenu")
    EntityManager.importEntity("HOPA.Entities", "InGameMenu")

    from HOPA.CursorManager import CursorManager
    CursorManager.onInitialize()

    from HOPA.ScenarioManager import ScenarioManager
    ScenarioManager.onInitialize()

    from HOPA.QuestManager import QuestManager
    QuestManager.onInitialize()

    from HOPA.TransitionManager import TransitionManager
    TransitionManager.onInitialize()

    from HOPA.ZoomManager import ZoomManager
    ZoomManager.onInitialize()

    from HOPA.HOGManager import HOGManager
    HOGManager.onInitialize()

    from HOPA.ChapterManager import ChapterManager
    ChapterManager.onInitialize()

    return True
    pass


def onFinalize():
    from Foundation.Utils import isSurvey
    if isSurvey():
        survey_url = Mengine.getGameParamUnicode("SurveyUrl")
        if Mengine.getGameParamBool("SurveyLink", False) is True:
            Mengine.openUrlInDefaultBrowser(survey_url)

    from HOPA.CursorManager import CursorManager
    CursorManager.onFinalize()

    from HOPA.TransitionManager import TransitionManager
    TransitionManager.onFinalize()

    from HOPA.ZoomManager import ZoomManager
    ZoomManager.onFinalize()

    from HOPA.ChapterManager import ChapterManager
    ChapterManager.onFinalize()

    from HOPA.PopUpItemManager import PopUpItemManager
    PopUpItemManager.onFinalize()

    from HOPA.BonusItemManager import BonusItemManager
    BonusItemManager.onFinalize()

    from HOPA.HOGManager import HOGManager
    HOGManager.onFinalize()

    from HOPA.InventoryItemUseMovieManager import InventoryItemUseMovieManager
    InventoryItemUseMovieManager.onFinalize()

    from HOPA.StaticPopUpManager import StaticPopUpManager
    StaticPopUpManager.onFinalize()

    from HOPA.HintManager import HintManager
    HintManager.onFinalize()

    from HOPA.ScenarioManager import ScenarioManager
    ScenarioManager.onFinalize()

    from HOPA.QuestManager import QuestManager
    QuestManager.onFinalize()

    from HOPA.MacroManager import MacroManager
    MacroManager.onFinalize()
