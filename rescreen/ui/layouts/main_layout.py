# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_windowvJeRPv.ui'
##
## Created by: Qt User Interface Compiler version 5.15.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from rescreen.ui.preview import Preview


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(763, 759)
        icon = QIcon()
        icon.addFile(u"icon_rounded.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setAutoFillBackground(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.preview = Preview(self.centralwidget)
        self.preview.setObjectName(u"preview")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.preview.sizePolicy().hasHeightForWidth())
        self.preview.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.preview)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.display_selection_dropdown = QComboBox(self.centralwidget)
        self.display_selection_dropdown.setObjectName(u"display_selection_dropdown")

        self.gridLayout.addWidget(self.display_selection_dropdown, 0, 3, 1, 1)

        self.enabled_checkbox = QCheckBox(self.centralwidget)
        self.enabled_checkbox.setObjectName(u"enabled_checkbox")

        self.gridLayout.addWidget(self.enabled_checkbox, 0, 0, 1, 1)

        self.primary_display_radio = QRadioButton(self.centralwidget)
        self.primary_display_radio.setObjectName(u"primary_display_radio")

        self.gridLayout.addWidget(self.primary_display_radio, 0, 1, 1, 1)

        self.verticalLayout.addLayout(self.gridLayout)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.refresh_rate_label = QLabel(self.frame)
        self.refresh_rate_label.setObjectName(u"refresh_rate_label")

        self.gridLayout_2.addWidget(self.refresh_rate_label, 2, 0, 1, 1)

        self.refresh_rate_dropdown = QComboBox(self.frame)
        self.refresh_rate_dropdown.setObjectName(u"refresh_rate_dropdown")

        self.gridLayout_2.addWidget(self.refresh_rate_dropdown, 2, 1, 1, 1)

        self.resolution_dropdown = QComboBox(self.frame)
        self.resolution_dropdown.setObjectName(u"resolution_dropdown")

        self.gridLayout_2.addWidget(self.resolution_dropdown, 1, 1, 1, 1)

        self.ui_scale_dropdown = QComboBox(self.frame)
        self.ui_scale_dropdown.setObjectName(u"ui_scale_dropdown")

        self.gridLayout_2.addWidget(self.ui_scale_dropdown, 3, 1, 1, 1)

        self.resolution_scale_label = QLabel(self.frame)
        self.resolution_scale_label.setObjectName(u"resolution_scale_label")

        self.gridLayout_2.addWidget(self.resolution_scale_label, 4, 0, 1, 1)

        self.orientation_label = QLabel(self.frame)
        self.orientation_label.setObjectName(u"orientation_label")

        self.gridLayout_2.addWidget(self.orientation_label, 0, 0, 1, 1)

        self.ui_scale_label = QLabel(self.frame)
        self.ui_scale_label.setObjectName(u"ui_scale_label")

        self.gridLayout_2.addWidget(self.ui_scale_label, 3, 0, 1, 1)

        self.resolution_scale_dropdown = QComboBox(self.frame)
        self.resolution_scale_dropdown.setObjectName(u"resolution_scale_dropdown")

        self.gridLayout_2.addWidget(self.resolution_scale_dropdown, 4, 1, 1, 1)

        self.resolution_label = QLabel(self.frame)
        self.resolution_label.setObjectName(u"resolution_label")

        self.gridLayout_2.addWidget(self.resolution_label, 1, 0, 1, 1)

        self.orientation_dropdown = QComboBox(self.frame)
        self.orientation_dropdown.setObjectName(u"orientation_dropdown")

        self.gridLayout_2.addWidget(self.orientation_dropdown, 0, 1, 1, 1)

        self.verticalLayout_3.addLayout(self.gridLayout_2)

        self.verticalLayout.addWidget(self.frame)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.refresh_button = QPushButton(self.centralwidget)
        self.refresh_button.setObjectName(u"refresh_button")

        self.horizontalLayout_2.addWidget(self.refresh_button)

        self.apply_button = QPushButton(self.centralwidget)
        self.apply_button.setObjectName(u"apply_button")

        self.horizontalLayout_2.addWidget(self.apply_button)

        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.verticalLayout.addLayout(self.verticalLayout_4)

        self.horizontalLayout.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 763, 28))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"ReScreen", None))
        self.enabled_checkbox.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.primary_display_radio.setText(QCoreApplication.translate("MainWindow", u"Primary Display", None))
        self.refresh_rate_label.setText(QCoreApplication.translate("MainWindow", u"Refresh Rate", None))
        self.resolution_scale_label.setText(QCoreApplication.translate("MainWindow", u"Resolution Scale", None))
        self.orientation_label.setText(QCoreApplication.translate("MainWindow", u"Orientation", None))
        self.ui_scale_label.setText(QCoreApplication.translate("MainWindow", u"UI Scale", None))
        self.resolution_label.setText(QCoreApplication.translate("MainWindow", u"Resolution", None))
        self.refresh_button.setText(QCoreApplication.translate("MainWindow", u"Refresh", None))
        self.apply_button.setText(QCoreApplication.translate("MainWindow", u"Apply", None))
    # retranslateUi
