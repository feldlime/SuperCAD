"""Module with functions for design"""
from PyQt5.QtWidgets import QWidget, QPushButton, QAction
from PyQt5.QtWidgets import QMainWindow


class InterfaceProcessor:
    def __init__(self, window: QMainWindow):
        # self._window = window
        pass

    @staticmethod
    def trigger_action(action: QAction, show: bool = False):
        """ Show or hide widget.

        Parameters
        ----------
        action: QAction
            Widget to show or hide.
        show: bool, default False
            If True, show widget, if False, hide.
        """
        if show:
            action.show()
        else:
            action.hide()

    @staticmethod
    def trigger_widget(widget: QWidget, show: bool = False):
        """ Show or hide widget.

        Parameters
        ----------
        widget: QWidget
            Widget to show or hide.
        show: bool, default False
            If True, show widget, if False, hide.
        """
        if show:
            widget.show()
        else:
            widget.hide()

    @staticmethod
    def trigger_button(button: QPushButton, check: bool = False):
        """ Show or hide widget.

        Parameters
        ----------
        button: QPushButton
            Button to check or uncheck.
        check: bool, default False
            If True, check button, if False, uncheck.
        """
        button.setChecked(check)


    def save(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError


    # def triggered_point_widget(self, change):
    #     self.hide_all_footer_widgets()
    #     if change:
    #         self.statusbar.showMessage('Point')
    #         self.Point_widget.show()
    #     else:
    #         self.statusbar.showMessage('')
    #         self.Point_widget.hide()
    #
    # def triggered_line_widget(self, change):
    #     self.hide_all_footer_widgets()
    #     if change:
    #         self.statusbar.showMessage('Line')
    #         self.Line_widget.show()
    #     else:
    #         self.statusbar.showMessage('')
    #         self.Line_widget.hide()
    #
    # def triggered_combine_points_widget(self, change):
    #     self.hide_all_footer_widgets()
    #     if change:
    #         self.statusbar.showMessage('Choose first point to combine')
    #         self.Combine_points_widget.show()
    #     else:
    #         self.statusbar.showMessage('')
    #         self.Combine_points_widget.hide()
    #
    # def triggered_point_on_middle_line_widget(self, change):
    #     self.hide_all_footer_widgets()
    #     if change:
    #         self.statusbar.showMessage(
    #             'Choose line to combine with middle of line')
    #         self.Point_on_middle_line_widget.show()
    #     else:
    #         self.statusbar.showMessage('')
    #         self.Point_on_middle_line_widget.hide()
    #
    # def triggered_point_on_line_widget(self, change):
    #     self.hide_all_footer_widgets()
    #     if change:
    #         self.statusbar.showMessage('Choose line to combine with line')
    #         self.Point_on_line_widget.show()
    #     else:
    #         self.statusbar.showMessage('')
    #         self.Point_on_line_widget.hide()
    #
    # def triggered_parallelism_widget(self, change):
    #     self.hide_all_footer_widgets()
    #     if change:
    #         self.statusbar.showMessage('Choose changeable line')
    #         self.Parallelism_widget.show()
    #     else:
    #         self.statusbar.showMessage('')
    #         self.Parallelism_widget.hide()
    #
    # def triggered_normal_widget(self, change):
    #     self.hide_all_footer_widgets()
    #     if change:
    #         self.statusbar.showMessage('Choose changeable line')
    #         self.Normal_widget.show()
    #     else:
    #         self.statusbar.showMessage('')
    #         self.Normal_widget.hide()
    #
    # def triggered_horizontally_widget(self, change):
    #     # self.hide_all_footer_widgets()
    #     if change:
    #         self.statusbar.showMessage('Choose changeable line')
    #         self.Horizontally_widget.show()
    #     else:
    #         self.statusbar.showMessage('')
    #         self.Horizontally_widget.hide()
    #
    # def triggered_fix_size_widget(self, change):
    #     self.hide_all_footer_widgets()
    #     if change:
    #         self.statusbar.showMessage('Choose line for fix size')
    #         self.Fix_size_widget.show()
    #     else:
    #         self.statusbar.showMessage('')
    #         self.Fix_size_widget.hide()
    #
    # def triggered_fix_point_widget(self, change):
    #     self.hide_all_footer_widgets()
    #     if change:
    #         self.statusbar.showMessage('Choose point for fix')
    #         self.Fix_point_widget.show()
    #     else:
    #         self.statusbar.showMessage('')
    #         self.Fix_point_widget.hide()
    #
    # def triggered_fix_length_widget(self, change):
    #     self.hide_all_footer_widgets()
    #     if change:
    #         self.statusbar.showMessage('Choose point for fix length')
    #         self.Fix_length_widget.show()
    #     else:
    #         self.statusbar.showMessage('')
    #         self.Fix_length_widget.hide()
    #
    # def triggered_fix_angle_widget(self, change):
    #     self.hide_all_footer_widgets()
    #     if change:
    #         self.statusbar.showMessage('Choose first line for fix angle')
    #         self.Fix_angle_widget.show()
    #     else:
    #         self.statusbar.showMessage('')
    #         self.Fix_angle_widget.hide()

