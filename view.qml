import QtQuick 2.11
import QtQuick.Controls 2.15
import QtQuick.Dialogs 1.3
import QtQuick.Layouts 1.3

ApplicationWindow {

	title: qsTr("Storage Application")
	visible: true

	minimumWidth: 1280
	minimumHeight: 720
	visibility: Qt.WindowFullScreen

	header: ToolBar {
		id: myHeader
		visible: false
		spacing: 10

		Grid{
			visible: true
			columns: 2
			spacing: 4
			horizontalItemAlignment: Grid.AlignHCenter
			verticalItemAlignment: Grid.AlignVCenter
		Button{

			text: "View Local Files"

			onClicked: {
				manager.load_local_files()
				update_local_file_view()
				viewLocal.visible = true
				viewRemote.visible = false
			}
		}
		Button{

			text: "View Remote Files"

			onClicked: {
				manager.load_remote_files()
				update_remote_file_view()
				viewLocal.visible = false
				viewRemote.visible = true
			}
		}
		}
	}

	Column{

		id: loginItems
		visible: true
		anchors.centerIn: parent
		spacing: 10

		Grid{
			columns: 2
			spacing: 4
			horizontalItemAlignment: Grid.AlignHCenter
			verticalItemAlignment: Grid.AlignVCenter

			Label {
				text: "Username"
			}
			TextField {
				id: username
				width: 300
				onAccepted: loginBtn.onClicked()

				onFocusChanged: {
					if (focus){
						selectAll()
					}
				}
			}
			Label{
				text: "Password"
			}
			TextField {
				id: password
				width: 300
				echoMode: TextInput.Password
				onAccepted: loginBtn.onClicked()

				onFocusChanged: {
					if (focus){
						selectAll()
					}
				}
			}
		}

		Label {
			id: loginError
			visible: false
			color: 'red'
			text: 'Invalid username or password.'
		}

		Button {
			id: loginBtn
			text: "Login"

			onClicked: {
				if (username.length > 0 && password.length > 0){
					var valid = manager.login(username.text,password.text)
					//console.log(valid)
					if (valid == 1){
						valid_login()
					}
					else{
						password.text = ''
						loginError.visible = true
					}
				}
			}
			Keys.onReturnPressed: this.onClicked()
		}
	}

	Column {

		id: viewLocal
		visible: false
		width: parent.width
		height: parent.height

		Button {
			text: "Previous Directory"
			onClicked: {
				manager.back_up_file_path()
				update_local_file_view()
			}
		}

		ListView {
			id: fileDisplay
			Layout.alignment: Qt.AlignTop
			Layout.fillHeight: true
			Layout.fillWidth: true
			clip: true
			visible: true
			width: parent.width
			height: parent.height

			ScrollBar.vertical: ScrollBar{
				id: fileScroll
				interactive: true
			}

			model: ListModel {
				id: fileView
				ListElement {
					count:0
				}
			}
			delegate: Row {
				Label {
					text: manager.get_file_path(count)
				} Button {
					text: 'Open Directory'
					onClicked: {
						manager.open_file_path(count)
						update_local_file_view()
					}
				} Button {
					text: 'Upload'
					onClicked: {
						manager.upload_file(count)
					}
				}
			}
			spacing: 15

			header: Row {
				Label {
					text: 'Files'
					font.bold: true
				}
			}
		}
	}

	Column {

		id: viewRemote
		visible: false
		width: parent.width
		height: parent.height

		ListView {
			id: remoteFileDisplay
			Layout.alignment: Qt.AlignTop
			Layout.fillHeight: true
			Layout.fillWidth: true
			clip: true
			visible: true
			width: parent.width
			height: parent.height

			ScrollBar.vertical: ScrollBar{
				id: remoteFileScroll
				interactive: true
			}

			model: ListModel {
				id: remoteFileView
				ListElement {
					count:0
				}
			}
			delegate: Row {
				Label {
					text: manager.get_file_path(count)
				} Button {
					text: 'Download'
					onClicked: {
						manager.download_file(count)
					}
				} Button {
					text: 'Delete'
					onClicked: {
						manager.delete_file(count)
						update_remote_file_view()
					}
				}
			}
			spacing: 15

			header: Row {
				Label {
					text: 'Files'
					font.bold: true
				}
			}
		}
	}

	function update_local_file_view() {
		console.log('Load Local Files')
		fileView.clear()
		var count = manager.num_of_files()
		for (var i=0; i<count; i++){
			fileView.append({
				'count':i
			});
		}
	}

	function update_remote_file_view() {
		console.log('Load Remote Files')
		remoteFileView.clear()
		var count = manager.num_of_files()
		for (var i=0; i<count; i++){
			remoteFileView.append({
				'count':i
			});
		}
	}

	function valid_login() {
		console.log('Login Accepted')
		loginItems.visible = false
		myHeader.visible = true
		viewLocal.visible = true
		update_local_file_view()
	}

	function onClose() {
		console.log('Closing Application')
	}
}
