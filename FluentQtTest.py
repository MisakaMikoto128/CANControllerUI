# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\FluentQtTest.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1138, 817)
        self.gridLayout_9 = QtWidgets.QGridLayout(Form)
        self.gridLayout_9.setContentsMargins(-1, 9, -1, -1)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.TitleLabel_3 = TitleLabel(Form)
        self.TitleLabel_3.setObjectName("TitleLabel_3")
        self.verticalLayout_2.addWidget(self.TitleLabel_3)
        self.TableWidget_Charger = TableWidget(Form)
        self.TableWidget_Charger.setObjectName("TableWidget_Charger")
        self.TableWidget_Charger.setColumnCount(0)
        self.TableWidget_Charger.setRowCount(0)
        self.verticalLayout_2.addWidget(self.TableWidget_Charger)
        self.gridLayout_9.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.TitleLabel_2 = TitleLabel(Form)
        self.TitleLabel_2.setObjectName("TitleLabel_2")
        self.verticalLayout_3.addWidget(self.TitleLabel_2)
        self.TableWidget_Battery = TableWidget(Form)
        self.TableWidget_Battery.setObjectName("TableWidget_Battery")
        self.TableWidget_Battery.setColumnCount(0)
        self.TableWidget_Battery.setRowCount(0)
        self.verticalLayout_3.addWidget(self.TableWidget_Battery)
        self.gridLayout_9.addLayout(self.verticalLayout_3, 0, 1, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, -1, 0, -1)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.TitleLabel = TitleLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TitleLabel.sizePolicy().hasHeightForWidth())
        self.TitleLabel.setSizePolicy(sizePolicy)
        self.TitleLabel.setObjectName("TitleLabel")
        self.verticalLayout.addWidget(self.TitleLabel)
        self.BodyLabel_2 = BodyLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BodyLabel_2.sizePolicy().hasHeightForWidth())
        self.BodyLabel_2.setSizePolicy(sizePolicy)
        self.BodyLabel_2.setObjectName("BodyLabel_2")
        self.verticalLayout.addWidget(self.BodyLabel_2)
        self.ToggleButtonCAN = ToggleButton(Form)
        self.ToggleButtonCAN.setObjectName("ToggleButtonCAN")
        self.verticalLayout.addWidget(self.ToggleButtonCAN)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.BodyLabel_5 = BodyLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BodyLabel_5.sizePolicy().hasHeightForWidth())
        self.BodyLabel_5.setSizePolicy(sizePolicy)
        self.BodyLabel_5.setObjectName("BodyLabel_5")
        self.horizontalLayout_2.addWidget(self.BodyLabel_5)
        self.IconInfoBadge_CAN1 = IconInfoBadge(Form)
        self.IconInfoBadge_CAN1.setObjectName("IconInfoBadge_CAN1")
        self.horizontalLayout_2.addWidget(self.IconInfoBadge_CAN1)
        self.BodyLabel_6 = BodyLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BodyLabel_6.sizePolicy().hasHeightForWidth())
        self.BodyLabel_6.setSizePolicy(sizePolicy)
        self.BodyLabel_6.setObjectName("BodyLabel_6")
        self.horizontalLayout_2.addWidget(self.BodyLabel_6)
        self.IconInfoBadge_CAN2 = IconInfoBadge(Form)
        self.IconInfoBadge_CAN2.setObjectName("IconInfoBadge_CAN2")
        self.horizontalLayout_2.addWidget(self.IconInfoBadge_CAN2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.HorizontalSeparator = HorizontalSeparator(Form)
        self.HorizontalSeparator.setObjectName("HorizontalSeparator")
        self.verticalLayout.addWidget(self.HorizontalSeparator)
        self.StrongBodyLabel = StrongBodyLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.StrongBodyLabel.sizePolicy().hasHeightForWidth())
        self.StrongBodyLabel.setSizePolicy(sizePolicy)
        self.StrongBodyLabel.setObjectName("StrongBodyLabel")
        self.verticalLayout.addWidget(self.StrongBodyLabel)
        self.PushButton_OpenDCOutput = PushButton(Form)
        self.PushButton_OpenDCOutput.setObjectName("PushButton_OpenDCOutput")
        self.verticalLayout.addWidget(self.PushButton_OpenDCOutput)
        self.PushButton_CloseDCOutput = PushButton(Form)
        self.PushButton_CloseDCOutput.setObjectName("PushButton_CloseDCOutput")
        self.verticalLayout.addWidget(self.PushButton_CloseDCOutput)
        self.SwitchButton_Charger = SwitchButton(Form)
        self.SwitchButton_Charger.setObjectName("SwitchButton_Charger")
        self.verticalLayout.addWidget(self.SwitchButton_Charger)
        self.PushButton_SetVoltCurr = PushButton(Form)
        self.PushButton_SetVoltCurr.setObjectName("PushButton_SetVoltCurr")
        self.verticalLayout.addWidget(self.PushButton_SetVoltCurr)
        self.StrongBodyLabel_2 = StrongBodyLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.StrongBodyLabel_2.sizePolicy().hasHeightForWidth())
        self.StrongBodyLabel_2.setSizePolicy(sizePolicy)
        self.StrongBodyLabel_2.setAlignment(QtCore.Qt.AlignCenter)
        self.StrongBodyLabel_2.setObjectName("StrongBodyLabel_2")
        self.verticalLayout.addWidget(self.StrongBodyLabel_2)
        self.DoubleSpinBox_Curr = DoubleSpinBox(Form)
        self.DoubleSpinBox_Curr.setMaximum(100.0)
        self.DoubleSpinBox_Curr.setObjectName("DoubleSpinBox_Curr")
        self.verticalLayout.addWidget(self.DoubleSpinBox_Curr)
        self.StrongBodyLabel_3 = StrongBodyLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.StrongBodyLabel_3.sizePolicy().hasHeightForWidth())
        self.StrongBodyLabel_3.setSizePolicy(sizePolicy)
        self.StrongBodyLabel_3.setAlignment(QtCore.Qt.AlignCenter)
        self.StrongBodyLabel_3.setObjectName("StrongBodyLabel_3")
        self.verticalLayout.addWidget(self.StrongBodyLabel_3)
        self.DoubleSpinBox_Volt = DoubleSpinBox(Form)
        self.DoubleSpinBox_Volt.setMinimum(100.0)
        self.DoubleSpinBox_Volt.setMaximum(1000.0)
        self.DoubleSpinBox_Volt.setObjectName("DoubleSpinBox_Volt")
        self.verticalLayout.addWidget(self.DoubleSpinBox_Volt)
        self.HorizontalSeparator_2 = HorizontalSeparator(Form)
        self.HorizontalSeparator_2.setObjectName("HorizontalSeparator_2")
        self.verticalLayout.addWidget(self.HorizontalSeparator_2)
        self.BodyLabel = BodyLabel(Form)
        self.BodyLabel.setTextFormat(QtCore.Qt.AutoText)
        self.BodyLabel.setWordWrap(False)
        self.BodyLabel.setObjectName("BodyLabel")
        self.verticalLayout.addWidget(self.BodyLabel)
        self.PushButton_stage1 = PushButton(Form)
        self.PushButton_stage1.setObjectName("PushButton_stage1")
        self.verticalLayout.addWidget(self.PushButton_stage1)
        self.PushButton_stage2 = PushButton(Form)
        self.PushButton_stage2.setObjectName("PushButton_stage2")
        self.verticalLayout.addWidget(self.PushButton_stage2)
        self.PushButton_stage3 = PushButton(Form)
        self.PushButton_stage3.setObjectName("PushButton_stage3")
        self.verticalLayout.addWidget(self.PushButton_stage3)
        self.PushButton_stage4 = PushButton(Form)
        self.PushButton_stage4.setObjectName("PushButton_stage4")
        self.verticalLayout.addWidget(self.PushButton_stage4)
        self.HorizontalSeparator_3 = HorizontalSeparator(Form)
        self.HorizontalSeparator_3.setObjectName("HorizontalSeparator_3")
        self.verticalLayout.addWidget(self.HorizontalSeparator_3)
        self.BodyLabel_3 = BodyLabel(Form)
        self.BodyLabel_3.setObjectName("BodyLabel_3")
        self.verticalLayout.addWidget(self.BodyLabel_3)
        self.SwitchButton = SwitchButton(Form)
        self.SwitchButton.setObjectName("SwitchButton")
        self.verticalLayout.addWidget(self.SwitchButton)
        self.BodyLabel_4 = BodyLabel(Form)
        self.BodyLabel_4.setObjectName("BodyLabel_4")
        self.verticalLayout.addWidget(self.BodyLabel_4)
        self.SwitchButton_2 = SwitchButton(Form)
        self.SwitchButton_2.setObjectName("SwitchButton_2")
        self.verticalLayout.addWidget(self.SwitchButton_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout_9.addLayout(self.verticalLayout, 0, 2, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.TitleLabel_3.setText(_translate("Form", "充电器状态"))
        self.TitleLabel_2.setText(_translate("Form", "电池状态"))
        self.TitleLabel.setText(_translate("Form", "充电器控制"))
        self.BodyLabel_2.setText(_translate("Form", "CAN收发器控制"))
        self.ToggleButtonCAN.setText(_translate("Form", "打开CAN"))
        self.BodyLabel_5.setText(_translate("Form", "CAN1"))
        self.BodyLabel_6.setText(_translate("Form", "CAN1"))
        self.StrongBodyLabel.setText(_translate("Form", "充电器启动控制"))
        self.PushButton_OpenDCOutput.setText(_translate("Form", "启动充电输出"))
        self.PushButton_CloseDCOutput.setText(_translate("Form", "关闭充电输出"))
        self.SwitchButton_Charger.setOnText(_translate("Form", "充电器已启动"))
        self.SwitchButton_Charger.setOffText(_translate("Form", "充电器已关闭"))
        self.PushButton_SetVoltCurr.setText(_translate("Form", "设置输出电压电流"))
        self.StrongBodyLabel_2.setText(_translate("Form", "输出电流"))
        self.StrongBodyLabel_3.setText(_translate("Form", "输出电压"))
        self.BodyLabel.setText(_translate("Form", "高压控制"))
        self.PushButton_stage1.setText(_translate("Form", "闭合预充"))
        self.PushButton_stage2.setText(_translate("Form", "闭合预充和主正"))
        self.PushButton_stage3.setText(_translate("Form", "断开预充，保持主正闭合"))
        self.PushButton_stage4.setText(_translate("Form", "断开主正"))
        self.BodyLabel_3.setText(_translate("Form", "预充继电器状态"))
        self.SwitchButton.setOnText(_translate("Form", "闭合"))
        self.SwitchButton.setOffText(_translate("Form", "开路"))
        self.BodyLabel_4.setText(_translate("Form", "主正继电器状态"))
        self.SwitchButton_2.setOnText(_translate("Form", "闭合"))
        self.SwitchButton_2.setOffText(_translate("Form", "开路"))
from qfluentwidgets import BodyLabel, DoubleSpinBox, HorizontalSeparator, IconInfoBadge, PushButton, StrongBodyLabel, SwitchButton, TableWidget, TitleLabel, ToggleButton
