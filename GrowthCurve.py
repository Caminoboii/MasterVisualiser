import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


class GrowthCurveVisualiser:
    def __init__(self, filename):
        self.filename = filename
        self.time = []
        self.od600 = []

        self.read_data()

    def read_data(self):
        data = pd.read_csv(self.filename)

        self.time = data["Time [h]"].tolist()
        self.od600 = data["OD600"].tolist()

    @staticmethod
    def create_data_file():
        name = input("Enter a name for the experiment: ")

        time_input = input("What are your time data points? ")
        od_input = input("What are your OD600 data points? ")
        sample_volume_input = input("What are the sample volumes? ")

        time = [float(x.strip()) for x in time_input.split(",")]
        od600 = [float(x.strip()) for x in od_input.split(",")]
        sample_volumes = [float(x.strip()) for x in sample_volume_input.split(",")]

        if not (len(time) == len(od600) == len(sample_volumes)):
            print(
                "Error: Time, OD600, and sample volumes "
                "must have the same number of data points."
            )
            return

        resuspend_volumes = [
            (od * sample_volume) / 8
            for od, sample_volume in zip(od600, sample_volumes)
        ]

        data = pd.DataFrame({
            "Time [h]": time,
            "OD600": od600,
            "Sample Volume": sample_volumes,
            "Resuspend Volume": resuspend_volumes
        })

        folder = Path("Data") / "Growth"
        folder.mkdir(parents=True, exist_ok=True)

        filename = folder / f"{name}.csv"

        data.to_csv(filename, index=False)

        print(f"Data saved to {filename}")

    def plot(self, save_path="Data/Growth/Plots"):
        fig, ax = plt.subplots()

        ax.plot(self.time, self.od600, marker="o")

        ax.set_xlabel("Time [h]")
        ax.set_ylabel("OD600")
        ax.set_title("Growth curve")
        ax.grid(True)

        # Create save folder
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)

        # Create filename based on input CSV
        filename = save_path / f"{Path(self.filename).stem}.png"

        # Save figure
        fig.savefig(filename, dpi=300, bbox_inches="tight")

        print(f"Figure saved to: {filename}")

        plt.show()
        plt.close(fig)