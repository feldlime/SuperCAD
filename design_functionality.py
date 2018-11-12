"""Module with functions for design"""
import design_setup


class Functionality(design_setup.UiAddDesign):
    def __init__(self, window):
        super().setupUi(window)

    def triggered_list_view(self, change):
        if change:
            self.listView.show()
        else:
            self.listView.hide()

    def triggered_widget(self, name, change):
        dict_of = {'Point_widget': self.Point_widget,
                   'Line_widget':
                       self.Line_widget,
                   'Combine_points_widget':
                       self.Combine_points_widget,
                   'Points_on_middle_line_widget':
                       self.Point_on_middle_line_widget,
                   'Point_on_line_widget':
                       self.Point_on_line_widget,
                   'Parallelism_widget':
                       self.Parallelism_widget,
                   'Normal_widget':
                       self.Normal_widget,
                   'Horizontally_widget':
                       self.Horizontally_widget,
                   'Fix_size_widget':
                       self.Fix_size_widget,
                   'Fix_point_widget':
                       self.Fix_point_widget,
                   'Fix_length_widget':
                       self.Fix_length_widget,
                   'Fix_angle_widget':
                       self.Fix_angle_widget
                   }
        event = dict_of.get(name)
        self.hide_all_footer_widgets()
        if change:
            event.show()
        else:
            event.hide()

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

    def hide_all_footer_widgets(self):
        self.Line_widget.hide()
        self.Point_widget.hide()
        self.Combine_points_widget.hide()
        self.Point_on_middle_line_widget.hide()
        self.Point_on_line_widget.hide()
        self.Parallelism_widget.hide()
        self.Normal_widget.hide()
        self.Horizontally_widget.hide()
        self.Fix_size_widget.hide()
        self.Fix_point_widget.hide()
        self.Fix_length_widget.hide()
        self.Fix_angle_widget.hide()

        self.point.setChecked(False)
        self.line.setChecked(False)
        self.combine_points.setChecked(False)
        self.point_on_middle_line.setChecked(False)
        self.point_on_line.setChecked(False)
        self.parallelism.setChecked(False)
        self.normal.setChecked(False)
        self.horizontally.setChecked(False)
        self.fix_size.setChecked(False)
        self.fix_point.setChecked(False)
        self.fix_length.setChecked(False)
        self.fix_angle.setChecked(False)

    def save(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError
