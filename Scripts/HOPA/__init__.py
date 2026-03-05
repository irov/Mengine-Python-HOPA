def onInitialize():
    Trace.msg_dev("HOPA.onInitialize")

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
        , "PolicyAliasTransitionNormal"
        , "PolicyAliasTransitionAdvertising"
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

        , "onAdvertDisplayed"
        , "onAdvertRewarded"
        , "onAdvertHidden"
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

        if ItemManager.hasItemObject(name) is False:
            return None

        obj = ItemManager.getItemObject(name)

        return obj

    from HOPA.FanItemManager import FanItemManager
    from HOPA.MacroManager import MacroManager

    MacroManager.addFinder("InventoryItem", __findInventoryItem)

    def __findFanItem(name):
        if FanItemManager.hasItem(name) is False:
            return None

        if FanItemManager.hasItemObject(name) is False:
            return None

        obj = FanItemManager.getItemObject(name)

        return obj

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

    EntityTypes = [
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

        , "DebugMenu"
        , "Awards"
        , "Toolbar"
        , "Navigation"
        , "StrategyGuide"
        , "Notebook"
        , "NotebookInventory"
        , "NotebookInventoryList"
        , "NotebookDescription"
        , "SpinCirclesMastermind"
        , "SpinCirclesDependsPlugin"
        , "Difficulty"
        , "Difficulty2"
        , "Plumber"
        , "MoveBlocks"
        , "RotateAndReflectElement"
        , "AssociationElements2"
        , "LetItSlide"
        , "InventoryItemAccumulate"
        , "Spell"
        , "Map2"
        , "OpenJournal"
        , "Journal2"
        , "CloseDiary"
        , "Extras"
        , "LightLock"
        , "Mana"
        , "Reagents"
        , "ProfileNew"
        , "Puzzle"
        , "Profile"
        , "HOGFitting"
        , "HOGInventoryFitting"
        , "InventoryFX"
        , "CombatSpell"
        , "LightCircleGame"
        , "PaperConnectGame"
        , "ZoomAfterFrame"
        , "GlobeGame"
        , "HanoisTower"
        , "PatchesGame"
        , "PetnaGame"
        , "RailRoadGame"
        , "CollectedAmulet"
        , "ShootGame"
        , "Sandglass"
        , "ConnectLamp"
        , "ChekersCR"
        , "ClickSequence"
        , "SwapGame"
        , "SameElements"
        , "Mahjong"
        , "Isometric"
        , "Options"
        , "OptionsMore"
        , "Reloader"
        , "InGameMenu"
    ]

    from Foundation.Bootstrapper import Bootstrapper
    if Bootstrapper.loadEntities("HOPA", EntityTypes) is False:
        return False

    from HOPA.HOGManager import HOGManager

    HOGTypes = [
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

        def __onAccountChangeName(account_id, newName):
            Notification.notify(Notificator.onAccountChangeName, newName)

        Mengine.addCurrentAccountSetting("Name", u"Player", __onAccountChangeName)

        Mengine.addCurrentAccountSetting("SlotID", u"", None)

        def __changeDifficulty(account_id, value):
            Notification.notify(Notificator.onChangeDifficulty, value)

        def __changeDifficulty_Cursore(account_id, value):
            from HOPA.CursorManager import CursorManager

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

        # -----------------------------------------------------------------

        def __changeChapters(account_id, value):
            Chapters = int(value)
            Notification.notify(Notificator.onChapters, Chapters)

        Chapters = 0
        Mengine.addCurrentAccountSetting("Chapters", unicode(Chapters), __changeChapters)

    AccountManager.addCreateAccountExtra(accountSetuper)

    HOGManager.importParamTypes("HOPA", HOGTypes)

    from Foundation.Managers import Managers

    Managers.importManager("HOPA", "AchievementManager")
    Managers.importManager("HOPA", "AssemblyDesignerManager")
    Managers.importManager("HOPA", "CruiseControlManager")
    Managers.importManager("HOPA", "CursorManager")
    Managers.importManager("HOPA", "CutSceneManager")
    Managers.importManager("HOPA", "DialogManager")
    Managers.importManager("HOPA", "DialogWindowManager")
    Managers.importManager("HOPA", "DrawMagicSymbolsManager")
    Managers.importManager("HOPA", "EnigmaManager")
    Managers.importManager("HOPA", "ForestMazeManager")
    Managers.importManager("HOPA", "HOGFittingItemManager")
    Managers.importManager("HOPA", "InventoryPanelManager")
    Managers.importManager("HOPA", "ItemManager")
    Managers.importManager("HOPA", "LanguageSelectManager")
    Managers.importManager("HOPA", "MacroManager")
    Managers.importManager("HOPA", "MindBranchManager")
    Managers.importManager("HOPA", "MindManager")
    Managers.importManager("HOPA", "MonetizationManager")
    Managers.importManager("HOPA", "MusicManager")
    Managers.importManager("HOPA", "NewspaperManager")
    Managers.importManager("HOPA", "PopUpItemManager")
    Managers.importManager("HOPA", "QuestManager")
    Managers.importManager("HOPA", "RotateTilesWhichRotateEachOtherManager")
    Managers.importManager("HOPA", "RubiksPuzzleManager")
    Managers.importManager("HOPA", "ScenarioManager")
    Managers.importManager("HOPA", "SoundEffectManager")
    Managers.importManager("HOPA", "SoundEffectOnObjectManager")
    Managers.importManager("HOPA", "SparksManager")
    Managers.importManager("HOPA", "StageManager")
    Managers.importManager("HOPA", "StoreManager")
    Managers.importManager("HOPA", "TipManager")
    Managers.importManager("HOPA", "TransitionManager")
    Managers.importManager("HOPA", "TransitionHighlightManager")
    Managers.importManager("HOPA", "TooltipsManager")
    Managers.importManager("HOPA", "ZoomManager")
    Managers.importManager("HOPA", "ChapterManager")
    Managers.importManager("HOPA", "BonusItemManager")
    Managers.importManager("HOPA", "HOGManager")
    Managers.importManager("HOPA", "InventoryItemUseMovieManager")
    Managers.importManager("HOPA", "StaticPopUpManager")
    Managers.importManager("HOPA", "HintManager")
    Managers.importManager("HOPA", "ArrowBlackListManager")

    Managers.importManager("HOPA.Entities.AssociationElements2", "AssociationElements2Manager")
    Managers.importManager("HOPA.Entities.Awards", "AwardsManager")
    Managers.importManager("HOPA.Entities.BoneBoard", "BoneBoardManager")
    Managers.importManager("HOPA.Entities.BoneBoard", "BoneHelpChainManager")
    Managers.importManager("HOPA.Entities.ButtonConjunction", "ButtonConjunctionManager")
    Managers.importManager("HOPA.Entities.CircularReflection", "CircularReflectionManager")
    Managers.importManager("HOPA.Entities.CollectedAmulet", "CollectedAmuletManager")
    Managers.importManager("HOPA.Entities.Difficulty", "DifficultyManager")
    Managers.importManager("HOPA.Entities.Difficulty2", "Difficulty2Manager")
    Managers.importManager("HOPA.Entities.Extras", "ExtrasManager")
    Managers.importManager("HOPA.Entities.Extras.ExtrasConcept", "ExtrasConceptManager")
    Managers.importManager("HOPA.Entities.Extras.ExtrasEnigma", "ExtrasEnigmaManager")
    Managers.importManager("HOPA.Entities.Extras.ExtrasHOG", "ExtrasHOGManager")
    Managers.importManager("HOPA.Entities.Extras.ExtrasMusic", "ExtrasMusicManager")
    Managers.importManager("HOPA.Entities.Extras.ExtrasWallpaper", "ExtrasWallpaperManager")
    Managers.importManager("HOPA.Entities.InventoryFX", "InventoryFXManager")
    Managers.importManager("HOPA.Entities.Journal2", "Journal2Manager")
    Managers.importManager("HOPA.Entities.LetItSlide", "LetItSlideManager")
    Managers.importManager("HOPA.Entities.LightLock", "LightLockManager")
    Managers.importManager("HOPA.Entities.MagicVision", "MagicVisionManager")
    Managers.importManager("HOPA.Entities.MagneticLabyrinth", "MagneticLabyrinthManager")
    Managers.importManager("HOPA.Entities.Mana", "ManaManager")
    Managers.importManager("HOPA.Entities.Map2", "Map2Manager")
    Managers.importManager("HOPA.Entities.Map2.CollectedMap", "CollectedMapManager")
    Managers.importManager("HOPA.Entities.Map2.CollectedMapIndicator", "CollectedMapIndicatorManager")
    Managers.importManager("HOPA.Entities.Map2.MapSwitch", "MapSwitchManager")
    Managers.importManager("HOPA.Entities.MoveBlocks", "MoveBlocksManager")
    Managers.importManager("HOPA.Entities.Notebook", "NotebookManager")
    Managers.importManager("HOPA.Entities.NotebookDescription", "NotebookDescriptionManager")
    Managers.importManager("HOPA.Entities.NotebookInventory", "NotebookInventoryManager")
    Managers.importManager("HOPA.Entities.NotebookInventoryList", "NotebookInventoryListManager")
    Managers.importManager("HOPA.Entities.OpenJournal", "OpenJournalManager")
    Managers.importManager("HOPA.Entities.Options", "OptionsManager")
    Managers.importManager("HOPA.Entities.OptionsMore", "OptionsMoreManager")
    Managers.importManager("HOPA.Entities.Plumber", "PlumberManager")
    Managers.importManager("HOPA.Entities.Profile", "ProfileManager")
    Managers.importManager("HOPA.Entities.Programmator", "ProgrammatorManager")
    Managers.importManager("HOPA.Entities.Puzzle", "PuzzleManager")
    Managers.importManager("HOPA.Entities.Reagents", "ReagentsManager")
    Managers.importManager("HOPA.Entities.RotateAndReflectElement", "RotateAndReflectElementManager")
    Managers.importManager("HOPA.Entities.SameElements", "SameElementsManager")
    Managers.importManager("HOPA.Entities.Spell", "SpellManager")
    Managers.importManager("HOPA.Entities.SpinCirclesDependsPlugin", "SpinCirclesDependsPluginManager")
    Managers.importManager("HOPA.Entities.SpinCirclesMastermind", "SpinCirclesMastermindManager")
    Managers.importManager("HOPA.Entities.SplashScreen", "SplashScreenManager")
    Managers.importManager("HOPA.Entities.StrategyGuide.StrategyGuideController", "StrategyGuideControllerManager")
    Managers.importManager("HOPA.Entities.StrategyGuide.StrategyGuideMenu", "StrategyGuideMenuManager")
    Managers.importManager("HOPA.Entities.StrategyGuide.StrategyGuidePage", "StrategyGuidePageManager")
    Managers.importManager("HOPA.Entities.StrategyGuide.StrategyGuideZoom", "StrategyGuideZoomManager")

    Managers.importManager("HOPA.Entities.Mahjong", "MahjongManager")

    return True

def onFinalize():
    Trace.msg_dev("HOPA.onFinalize")

    from Foundation.Utils import isSurvey

    if isSurvey():
        survey_url = Mengine.getGameParamUnicode("SurveyUrl")
        if Mengine.getGameParamBool("SurveyLink", False) is True:
            Mengine.openUrlInDefaultBrowser(survey_url)

    from Foundation.Managers import Managers

    Managers.removeManager("HOPA", "AchievementManager")
    Managers.removeManager("HOPA", "AssemblyDesignerManager")
    Managers.removeManager("HOPA", "CruiseControlManager")
    Managers.removeManager("HOPA", "CursorManager")
    Managers.removeManager("HOPA", "CutSceneManager")
    Managers.removeManager("HOPA", "DialogManager")
    Managers.removeManager("HOPA", "DialogWindowManager")
    Managers.removeManager("HOPA", "DrawMagicSymbolsManager")
    Managers.removeManager("HOPA", "EnigmaManager")
    Managers.removeManager("HOPA", "ForestMazeManager")
    Managers.removeManager("HOPA", "HOGFittingItemManager")
    Managers.removeManager("HOPA", "InventoryPanelManager")
    Managers.removeManager("HOPA", "ItemManager")
    Managers.removeManager("HOPA", "LanguageSelectManager")
    Managers.removeManager("HOPA", "MacroManager")
    Managers.removeManager("HOPA", "MindBranchManager")
    Managers.removeManager("HOPA", "MindManager")
    Managers.removeManager("HOPA", "MonetizationManager")
    Managers.removeManager("HOPA", "MusicManager")
    Managers.removeManager("HOPA", "NewspaperManager")
    Managers.removeManager("HOPA", "PopUpItemManager")
    Managers.removeManager("HOPA", "QuestManager")
    Managers.removeManager("HOPA", "RotateTilesWhichRotateEachOtherManager")
    Managers.removeManager("HOPA", "RubiksPuzzleManager")
    Managers.removeManager("HOPA", "ScenarioManager")
    Managers.removeManager("HOPA", "SoundEffectManager")
    Managers.removeManager("HOPA", "SoundEffectOnObjectManager")
    Managers.removeManager("HOPA", "SparksManager")
    Managers.removeManager("HOPA", "StageManager")
    Managers.removeManager("HOPA", "StoreManager")
    Managers.removeManager("HOPA", "TipManager")
    Managers.removeManager("HOPA", "TransitionManager")
    Managers.removeManager("HOPA", "TransitionHighlightManager")
    Managers.removeManager("HOPA", "TooltipsManager")
    Managers.removeManager("HOPA", "ZoomManager")
    Managers.removeManager("HOPA", "ChapterManager")
    Managers.removeManager("HOPA", "BonusItemManager")
    Managers.removeManager("HOPA", "HOGManager")
    Managers.removeManager("HOPA", "InventoryItemUseMovieManager")
    Managers.removeManager("HOPA", "StaticPopUpManager")
    Managers.removeManager("HOPA", "HintManager")
    Managers.removeManager("HOPA", "ArrowBlackListManager")

    Managers.removeManager("HOPA.Entities.AssociationElements2", "AssociationElements2Manager")
    Managers.removeManager("HOPA.Entities.Awards", "AwardsManager")
    Managers.removeManager("HOPA.Entities.BoneBoard", "BoneBoardManager")
    Managers.removeManager("HOPA.Entities.BoneBoard", "BoneHelpChainManager")
    Managers.removeManager("HOPA.Entities.ButtonConjunction", "ButtonConjunctionManager")
    Managers.removeManager("HOPA.Entities.CircularReflection", "CircularReflectionManager")
    Managers.removeManager("HOPA.Entities.CollectedAmulet", "CollectedAmuletManager")
    Managers.removeManager("HOPA.Entities.Difficulty", "DifficultyManager")
    Managers.removeManager("HOPA.Entities.Difficulty2", "Difficulty2Manager")
    Managers.removeManager("HOPA.Entities.Extras", "ExtrasManager")
    Managers.removeManager("HOPA.Entities.Extras.ExtrasConcept", "ExtrasConceptManager")
    Managers.removeManager("HOPA.Entities.Extras.ExtrasEnigma", "ExtrasEnigmaManager")
    Managers.removeManager("HOPA.Entities.Extras.ExtrasHOG", "ExtrasHOGManager")
    Managers.removeManager("HOPA.Entities.Extras.ExtrasMusic", "ExtrasMusicManager")
    Managers.removeManager("HOPA.Entities.Extras.ExtrasWallpaper", "ExtrasWallpaperManager")
    Managers.removeManager("HOPA.Entities.InventoryFX", "InventoryFXManager")
    Managers.removeManager("HOPA.Entities.Journal2", "Journal2Manager")
    Managers.removeManager("HOPA.Entities.LetItSlide", "LetItSlideManager")
    Managers.removeManager("HOPA.Entities.LightLock", "LightLockManager")
    Managers.removeManager("HOPA.Entities.MagicVision", "MagicVisionManager")
    Managers.removeManager("HOPA.Entities.MagneticLabyrinth", "MagneticLabyrinthManager")
    Managers.removeManager("HOPA.Entities.Mana", "ManaManager")
    Managers.removeManager("HOPA.Entities.Map2", "Map2Manager")
    Managers.removeManager("HOPA.Entities.Map2.CollectedMap", "CollectedMapManager")
    Managers.removeManager("HOPA.Entities.Map2.CollectedMapIndicator", "CollectedMapIndicatorManager")
    Managers.removeManager("HOPA.Entities.Map2.MapSwitch", "MapSwitchManager")
    Managers.removeManager("HOPA.Entities.MoveBlocks", "MoveBlocksManager")
    Managers.removeManager("HOPA.Entities.Notebook", "NotebookManager")
    Managers.removeManager("HOPA.Entities.NotebookDescription", "NotebookDescriptionManager")
    Managers.removeManager("HOPA.Entities.NotebookInventory", "NotebookInventoryManager")
    Managers.removeManager("HOPA.Entities.NotebookInventoryList", "NotebookInventoryListManager")
    Managers.removeManager("HOPA.Entities.OpenJournal", "OpenJournalManager")
    Managers.removeManager("HOPA.Entities.Options", "OptionsManager")
    Managers.removeManager("HOPA.Entities.OptionsMore", "OptionsMoreManager")
    Managers.removeManager("HOPA.Entities.Plumber", "PlumberManager")
    Managers.removeManager("HOPA.Entities.Profile", "ProfileManager")
    Managers.removeManager("HOPA.Entities.Programmator", "ProgrammatorManager")
    Managers.removeManager("HOPA.Entities.Puzzle", "PuzzleManager")
    Managers.removeManager("HOPA.Entities.Reagents", "ReagentsManager")
    Managers.removeManager("HOPA.Entities.RotateAndReflectElement", "RotateAndReflectElementManager")
    Managers.removeManager("HOPA.Entities.SameElements", "SameElementsManager")
    Managers.removeManager("HOPA.Entities.Spell", "SpellManager")
    Managers.removeManager("HOPA.Entities.SpinCirclesDependsPlugin", "SpinCirclesDependsPluginManager")
    Managers.removeManager("HOPA.Entities.SpinCirclesMastermind", "SpinCirclesMastermindManager")
    Managers.removeManager("HOPA.Entities.SplashScreen", "SplashScreenManager")
    Managers.removeManager("HOPA.Entities.StrategyGuide.StrategyGuideController", "StrategyGuideControllerManager")
    Managers.removeManager("HOPA.Entities.StrategyGuide.StrategyGuideMenu", "StrategyGuideMenuManager")
    Managers.removeManager("HOPA.Entities.StrategyGuide.StrategyGuidePage", "StrategyGuidePageManager")
    Managers.removeManager("HOPA.Entities.StrategyGuide.StrategyGuideZoom", "StrategyGuideZoomManager")
    Managers.removeManager("HOPA.Entities.Mahjong", "MahjongManager")
    pass
