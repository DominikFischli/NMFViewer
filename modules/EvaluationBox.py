from PyQt6.QtWidgets import QGroupBox

class EvaluationBox(QGroupBox):
    threshold_box = None
    threshold_layout = None
    thresholds = []
    time_grades = None

    def __init__(self):
        super().__init__()
        self.hide()
        self.setTitle('Evaluation')

        self.threshold_box = QGroupBox(title='H Rows', parent=self)



    def set_thresholds(self, thresholds):
        self.thresholds = thresholds

    def set_time_grades(self, time_grades):
        self.time_grades = time_grades
        self.show()
