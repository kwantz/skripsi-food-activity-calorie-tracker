import math
from statsmodels.tsa import stattools
from scipy.stats import skew, kurtosis

class Features:
    def convert(self, activity):
        x = activity[1] * activity[1]
        y = activity[2] * activity[2]
        z = activity[3] * activity[3]
        m = x + y + z
        return {
            "timestamp": activity[0],
            "x_axis": activity[1],
            "y_axis": activity[2],
            "z_axis": activity[3],
            "magnitude": math.sqrt(m)
        }

    def jitter(self, axis, start, end):
        j = float(0)
        for i in range(start, min(end, axis.count())):
            if start != 0:
                j += abs(axis[i] - axis[i-1])
        return j / (end - start)

    def mean_crossing_rate(self, axis, start, end):
        cr = 0
        m = axis.mean()
        for i in range(start, min(end, axis.count())):
            if start != 0:
                p = axis[i - 1] > m
                c = axis[i] > m
                if p != c:
                    cr += 1
        return float(cr) / (end - start - 1)

    def hidden_window_summary(self, axis, start, end):
        acf = stattools.acf(axis[start:end])
        acv = stattools.acovf(axis[start:end])
        sqd_error = (axis[start:end] - axis[start:end].mean()) ** 2
        return [
            self.jitter(axis, start, end),
            self.mean_crossing_rate(axis, start, end),
            axis[start:end].mean(),
            axis[start:end].std(),
            axis[start:end].var(),
            axis[start:end].min(),
            axis[start:end].max(),
            acf.mean(),
            acf.std(),
            acv.mean(),
            acv.std(),
            skew(axis[start:end]),
            kurtosis(axis[start:end]),
            math.sqrt(sqd_error.mean())
        ]

    def hidden_windows(self, df, size=450):
        start = 0
        while start < df.count():
            yield start, start + size
            start += (size / 2)

    def extract(self, activity):
        for (start, end) in self.hidden_windows(activity["timestamp"]):
            features = []
            for axis in ["x_axis", "y_axis", "z_axis", "magnitude"]:
                features += self.hidden_window_summary(activity[axis], int(start), int(end))
            yield features
