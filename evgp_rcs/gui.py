import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread
from PyQt5.Qt import QSortFilterProxyModel
from PyQt5.QtWidgets import QGridLayout, QGroupBox, QVBoxLayout, QPushButton
from rcsmodel import RCSModel
from race import RaceState
from tcpserver import TCPServer

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.is_server_started = False

        self.table = QtWidgets.QTableView()
        self.table.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.table.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)

        self.model = RCSModel()
        #TODO: load based on server connections
        self.model.active_race.createNewRacer("team1", None, "123.123.123.123")
        self.model.active_race.createNewRacer("team2", None, "456.456.456.456")
        self.model.standby_race.createNewRacer("team3", None, "300.300.300.300")
        ##
        self.table.setModel(self.model)

        layout = QGridLayout() #TODO: better layout
        layout.setColumnStretch(0, 10)
        layout.setColumnStretch(1, 10)


        layout.addWidget(self.table, 0, 0)


        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setSourceModel(self.model)
        self.tableFiltered = QtWidgets.QTableView()
        self.tableFiltered.setModel(self.proxyModel)
        self.tableFiltered.setSizeAdjustPolicy(
            QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableFiltered.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        # self.proxyModel.setFilterKeyColumn(1)
        # self.proxyModel.setFilterFixedString("3")
        layout.addWidget(self.tableFiltered, 0, 1)




        self.horizontalGroupBox = QGroupBox("Grid")
        self.horizontalGroupBox.setLayout(layout)

        verticalBoxLayout = QVBoxLayout()
        start_race_button = QPushButton("START RACE")
        start_race_button.clicked.connect(lambda: self.race_state_change_callback(RaceState.GREEN_GREEN))
        verticalBoxLayout.addWidget(start_race_button)
        move_to_active_race_button = QPushButton("Move to Active Race")
        move_to_active_race_button.clicked.connect(self.move_to_active_race)
        verticalBoxLayout.addWidget(move_to_active_race_button)


        layout.addLayout(verticalBoxLayout, 0, 2)


        start_server_button = QPushButton("Start Server")
        start_server_button.clicked.connect(self.start_server)
        verticalBoxLayout.addWidget(start_server_button)
        stop_server_button = QPushButton("Stop Server")
        stop_server_button.clicked.connect(self.stop_server)
        verticalBoxLayout.addWidget(stop_server_button)


        self.setCentralWidget(self.horizontalGroupBox)

    def race_state_change_callback(self, state):
        self.model.race_state_change(state)

    def move_to_active_race(self):
        index = self.table.selectionModel().selectedRows()[0].row() #TODO: handle no selection
        self.model.move_to_active_race(index)
        self.table.selectionModel().clearSelection()

    def start_server(self):
        #TODO: handle address in use (server just shut down)
        if not self.is_server_started:
            self.is_server_started = True
            port = 8080
            server_backlog = 10
            self.server = TCPServer(port, server_backlog)
            self.server.new_connection.connect(self.model.new_connection_handler)
            self.server.lost_connection.connect(self.model.lost_connection_handler)
            self.server.new_response.connect(self.model.new_response_handler)
            #TODO: server on race state change
            self.server_thread = QThread()
            self.server.moveToThread(self.server_thread)
            self.server_thread.started.connect(self.server.run_server)
            self.server_thread.start()

    def stop_server(self):
        if self.is_server_started:
            self.server.stop() #TODO: make this a signal so it works
            self.is_server_started = False


app=QtWidgets.QApplication(sys.argv)
window=MainWindow()
window.show()
app.exec_()
