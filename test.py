from restrictions import SegmentsNormal
from project import CADProject
from figures import Segment
from bindings import choose_best_bindings
from diagnostic_context import measured


@measured
def main():
    project = CADProject()

    segment1 = Segment((0, 0), 0, 10)
    segment1_name = project.add_figure(segment1)
    segment2 = Segment((1, 1), 1, 10)
    segment2_name = project.add_figure(segment2)
    segment3 = Segment((2, 5), -1, 10)
    segment3_name = project.add_figure(segment3)

    bb = choose_best_bindings(project.bindings, 10, 0)[0]  # end of segment 1

    project.add_restriction(SegmentsNormal(), (segment1_name, segment2_name))
    project.add_restriction(SegmentsNormal(), (segment2_name, segment3_name))

    # Move segment 1 end
    project.move_figure(bb, 10 + 1, 0)


if __name__ == '__main__':
    main()
