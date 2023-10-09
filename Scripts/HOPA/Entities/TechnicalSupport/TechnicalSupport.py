from Foundation.Entity.BaseEntity import BaseEntity
from Foundation.TaskManager import TaskManager

MAIL_BUTTON_NAME = "Movie2Button_SendMail"


class TechnicalSupport(BaseEntity):
    def __init__(self):
        super(TechnicalSupport, self).__init__()
        self.button = None
        self._active = False

    def _onPreparation(self):
        if self.object.hasObject(MAIL_BUTTON_NAME) is False:
            Trace.log("Entity", 0, "Demon {} should has object {}".format(self.object.getName(), MAIL_BUTTON_NAME))
            return

        self.button = self.object.getObject(MAIL_BUTTON_NAME)

        is_active = self._prepareEnable()
        self.button.setEnable(is_active)

    def _onActivate(self):
        if self.button is None or self._active is False:
            return
        with TaskManager.createTaskChain(Name="TechnicalSupportButton", Repeat=True) as tc:
            tc.addTask("TaskMovie2ButtonClick", Movie2Button=self.button)
            tc.addFunction(self.sendSupportMail)

    def _onDeactivate(self):
        if TaskManager.existTaskChain("TechnicalSupportButton") is True:
            TaskManager.cancelTaskChain("TechnicalSupportButton")

        self.button = None

    def _prepareEnable(self):
        self._active = Mengine.getGameParamBool("TechnicalSupportEnable", False) is True
        return self._active

    def getSupportMessageBody(self):
        kwargs = dict(
            BUILD_VERSION=_BUILD_VERSION,
            BUILD_NUMBER=_BUILD_VERSION_NUMBER,
            PUBLISHER=Utils.getCurrentPublisher(),
            OS_NAME=Utils.getCurrentPlatform(),
            OS_VERSION="unknown",
            SESSION_ID="unknown",
        )
        if _ANDROID:
            kwargs["OS_VERSION"] = Mengine.androidStringMethod("Application", "getOSVersion")
            kwargs["SESSION_ID"] = Mengine.androidStringMethod("Application", "getSessionId")

        body = u"""----- Please Describe Your Issue Above Here -----

        Important Details for our Support Team:
        * game publisher: {PUBLISHER}
        * build version: {BUILD_VERSION}
        * build number: {BUILD_NUMBER}
        * {OS_NAME} version: {OS_VERSION}
        * session id: {SESSION_ID}
        """.format(**kwargs)

        return body

    def sendSupportMail(self):
        receiver = Mengine.getGameParamUnicode("TechnicalSupportEmail")
        subject = u"[{}] Technical Support Request".format(Mengine.getProjectName())
        body = self.getSupportMessageBody()

        if _DEVELOPMENT is True:
            Trace.msg("DUMMY send support mail:\n  Receiver: {!r}\n  Subject: {!r}"
                      "\n{}\n  (Include player save)".format(receiver, subject, body))

        try:
            Mengine.openMail(receiver, subject, body)
        except Exception as ex:
            Trace.log("Manager", 0, "TechnicalSupport.sendSupportMail: %s" % ex)