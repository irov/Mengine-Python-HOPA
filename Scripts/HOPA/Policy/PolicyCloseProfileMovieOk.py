from Foundation.Task.TaskAlias import TaskAlias


class PolicyCloseProfileMovieOk(TaskAlias):

    def _onGenerate(self, source):
        with source.addRaceTask(2) as (tc_button, tc_socket):
            tc_button.addTask("TaskMovie2ButtonClick", DemonName="Profile",
                              Movie2ButtonName="Movie2Button_Profile_Ok")
            tc_socket.addTask("TaskMovie2SocketClick", GroupName="Profile",
                              Movie2Name="Movie2_Background", SocketName="close")
