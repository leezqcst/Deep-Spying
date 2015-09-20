__author__ = 'Tony Beltramelli www.tonybeltramelli.com - 14/09/2015'

from PeakAnalysis import *
from ..utils.UMath import *
from ..Path import Path


class FeatureExtractor:
    def __init__(self, output_path, view):
        self.output_path = output_path
        self.view = view

    def segment_heuristically(self, signal):
        p = PeakAnalysis()
        p.segment(signal, True)

    def segment_from_labels(self, sensors, label, separator=","):
        label_timestamps = label.timestamp
        labels = label.label

        output_file = open("{}labelled.data".format(self.output_path), 'w')

        for i in range(0, len(label_timestamps)):
            features = self.get_features(sensors, label_timestamps[i])

            output_file.write("label:{}\n".format(labels[i]))

            for j in range(0, len(features[0])):
                length = len(features)
                line = ""

                for k in range(0, length):
                    value = '{0:.16f}'.format(features[k][j])
                    line += "{}{}".format(value, separator if k < length - 1 else '\n')

                output_file.write(line)

            output_file.write("\n")
        output_file.close()

        print "Save features in {}".format(output_file.name)

        for sensor in sensors:
            self.plot_segmentation(sensor, label_timestamps, labels)

    def plot_segmentation(self, sensor, label_timestamps, labels):
        title = "{} segmentation".format(sensor.name)
        self.view.plot_sensor_data_and_label(title.title(), sensor.timestamp, sensor.x, sensor.y, sensor.z, label_timestamps, labels)

        self.view.save("{}{}_{}.png".format(Path.FIGURE_PATH, sensor.id, title.replace(" ", "_")))

        self.view.show()

    def get_features(self, sensors, timestamp_reference):
        sensor = sensors[0]
        center_timestamp_index = (np.abs(sensor.timestamp - timestamp_reference)).argmin()

        features = []

        for i in range(0, len(sensors)):
            sensor = sensors[i]
            sensor.normalize()

            if sensor.mean_signal is None:
                x_sample = self.get_data_slice(sensor.x, center_timestamp_index)
                y_sample = self.get_data_slice(sensor.y, center_timestamp_index)
                z_sample = self.get_data_slice(sensor.z, center_timestamp_index)

                features.append(x_sample)
                features.append(y_sample)
                features.append(z_sample)
            else:
                mean_sample = self.get_data_slice(sensor.mean_signal, center_timestamp_index)
                features.append(mean_sample)

        return features

    def get_data_slice(self, data, center_index, window_size=100):
        left_samples = data[center_index - (window_size / 2):center_index]
        right_samples = data[center_index:center_index + (window_size / 2)]

        return np.hstack((left_samples, right_samples))